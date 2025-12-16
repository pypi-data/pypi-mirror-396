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

from typing import Annotated

from pydantic import PrivateAttr

from boulderopalscaleupsdk.experiments import ConstantWaveform

from .common import Routine, TransmonsValidator


class TransmonDiscovery(Routine):
    """
    Parameters for running a transmon discovery routine.

    Attributes
    ----------
    transmon : str or list[str] or None, optional
        The references for the transmons to target.
        If not provided, the routine will target all the transmons in the device.
    spectroscopy_waveform : ConstantWaveform or list[ConstantWaveform] or None, optional
        The drive pulse used during transmon spectroscopy and transmon anharmonicity.
        If a single pulse is provided, it will be used for all transmons.
        If a list is provided, it must have the same length as transmons.
        If no pulse is provided, a default constant waveform with an amplitude
            of 0.01 and a duration of 40,000 ns will be used for all transmons.
    force_rerun : bool, optional
        Whether to rerun the entire routine regardless transmon's current calibration status.
        Defaults to False.
    """

    _routine_name: str = PrivateAttr("transmon_discovery")

    transmon: Annotated[list[str] | None, TransmonsValidator] = None
    spectroscopy_waveform: list[ConstantWaveform] | ConstantWaveform | None = None
    force_rerun: bool = False
