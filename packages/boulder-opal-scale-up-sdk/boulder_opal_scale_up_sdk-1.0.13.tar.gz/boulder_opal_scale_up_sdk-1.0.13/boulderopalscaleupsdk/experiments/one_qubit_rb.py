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
from .waveforms import ConstantWaveform


class OneQubitRB(Experiment):
    """
    Parameters for running a one-qubit randomized benchmarking experiment.

    Attributes
    ----------
    transmon : str
        The reference for the transmon to target.
    gate : "sx" or "x"
        The gate to benchmark.
    seed : int or None, optional
        The random seed for sequence generation. Defaults to None.
    sequence_count : int, optional
        The number of random sequences to generate. Defaults to 10.
    clifford_depths : list of int, optional
        The list of Clifford depths to use for benchmarking.
        Defaults to a depth of 0 followed by powers of two from 1 up to 1024.
    recycle_delay_ns : int, optional
        The delay between consecutive shots, in nanoseconds. Defaults to 100,000 ns.
    shot_count : int, optional
        The number of shots per sequence to take. Defaults to 500.
    measure_waveform : ConstantWaveform or None, optional
        The waveform to use for the measurement pulse.
        Defaults to the measurement defcal.
    update : "auto" or "off" or "prompt", optional
        How the device should be updated after an experiment run. Defaults to auto.
    """

    _experiment_name: str = PrivateAttr("one_qubit_rb")

    transmon: str
    gate: Literal["sx", "x"]
    seed: int | None = None
    sequence_count: int = 10
    clifford_depths: list[int] = [0] + [2**i for i in range(10)]
    recycle_delay_ns: int = 100_000
    shot_count: int = 500
    measure_waveform: ConstantWaveform | None = None
    update: Literal["auto", "off", "prompt"] = "auto"
