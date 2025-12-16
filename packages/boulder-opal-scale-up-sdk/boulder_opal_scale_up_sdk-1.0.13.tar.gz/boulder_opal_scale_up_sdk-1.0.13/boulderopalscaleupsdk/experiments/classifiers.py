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

from typing import Annotated, Any, Literal

import numpy as np
from pydantic import BaseModel, BeforeValidator, ConfigDict


def _matrix_validator(value: Any) -> list[list[float]]:
    array_value = np.asarray(value)
    if array_value.shape != (2, 2):
        raise ValueError("Confusion matrix must be 2x2.")
    return array_value.tolist()


class Classifier(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LinearIQClassifier(Classifier):
    """
    Linear IQ classifier for single qubit readout.

    Attributes
    ----------
    projection : tuple[float, float]
        Optimal quadrature line to project over.
    threshold : float
        Threshold for binary classification.
    confusion_matrix : list[list[float]]
        Confusion matrix associated with the classifier.
    status : "calibrated" or "uncalibrated" or "stale"
        The calibration status of the classifier. Defaults to "calibrated".
    """

    projection: tuple[float, float]
    threshold: float
    confusion_matrix: Annotated[list[list[float]], BeforeValidator(_matrix_validator)]
    status: Literal["calibrated", "uncalibrated", "stale"] = "calibrated"


class LinearNDClassifier(Classifier):
    """
    Linear N-dimensional classifier.

    Attributes
    ----------
    projection : tuple[float, float, float, float]
        Optimal quadrature line to project over.
    threshold : float
        Threshold for binary classification.
    confusion_matrix : list[list[float]]
        Confusion matrix associated with the classifier.
    status : "calibrated" or "uncalibrated" or "stale"
        The calibration status of the classifier. Defaults to "calibrated".
    """

    projection: tuple[float, float, float, float]
    threshold: float
    confusion_matrix: Annotated[list[list[float]], BeforeValidator(_matrix_validator)]
    status: Literal["calibrated", "uncalibrated", "stale"] = "calibrated"


class ClassifierData(BaseModel):
    iq_classifiers: list[tuple[str, LinearIQClassifier]]
    leakage_classifiers: list[tuple[tuple[str, str], LinearNDClassifier]]
