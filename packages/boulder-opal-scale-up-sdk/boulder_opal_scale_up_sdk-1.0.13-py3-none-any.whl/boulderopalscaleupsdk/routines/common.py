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

from typing import Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict

ROUTINE_REGISTRY: dict[str, Literal["Routine"]] = {}


class Routine(BaseModel):
    model_config = ConfigDict(extra="forbid")
    _routine_name: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        name = str(cls.__private_attributes__["_routine_name"].default)
        ROUTINE_REGISTRY[name] = "Routine"

    @property
    def routine_name(self) -> str:
        return self._routine_name


TransmonsValidator = BeforeValidator(lambda x: [x] if isinstance(x, str) else x)
