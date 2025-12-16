# Copyright 2025 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

from boulderopalscaleupsdk.utils.serial_utils import sanitize_keys


class ProcessorArchitecture(str, Enum):
    Superconducting = "superconducting"


class DeviceDescriptor(BaseModel):
    qpu_model: str
    controller_info: dict[str, Any]
    device_parameters: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return sanitize_keys(self.model_dump(by_alias=True, mode="json"))


class DeviceConfigLoader:
    def __init__(self, config_path: Path):
        self.config_path = config_path

    def load(self) -> dict[str, Any]:
        device_config_data = self._load_yaml_file(self.config_path)
        processed_device_config = {**device_config_data}
        return sanitize_keys(processed_device_config)

    def load_device_info(self) -> DeviceDescriptor:
        device_config_dict = self.load()
        match device_config_dict["device_arch"]:
            case "superconducting" | "spin":
                device_descriptor = DeviceDescriptor(
                    qpu_model=device_config_dict["qpu_model"],
                    controller_info=device_config_dict["controller_info"],
                    device_parameters=device_config_dict["device_parameters"],
                )
            case other:
                raise ValueError(f"Invalid or unsupported architecture {other}.")
        return device_descriptor

    @staticmethod
    def _load_yaml_file(yaml_file_path: Path) -> dict[str, Any]:
        with yaml_file_path.open("rb") as fd:
            return yaml.safe_load(fd)

    @staticmethod
    def _validate_file_is_filename(file_name: str) -> None:
        if "/" in file_name or "\\" in file_name:
            raise ValueError(
                f"'{file_name}' must be a file name, not a path.",
            )
