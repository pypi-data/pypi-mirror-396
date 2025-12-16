import json
from typing import Any

import DIRAC
from ruamel.yaml import YAML

from CTADIRAC.Core.Utilities.tool_box import DATA_LEVEL_METADATA_ID
from CTADIRAC.Interfaces.API.CTAJob import CTAJob


class SimPipeJob(CTAJob):
    """Generic MCPipe Job class"""

    def __init__(self, we_type: str = "simpipe") -> None:
        super().__init__(we_type=we_type)
        self.setName("MC_Generation")
        self.setType("MCSimulation")
        self.package = "simpipe"
        self.compiler = "gcc114_default"
        self.program_category = "tel_sim"
        self.prog_name = "simpipe"
        self.container = True
        self.run_number_offset = 0
        self.run_number = "@{JOB_ID}"
        self.data_level: int = DATA_LEVEL_METADATA_ID["R1"]
        self.base_path = "/ctao/MC/PROD6/"
        self.sct = False
        self.only_corsika = False
        self.array_layout = ""
        self.zenith_angle = 20.0
        self._azimuth_angle = None
        self.software_category = "simulations"
        self.particle = None
        self.view_cone = None
        self.output_directory = None
        self.simpipe_config_options = None
        self.save_reduced_event_lists = False
        self.output_reduced_event_lists_type = "reduced_event_lists"

    def set_simpipe_config(self, value) -> None:
        config = self._load_config_file(value)
        self._apply_config(config)

    def _load_config_file(self, config_file: str) -> dict:
        yaml = YAML(typ="safe")
        with open(config_file) as file:
            return yaml.load(file)

    def _apply_config(self, config: dict) -> None:
        """Apply configuration settings to the class attributes."""

        # Define a generic handler for setting attributes
        def set_attribute(attr_name, value):
            setattr(self, attr_name, value)

        # Define a mapping of keys to handler methods or attributes
        handlers = {
            "array_layout_name": self._set_array_layout,
            "site": self._set_site,
            "model_version": lambda value: setattr(
                self, "model_version", value if isinstance(value, list) else [value]
            ),
            "simulation_software": self._set_simulation_software,
            "pack_for_grid_register": lambda value: setattr(
                self, "output_directory", value
            ),
            "primary": lambda value: setattr(self, "particle", value.lower()),
            "save_reduced_event_lists": lambda value: setattr(
                self, "save_reduced_event_lists", bool(value)
            ),
            "view_cone": lambda value: setattr(
                self, "view_cone", str(value).replace(" ", "_")
            ),
        }

        # Add generic handlers for attributes that map directly
        direct_mappings = ["zenith_angle", "azimuth_angle"]
        for key in direct_mappings:
            handlers[key] = lambda value, attr=key: set_attribute(attr, value)

        # Get the configuration in a dict to serialize it for the simpipe wrapper
        self.simpipe_config_options = {}
        for key, value in config.items():
            key_lower = key.lower()
            if key_lower in handlers:
                handlers[key_lower](value)
            elif key_lower in {"run_number_offset", "run_number"}:
                DIRAC.gLogger.error(
                    f"The {key_lower} must be set in the DIRAC config file, "
                    "not the SimPipe config file."
                )
                DIRAC.exit(-1)

            # Store the configuration in simpipe_config_options
            self.simpipe_config_options[key_lower] = value

    def _set_array_layout(self, value: str) -> None:
        """Set the array layout and SCT flag."""
        self.array_layout = value
        if "_scts" in value:
            self.sct = True
            # TODO: choose also the right container for this case

    def _set_site(self, value: str) -> None:
        """Set the site based on the configuration."""
        if value == "North":
            self.site = "LaPalma"
        elif value == "South":
            self.site = "Paranal"
        else:
            DIRAC.gLogger.error(f"Unknown site: {value}")
            DIRAC.exit(-1)

    @property
    def azimuth_angle(self) -> float:
        """Get the azimuth angle."""
        if self._azimuth_angle is None:
            DIRAC.gLogger.error(
                "Azimuth angle is not set. "
                "Please set it using the azimuth_angle property."
            )
            DIRAC.exit(-1)
        return self._azimuth_angle

    @azimuth_angle.setter
    def azimuth_angle(self, value: float) -> None:
        try:
            value = float(value)
            self._azimuth_angle = value
        except ValueError:
            azimuth_map = {
                "north": 0,
                "south": 180,
                "east": 90,
                "west": 270,
            }
            azimuth_angle = value.lower()
            if azimuth_angle in azimuth_map:
                self._azimuth_angle = azimuth_map[azimuth_angle]
            else:
                DIRAC.gLogger.error(
                    f"Unknown azimuth angle: {value}. "
                    f"Options are: {list(azimuth_map.keys())}"
                )
                DIRAC.exit(-1)

    def _set_simulation_software(self, value: str) -> None:
        """Set simulation software-specific attributes."""
        if value == "corsika":
            self.only_corsika = True
            self.program_category = "airshower_sim"
            self.prog_name = "corsika"

    def build_file_metadata(
        self, combination, propagate_run_number=True
    ) -> tuple[dict[str, str], Any, str, str]:
        file_meta_data: dict[str, str] = {}
        if propagate_run_number:
            file_meta_data["runNumber"] = self.run_number
            if self.run_number != "@{JOB_ID}":
                file_meta_data["runNumber"] += self.run_number_offset

        for key, value in combination.items():
            file_meta_data[key] = value

        return file_meta_data

    def run_simpipe(self, debug=False) -> None:
        """
        Run CORSIKA/sim_telarray simulation step
        """
        simpipe_config_json = json.dumps(self.simpipe_config_options)
        prod_exe = "dirac_simpipe_simulate_prod_wrapper"
        prod_args = (
            f"{self.run_number_offset} {self.run_number} '{simpipe_config_json}'"
        )

        step = self.setExecutable(
            prod_exe,
            arguments=prod_args,
            logFile="SimPipe_Log.txt",
            modulesList=["cta_script"],
        )
        step["Value"]["name"] = "Step_SimPipe"
        step["Value"]["descr_short"] = "Run SimPipe simulation step"

    def init_debug_step(self) -> None:
        super().init_debug_step()
        step = self.setExecutable("/bin/env", logFile="Env_Log.txt")
        step["Value"]["name"] = "Step_Env"
        step["Value"]["descr_short"] = "Dump environment"

    def upload_and_register_file(
        self,
        meta_data_json,
        file_meta_data_json,
        file_pattern,
        log_str,
        data_type: str = "data",
    ) -> None:
        """
        Upload and register files to SE and register them in DFC.

        Args:
            meta_data_json: JSON string containing metadata
            file_meta_data_json: JSON string containing file metadata
            file_pattern: Pattern for files to upload
            log_str: String identifier for logging
            data_type: Type of data ('data', 'log', 'reduced_event_lists')
        """
        # Define configuration for different data types
        type_config = {
            "data": {
                "output_type_attr": "output_data_type",
                "management_type": "DataManagement",
                "step_name": "Step_DataManagement",
                "description": "Save data files to SE and register them in DFC",
            },
            "log": {
                "output_type_attr": "output_log_type",
                "management_type": "LogManagement",
                "step_name": "Step_LogManagement",
                "description": "Save log files to SE and register them in DFC",
            },
            "reduced_event_lists": {
                "output_type_attr": "output_reduced_event_lists_type",
                "management_type": "ReducedEventListsManagement",
                "step_name": "Step_ReducedEventListsManagement",
                "description": (
                    "Save reduced event lists to SE and register them in DFC"
                ),
            },
        }

        if data_type not in type_config:
            raise ValueError(
                f"Unknown data type: {data_type}. "
                f"Supported types: {list(type_config.keys())}"
            )

        config = type_config[data_type]
        output_data_type = getattr(self, config["output_type_attr"])
        management_type = config["management_type"]
        step_name = config["step_name"]
        description = config["description"]

        step = self.setExecutable(
            "cta-prod-managedata",
            arguments=(
                f"'{meta_data_json}' '{file_meta_data_json}' {self.base_path} "
                f"'{file_pattern}' {self.package} {self.program_category} "
                f"'{self.catalogs}' {output_data_type}"
            ),
            logFile=f"{management_type}_{log_str}_Log.txt",
        )

        step["Value"]["name"] = step_name
        step["Value"]["descr_short"] = description

    def set_metadata_and_register_data(self, propagate_run_number=True) -> None:
        meta_data_json: str = json.dumps(self.output_metadata)

        # Iterate over each model_version entry
        for model_version in self.model_version:
            combination = {"model_version": model_version}

            # Build file metadata for the current model_version
            file_meta_data = self.build_file_metadata(combination, propagate_run_number)
            file_meta_data_json = json.dumps(file_meta_data)

            data_output_pattern = f"{self.output_directory}/*_{model_version}_*.zst"
            if self.only_corsika:
                data_output_pattern = (
                    f"{self.output_directory}/*_{model_version}_*.corsika.zst"
                )
            log_str = f"{model_version}"

            # Upload and register data files for the current model_version
            self.upload_and_register_file(
                meta_data_json,
                file_meta_data_json,
                data_output_pattern,
                log_str,
                data_type="data",
            )

            # Upload reduced event lists files if available
            if self.save_reduced_event_lists:
                reduced_data_output_pattern = (
                    f"{self.output_directory}/*_{model_version}_*"
                    ".reduced_event_data.hdf5"
                )

                # Upload and register reduced event lists files
                self.upload_and_register_file(
                    meta_data_json,
                    file_meta_data_json,
                    reduced_data_output_pattern,
                    f"{log_str}_reduced_event_lists",
                    data_type="reduced_event_lists",
                )

            # Use model_version in log file patterns
            log_file_pattern = (
                f"{self.output_directory}/*_{model_version}_*.log_hist.tar.gz"
            )
            if self.only_corsika:
                log_file_pattern = (
                    f"{self.output_directory}/*_{model_version}_*.corsika.log.gz"
                )

            # Upload and register log files for the current model_version
            self.upload_and_register_file(
                meta_data_json,
                file_meta_data_json,
                log_file_pattern,
                log_str,
                data_type="log",
            )

    def run_dedicated_software(self) -> None:
        self.run_simpipe()

    def set_executable_sequence(
        self, debug: bool = False, define_n_showers=True
    ) -> None:
        super().set_executable_sequence(debug=debug)
