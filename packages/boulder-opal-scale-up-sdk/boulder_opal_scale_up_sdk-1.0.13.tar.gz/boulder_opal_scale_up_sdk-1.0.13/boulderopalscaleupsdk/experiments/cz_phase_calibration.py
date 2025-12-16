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

from .common import Experiment
from .waveforms import Waveform


class CZPhaseCalibration(Experiment):
    """
    Parameters for running a Ramsey-like experiment to measure
    the CZ/single qubit phase associated with a CZ gate.

    Attributes
    ----------
    control_transmon : str
        The name of the control transmon qubit.
    target_transmon : str
        The name of the target transmon qubit.
    calibration_phase : Literal["1q_phases", "cphase"]
        Specifies which phase to calibrate:
        - "cphase": calibrate the CZ phase
        - "1q_phases": calibrate the single qubit phase
    ramsey_phases : list[float]
        List of phase angles (in radians) to sweep in the Ramsey experiment.
    qubit_amplitude_scale : float
        The amplitude scale factor for qubit pulses.
    coupler_amplitude_scale : float
        The amplitude scale factor for coupler pulses.
    drive_waveform : Waveform
        The waveform to use for the drive pulse.
    prep_padding_ns : int
        The padding to apply before the CZ pulse, in nanoseconds.
        Defaults to 16 ns.
    measurement_padding_ns : int
        The padding to apply after the CZ pulse, in nanoseconds.
        Defaults to 16 ns.
    repetitions : list[int]
        List of CZ echo repetitions to apply for each Ramsey point.
    recycle_delay_ns : int
        Delay time between consecutive shots of the experiment, in nanoseconds.
    shot_count : int
        The number of shots to be taken in the experiment.
        Defaults to 200.
    batch_analysis : bool
        Whether to perform batch analysis on the results.
    """

    _experiment_name: str = PrivateAttr("cz_phase_calibration")

    control_transmon: str
    target_transmon: str
    calibration_phase: Literal["1q_phases", "cphase"]
    ramsey_phases: list[float]
    qubit_amplitude_scale: float
    coupler_amplitude_scale: float
    drive_waveform: Waveform
    prep_padding_ns: int = 16
    measurement_padding_ns: int = 16
    repetitions: list[int]
    recycle_delay_ns: int = 500_000
    shot_count: int = 200
    batch_analysis: bool = False
    update: Literal["auto", "off", "prompt"] = "auto"
