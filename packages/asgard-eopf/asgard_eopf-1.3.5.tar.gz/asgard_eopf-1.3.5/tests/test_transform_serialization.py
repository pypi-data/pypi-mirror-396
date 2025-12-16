#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2023 CS GROUP
# Licensed to CS GROUP (CS) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# CS licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Unit tests for transform serialization
"""

from __future__ import annotations

import json
from typing import Any, Dict

import numpy as np
import pytest

from asgard.core.transform import (
    DynamicRotation,
    HomothetyTransform,
    RigidTransform,
    StaticTransform,
)
from asgard.models.thermoelastic import ThermoelasticModel


def test_static_transform_to_dict_single() -> None:
    """
    Test that StaticTransform.to_dict produces a JSON-serializable dictionary for a single transform.
    """
    translation = np.array([1.0, 2.0, 3.0], dtype="float64")
    matrix = np.eye(3, dtype="float64")
    transform = StaticTransform(translation=translation, matrix=matrix)

    data: Dict[str, Any] = transform.to_dict()

    # Basic structure checks
    assert data["type"] == "StaticTransform"
    assert isinstance(data["translation"], list)
    assert isinstance(data["matrix"], list)

    # Ensure JSON compatibility
    json.dumps(data)


def test_static_transform_round_trip_single() -> None:
    """
    Test that StaticTransform.to_dict and StaticTransform.from_dict preserve a single transform.
    """
    translation = np.array([1.0, 2.0, 3.0], dtype="float64")
    matrix = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
            [0.0, 0.0, 3.0],
        ],
        dtype="float64",
    )

    transform = StaticTransform(translation=translation, matrix=matrix)

    data = transform.to_dict()
    reconstructed = StaticTransform.from_dict(data)

    np.testing.assert_allclose(reconstructed.translation, transform.translation)
    np.testing.assert_allclose(reconstructed.matrix, transform.matrix)


def test_static_transform_round_trip_batch() -> None:
    """
    Test that StaticTransform.to_dict and StaticTransform.from_dict preserve batched transforms.
    """
    translation = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 2.0, 3.0],
        ],
        dtype="float64",
    )
    matrix = np.stack(
        [
            np.eye(3, dtype="float64"),
            2.0 * np.eye(3, dtype="float64"),
        ],
        axis=0,
    )

    transform = StaticTransform(translation=translation, matrix=matrix)

    data = transform.to_dict()
    reconstructed = StaticTransform.from_dict(data)

    np.testing.assert_allclose(reconstructed.translation, transform.translation)
    np.testing.assert_allclose(reconstructed.matrix, transform.matrix)


def test_static_transform_from_dict_missing_keys() -> None:
    """
    Test that StaticTransform.from_dict raises KeyError when required keys are missing.
    """
    valid_translation = [1.0, 2.0, 3.0]
    valid_matrix = np.eye(3, dtype="float64").tolist()

    # Missing translation
    data_missing_translation: Dict[str, Any] = {
        "type": "StaticTransform",
        "matrix": valid_matrix,
    }
    with pytest.raises(KeyError):
        StaticTransform.from_dict(data_missing_translation)

    # Missing matrix
    data_missing_matrix: Dict[str, Any] = {
        "type": "StaticTransform",
        "translation": valid_translation,
    }
    with pytest.raises(KeyError):
        StaticTransform.from_dict(data_missing_matrix)


def test_static_transform_from_dict_invalid_shapes() -> None:
    """
    Test that StaticTransform.from_dict raises when shapes or types are not valid.
    """
    # Invalid translation type: scalar instead of list
    data_bad_translation: Dict[str, Any] = {
        "type": "StaticTransform",
        "translation": 1.0,  # not a list
        "matrix": np.eye(3, dtype="float64").tolist(),
    }

    with pytest.raises(TypeError):
        StaticTransform.from_dict(data_bad_translation)

    # Invalid matrix shape: 2x2 instead of 3x3
    data_bad_matrix: Dict[str, Any] = {
        "type": "StaticTransform",
        "translation": [1.0, 2.0, 3.0],
        "matrix": [[1.0, 0.0], [0.0, 1.0]],
    }

    with pytest.raises(ValueError):
        StaticTransform.from_dict(data_bad_matrix)


def test_rigid_transform_to_dict_single() -> None:
    """
    Test that RigidTransform.to_dict produces a JSON-serializable dictionary for a single transform.
    """
    translation = np.array([1.0, 2.0, 3.0], dtype="float64")
    rotation = np.array([0.0, 0.0, 0.0, 1.0], dtype="float64")  # identity quaternion

    transform = RigidTransform(translation=translation, rotation=rotation)

    data = transform.to_dict()

    assert data["type"] == "RigidTransform"
    assert isinstance(data["translation"], list)
    assert isinstance(data["rotation"], list)

    # Check JSON compatibility
    json.dumps(data)


def test_rigid_transform_round_trip_single() -> None:
    """
    Test that RigidTransform.to_dict and RigidTransform.from_dict preserve a single rigid transform.
    """
    translation = np.array([1.0, 2.0, 3.0], dtype="float64")
    rotation = np.array([0.1, 0.2, 0.3, 0.9], dtype="float64")
    rotation = rotation / np.linalg.norm(rotation)  # normalize to valid quaternion

    transform = RigidTransform(translation=translation, rotation=rotation)

    data = transform.to_dict()
    reconstructed = RigidTransform.from_dict(data)

    np.testing.assert_allclose(reconstructed.translation, transform.translation)
    np.testing.assert_allclose(reconstructed.rotation.as_quat(), transform.rotation.as_quat(), rtol=0, atol=1e-12)


def test_rigid_transform_round_trip_batch() -> None:
    """
    Test that RigidTransform.to_dict and RigidTransform.from_dict preserve batched rigid transforms.
    """
    translation = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.5, 2.0, -1.0],
        ],
        dtype="float64",
    )

    quats = np.array(
        [
            [0.0, 0.0, 0.0, 1.0],  # identity
            [0.1, -0.2, 0.3, 0.9],  # some rotation
        ],
        dtype="float64",
    )
    # Normalize quaternions for safety
    quats = quats / np.linalg.norm(quats, axis=1, keepdims=True)

    transform = RigidTransform(translation=translation, rotation=quats)

    data = transform.to_dict()
    reconstructed = RigidTransform.from_dict(data)

    np.testing.assert_allclose(reconstructed.translation, transform.translation)
    np.testing.assert_allclose(reconstructed.rotation.as_quat(), transform.rotation.as_quat(), atol=1e-12)


def test_rigid_transform_from_dict_missing_keys() -> None:
    """
    Test that RigidTransform.from_dict raises KeyError when required keys are missing.
    """
    valid_translation = [1.0, 2.0, 3.0]
    valid_rotation = [0.0, 0.0, 0.0, 1.0]

    # Missing translation
    data_missing_translation = {
        "type": "RigidTransform",
        "rotation": valid_rotation,
    }
    with pytest.raises(KeyError):
        RigidTransform.from_dict(data_missing_translation)

    # Missing rotation
    data_missing_rotation = {
        "type": "RigidTransform",
        "translation": valid_translation,
    }
    with pytest.raises(KeyError):
        RigidTransform.from_dict(data_missing_rotation)


def test_rigid_transform_from_dict_invalid_shapes() -> None:
    """
    Test that RigidTransform.from_dict raises when shapes or types are not valid.
    """
    # Invalid translation type: scalar instead of list
    data_bad_translation = {
        "type": "RigidTransform",
        "translation": 1.0,  # not a list
        "rotation": [0.0, 0.0, 0.0, 1.0],
    }

    with pytest.raises(TypeError):
        RigidTransform.from_dict(data_bad_translation)

    # Invalid rotation shape: not length 4
    data_bad_rotation = {
        "type": "RigidTransform",
        "translation": [1.0, 2.0, 3.0],
        "rotation": [0.0, 0.0, 1.0],  # length 3, invalid
    }

    with pytest.raises(ValueError):
        RigidTransform.from_dict(data_bad_rotation)


def test_homothety_transform_to_dict_single() -> None:
    """
    Test that HomothetyTransform.to_dict produces a JSON-serializable dictionary for a single transform.
    """
    homothety = np.array([1.0, 2.0, -1.0], dtype="float64")

    transform = HomothetyTransform(homothety=homothety)

    data = transform.to_dict()

    assert data["type"] == "HomothetyTransform"
    assert isinstance(data["homothety"], list)

    # Check JSON compatibility
    json.dumps(data)


def test_homothety_transform_round_trip_single() -> None:
    """
    Test that HomothetyTransform.to_dict and HomothetyTransform.from_dict preserve a single transform.
    """
    homothety = np.array([1.5, -2.0, 0.5], dtype="float64")

    transform = HomothetyTransform(homothety=homothety)

    data = transform.to_dict()
    reconstructed = HomothetyTransform.from_dict(data)

    np.testing.assert_allclose(reconstructed.homothety, transform.homothety)


def test_homothety_transform_round_trip_batch() -> None:
    """
    Test that HomothetyTransform.to_dict and from_dict preserve batched homotheties.
    """
    homothety = np.array(
        [
            [1.0, 2.0, 3.0],
            [-1.0, 0.5, 0.25],
        ],
        dtype="float64",
    )

    transform = HomothetyTransform(homothety=homothety)

    data = transform.to_dict()
    reconstructed = HomothetyTransform.from_dict(data)

    np.testing.assert_allclose(reconstructed.homothety, transform.homothety)


def test_homothety_transform_from_dict_missing_keys() -> None:
    """
    Test that HomothetyTransform.from_dict raises KeyError when required keys are missing.
    """
    valid_homothety = [1.0, 2.0, 3.0]

    # Missing homothety
    data_missing_homothety = {
        "type": "HomothetyTransform",
    }

    with pytest.raises(KeyError):
        HomothetyTransform.from_dict(data_missing_homothety)


def test_homothety_transform_from_dict_invalid_shapes() -> None:
    """
    Test that HomothetyTransform.from_dict raises when shapes or types are not valid.
    """
    # Invalid homothety type: scalar instead of list
    data_bad_type = {
        "type": "HomothetyTransform",
        "homothety": 1.0,  # not a list
    }

    with pytest.raises(TypeError):
        HomothetyTransform.from_dict(data_bad_type)

    # Invalid homothety shape: 2 components instead of 3
    data_bad_shape = {
        "type": "HomothetyTransform",
        "homothety": [1.0, 2.0],  # wrong length
    }

    with pytest.raises(ValueError):
        HomothetyTransform.from_dict(data_bad_shape)


def test_dynamic_rotation_to_dict_single() -> None:
    """
    Test that DynamicRotation.to_dict produces a JSON-serializable dictionary.
    """
    config = {
        "rotation": np.radians(np.array([[90.0, 0.0, 0.0]], dtype="float64")),
        "epoch": "2024-03-20T11:34:00",
        "unit": "s",
        "ref": "GPS",
        "central_time": 3.14,
        "euler_order": "XYZ",
    }
    transform = DynamicRotation(**config)

    data = transform.to_dict()

    assert data["type"] == "DynamicRotation"
    assert isinstance(data["rotation"], list)
    assert isinstance(data["epoch"], str)
    assert isinstance(data["unit"], str)
    assert isinstance(data["ref"], str)
    assert isinstance(data["central_time"], float) or isinstance(data["central_time"], int)
    assert isinstance(data["euler_order"], str)

    # JSON compatibility
    json.dumps(data)


def test_dynamic_rotation_round_trip_single() -> None:
    """
    Test that DynamicRotation.to_dict and DynamicRotation.from_dict preserve a single transform.
    """
    config = {
        "rotation": np.radians(np.array([[90.0, 0.0, 0.0]], dtype="float64")),
        "epoch": "2024-03-20T11:34:00",
        "unit": "s",
        "ref": "GPS",
        "central_time": 3.14,
        "euler_order": "XYZ",
    }

    transform = DynamicRotation(**config)

    data = transform.to_dict()
    reconstructed = DynamicRotation.from_dict(data)

    np.testing.assert_allclose(reconstructed.polynomial, transform.polynomial)
    assert reconstructed.epoch == transform.epoch
    assert reconstructed.unit == transform.unit
    assert reconstructed.time_scale == transform.time_scale
    assert reconstructed.central_time == transform.central_time
    assert reconstructed.euler_order == transform.euler_order


def test_dynamic_rotation_round_trip_polynomial() -> None:
    """
    Test that DynamicRotation.to_dict and from_dict preserve a polynomial rotation (D > 1).
    """
    rotation = np.radians(
        np.array(
            [
                [90.0, 0.0, 0.0],
                [-9.0, 9.0, 0.0],
            ],
            dtype="float64",
        )
    )

    config = {
        "rotation": rotation,
        "epoch": "2024-03-20T11:34:00",
        "unit": "s",
        "ref": "GPS",
        "central_time": 3.14,
        "euler_order": "XYZ",
    }

    transform = DynamicRotation(**config)

    data = transform.to_dict()
    reconstructed = DynamicRotation.from_dict(data)

    np.testing.assert_allclose(reconstructed.polynomial, transform.polynomial)
    assert reconstructed.epoch == transform.epoch
    assert reconstructed.unit == transform.unit
    assert reconstructed.time_scale == transform.time_scale
    assert reconstructed.central_time == transform.central_time
    assert reconstructed.euler_order == transform.euler_order


def test_dynamic_rotation_from_dict_missing_keys() -> None:
    """
    Test that DynamicRotation.from_dict raises KeyError when required keys are missing.
    """
    data_missing_rotation = {
        "type": "DynamicRotation",
        "epoch": "2024-03-20T11:34:00",
        "unit": "s",
        "ref": "GPS",
        "central_time": 3.14,
        "euler_order": "XYZ",
    }

    with pytest.raises(KeyError):
        DynamicRotation.from_dict(data_missing_rotation)


def test_dynamic_rotation_from_dict_invalid_shapes() -> None:
    """
    Test that DynamicRotation.from_dict raises when the rotation field is invalid.
    """
    # rotation not a list
    data_bad_type = {
        "type": "DynamicRotation",
        "rotation": 1.0,
        "epoch": "2024-03-20T11:34:00",
        "unit": "s",
        "ref": "GPS",
        "central_time": 3.14,
        "euler_order": "XYZ",
    }

    with pytest.raises(TypeError):
        DynamicRotation.from_dict(data_bad_type)

    # rotation has wrong shape (not (D, 3))
    data_bad_shape = {
        "type": "DynamicRotation",
        "rotation": [[1.0, 2.0]],  # shape (1, 2) -> invalid
        "epoch": "2024-03-20T11:34:00",
        "unit": "s",
        "ref": "GPS",
        "central_time": 3.14,
        "euler_order": "XYZ",
    }

    with pytest.raises(ValueError):
        DynamicRotation.from_dict(data_bad_shape)


def test_thermoelastic_model_to_dict_minimal() -> None:
    """
    Test that ThermoelasticModel.to_dict produces a JSON-serializable dictionary
    from a minimal synthetic model.
    """
    # Build a tiny synthetic thermoelastic model directly via setup_model
    lut_times = np.array([0.0, 1.0], dtype="float64")
    lut_oop = np.array([10.0, 20.0], dtype="float64")
    pdoy = 0.5

    quaternion_lut: Dict[str, list[np.ndarray]] = {
        "instr_1": [
            np.array([[1.0, 0.0, 0.0, 0.0]], dtype="float64"),
            np.array([[0.0, 1.0, 0.0, 0.0]], dtype="float64"),
        ]
    }
    oop_grid: Dict[str, np.ndarray] = {
        "instr_1": np.array([[0.0], [180.0]], dtype="float64"),
    }

    model = ThermoelasticModel.__new__(ThermoelasticModel)
    model.setup_model(pdoy, quaternion_lut, oop_grid, lut_times, lut_oop)

    data = model.to_dict()

    assert data["type"] == "ThermoelasticModel"
    assert data["instruments"] == ["instr_1"]

    # JSON compatibility
    json.dumps(data)


def test_thermoelastic_model_round_trip() -> None:
    """
    Test that ThermoelasticModel.to_dict and ThermoelasticModel.from_dict
    preserve a minimal synthetic model.
    """
    lut_times = np.array([0.0, 1.0], dtype="float64")
    lut_oop = np.array([10.0, 20.0], dtype="float64")
    pdoy = 0.5

    quaternion_lut: Dict[str, list[np.ndarray]] = {
        "instr_1": [
            np.array([[1.0, 0.0, 0.0, 0.0]], dtype="float64"),
            np.array([[0.0, 1.0, 0.0, 0.0]], dtype="float64"),
        ]
    }
    oop_grid: Dict[str, np.ndarray] = {
        "instr_1": np.array([[0.0], [180.0]], dtype="float64"),
    }

    original = ThermoelasticModel.__new__(ThermoelasticModel)
    original.setup_model(pdoy, quaternion_lut, oop_grid, lut_times, lut_oop)

    data = original.to_dict()
    reconstructed = ThermoelasticModel.from_dict(data)

    assert isinstance(reconstructed, ThermoelasticModel)
    np.testing.assert_allclose(reconstructed.pdoy, original.pdoy)
    np.testing.assert_allclose(reconstructed.lut_times, original.lut_times)
    np.testing.assert_allclose(reconstructed.lut_oop, original.lut_oop)

    assert reconstructed.instruments == original.instruments
    for instr in original.instruments:
        oq1, oq2 = original.quaternion_lut[instr]
        rq1, rq2 = reconstructed.quaternion_lut[instr]
        np.testing.assert_allclose(rq1, oq1)
        np.testing.assert_allclose(rq2, oq2)

        np.testing.assert_allclose(reconstructed.oop_grid[instr], original.oop_grid[instr])
