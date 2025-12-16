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

from pydantic import PrivateAttr

from .common import Experiment, LinspaceIterable
from .waveforms import Waveform


class CZLeakageCalibration(Experiment):
    """
    Parameters for running a CZ leakage calibration experiment.

    Attributes
    ----------
    control_transmon : str
        The control transmon to target in the experiment.
    target_transmon : str
        The target transmon to pair with the control transmon.
    qubit_amplitude_scale : LinspaceIterable
        The qubit pulse amplitude scale values to sweep over.
    coupler_amplitude_scale : LinspaceIterable
        The coupler pulse amplitude scale values to sweep over.
    drive_waveform : Waveform
        The waveform to use for the CZ pulse.
    prep_padding_ns : int, optional
        The padding to apply before the CZ pulse, in nanoseconds.
        Defaults to 16 ns.
    measurement_padding_ns : int, optional
        The padding to apply after the CZ pulse, in nanoseconds.
        Defaults to 16 ns.
    recycle_delay_ns : float, optional
        The delay time between consecutive shots of the experiment, in nanoseconds.
        Defaults to 500,000 ns.
    shot_count : int, optional
        The number of shots to take. Defaults to 200.
    batch_analysis : bool, optional
        Whether to perform batch analysis on the results. Defaults to False.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("cz_leakage_calibration")

    control_transmon: str
    target_transmon: str
    qubit_amplitude_scale: LinspaceIterable
    coupler_amplitude_scale: LinspaceIterable
    drive_waveform: Waveform
    prep_padding_ns: int = 16
    measurement_padding_ns: int = 16
    recycle_delay_ns: int = 500_000
    shot_count: int = 200
    batch_analysis: bool = False
    update: Literal["auto", "off", "prompt"] = "auto"
