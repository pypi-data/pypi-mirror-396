#!/usr/bin/env python
# coding: utf8
#
# Copyright 2022-2025 CS GROUP
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
Unit tests for transform __repr__ implementations.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
import pytest

from asgard.core.transform import (
    DynamicRotation,
    HomothetyTransform,
    RigidTransform,
    StaticTransform,
)
from asgard.models.thermoelastic import ThermoelasticModel


def test_static_transform_repr_scalar() -> None:
    """
    The repr of a scalar StaticTransform must contain class name and fields.
    """
    translation = np.array([1.0, 2.0, 3.0], dtype="float64")
    matrix = np.eye(3, dtype="float64")

    transform = StaticTransform(translation=translation, matrix=matrix)
    representation = repr(transform)

    assert "StaticTransform" in representation
    assert "translation=" in representation
    assert "matrix=" in representation
    assert "batch_size" not in representation


def test_static_transform_repr_batch_size() -> None:
    """
    The repr of a batched StaticTransform must expose the batch size.
    """
    translation = np.zeros((5, 3), dtype="float64")
    matrix = np.repeat(np.eye(3, dtype="float64")[np.newaxis, ...], 5, axis=0)

    transform = StaticTransform(translation=translation, matrix=matrix)
    representation = repr(transform)

    assert "StaticTransform" in representation
    assert "batch_size=5" in representation


def test_static_transform_repr_never_raises() -> None:
    """
    repr must never raise an exception, even in unexpected situations.
    """
    transform = StaticTransform()

    try:
        _ = repr(transform)
    except Exception as exc:  # pragma: no cover - this should not happen
        pytest.fail(f"StaticTransform.__repr__ raised an exception: {exc!r}")


def test_rigid_transform_repr_scalar() -> None:
    translation = np.array([1.0, 2.0, 3.0], dtype="float64")
    rotation = np.array([0.0, 0.0, 0.0, 1.0], dtype="float64")

    transform = RigidTransform(translation=translation, rotation=rotation)
    representation = repr(transform)

    assert "RigidTransform" in representation
    assert "translation=" in representation
    assert "euler_deg=" in representation
    assert "euler_order='XYZ'" in representation
    assert "batch_size" not in representation


def test_rigid_transform_repr_batch() -> None:
    """
    The repr of a batched RigidTransform must expose the batch size and shapes.
    """
    translation = np.zeros((4, 3), dtype="float64")
    rotation = np.zeros((4, 4), dtype="float64")
    rotation[:, 3] = 1.0  # identity quaternions

    transform = RigidTransform(translation=translation, rotation=rotation)
    representation = repr(transform)

    assert "RigidTransform" in representation
    assert "batch_size=4" in representation
    assert "translation_shape" in representation
    assert "rotation_shape" in representation


def test_rigid_transform_repr_never_raises() -> None:
    """
    repr must never raise an exception, even in unexpected situations.
    """
    transform = RigidTransform()

    try:
        _ = repr(transform)
    except Exception as exc:  # pragma: no cover - this should not happen
        pytest.fail(f"RigidTransform.__repr__ raised an exception: {exc!r}")


def test_homothety_transform_repr_scalar() -> None:
    """
    The repr of a scalar HomothetyTransform must expose the homothety vector.
    """
    homothety = np.array([1.0, 2.0, 3.0], dtype="float64")

    transform = HomothetyTransform(homothety=homothety)
    representation = repr(transform)

    assert "HomothetyTransform" in representation
    assert "homothety=" in representation
    assert "batch_size" not in representation


def test_homothety_transform_repr_batch() -> None:
    """
    The repr of a batched HomothetyTransform must expose the batch size and shape.
    """
    homothety = np.ones((4, 3), dtype="float64")

    transform = HomothetyTransform(homothety=homothety)
    representation = repr(transform)

    assert "HomothetyTransform" in representation
    assert "homothety_shape=(4, 3)" in representation
    assert "batch_size=4" in representation


def test_homothety_transform_repr_never_raises() -> None:
    """
    repr must never raise an exception, even in unexpected situations.
    """
    transform = HomothetyTransform()

    try:
        _ = repr(transform)
    except Exception as exc:  # pragma: no cover - this should not happen
        pytest.fail(f"HomothetyTransform.__repr__ raised an exception: {exc!r}")


def test_dynamic_rotation_repr_basic() -> None:
    """
    The repr of DynamicRotation must expose degree, polynomial structure,
    and temporal metadata for a simple configuration.
    """
    rotation = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0e-3, 2.0e-3, 3.0e-3],
        ],
        dtype="float64",
    )

    transform = DynamicRotation(rotation=rotation)
    representation = repr(transform)

    assert "DynamicRotation(" in representation
    assert "degree=1" in representation
    assert "n_coeffs=2" in representation
    assert "n_components=3" in representation
    assert "coeffs=[[" in representation

    # Preview of the first coefficient rows
    assert "[0, 0, 0]" in representation
    assert "[0.001, 0.002, 0.003]" in representation

    # Default temporal metadata must appear in the repr
    assert "epoch='2000-01-01T00:00:00'" in representation
    assert "unit='d'" in representation
    assert "ref='GPS'" in representation
    assert "central_time=0.0" in representation
    assert "euler_order='XYZ'" in representation


def test_dynamic_rotation_repr_custom_metadata() -> None:
    """
    The repr must reflect non-default temporal metadata and still expose
    the polynomial structure in a compact way.
    """
    rotation = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, -2.0, 3.5],
            [0.1, 0.2, 0.3],
            [4.0, 5.0, 6.0],
        ],
        dtype="float64",
    )

    transform = DynamicRotation(
        rotation=rotation,
        epoch="2025-01-01T12:00:00",
        unit="s",
        ref="UTC",
        central_time=123.0,
        euler_order="ZYX",
    )

    representation = repr(transform)

    assert "DynamicRotation(" in representation
    assert "degree=3" in representation
    assert "n_coeffs=4" in representation
    assert "n_components=3" in representation
    assert "coeffs=[[" in representation

    # Check for a few representative coefficient rows (not exhaustive)
    assert "[0, 0, 0]" in representation
    assert "[1, -2, 3.5]" in representation or "[1, -2, 3.5" in representation

    # Check temporal metadata
    assert "epoch='2025-01-01T12:00:00'" in representation
    assert "unit='s'" in representation
    assert "ref='UTC'" in representation
    assert "central_time=123.0" in representation
    assert "euler_order='ZYX'" in representation


def test_dynamic_rotation_repr_long_polynomial_uses_ellipsis() -> None:
    """
    For a long polynomial, the repr must use an ellipsis in the coefficients
    preview instead of dumping all rows.
    """
    rotation = np.zeros((6, 3), dtype="float64")

    transform = DynamicRotation(rotation=rotation)
    representation = repr(transform)

    assert "DynamicRotation(" in representation
    assert "degree=5" in representation
    assert "n_coeffs=6" in representation
    assert "n_components=3" in representation
    assert "coeffs=[[" in representation

    # Must contain an ellipsis to indicate truncation for large polynomials
    assert "..." in representation


def test_dynamic_rotation_repr_never_raises() -> None:
    """
    repr must never raise an exception, even in unexpected situations.
    """
    rotation = np.zeros((1, 3), dtype="float64")
    transform = DynamicRotation(rotation=rotation)

    try:
        representation = repr(transform)
    except Exception as exc:  # pragma: no cover - this should not happen
        pytest.fail(f"DynamicRotation.__repr__ raised an exception: {exc!r}")

    assert "repr-error" not in representation


def _build_dummy_thermoelastic_model(n_instruments: int = 2) -> ThermoelasticModel:
    """
    Build a minimal ThermoelasticModel instance for repr tests.

    The instance is constructed via __new__ and setup_model() to avoid
    depending on the full thermoelastic tables used in other tests.
    """
    model = ThermoelasticModel.__new__(ThermoelasticModel)

    pdoy = 0.5
    lut_times = np.linspace(0.0, 10.0, 5, dtype="float64")
    lut_oop = np.linspace(0.0, 360.0, 5, dtype="float64")

    instruments = [f"instr_{idx + 1}" for idx in range(n_instruments)]

    quaternion_lut: Dict[str, List[np.ndarray]] = {}
    oop_grid: Dict[str, np.ndarray] = {}

    for name in instruments:
        # Two DoY slices, each with 3 grid points and 4 quaternion components
        quat_doy1 = np.zeros((3, 4), dtype="float64")
        quat_doy1[:, 0] = 1.0  # identity quaternions
        quat_doy2 = np.zeros((3, 4), dtype="float64")
        quat_doy2[:, 0] = 1.0

        quaternion_lut[name] = [quat_doy1, quat_doy2]

        # Two DoY grids of 3 on-orbit positions each
        grid = np.vstack(
            [
                np.linspace(0.0, 180.0, 3, dtype="float64"),
                np.linspace(180.0, 360.0, 3, dtype="float64"),
            ]
        )
        oop_grid[name] = grid

    model.setup_model(
        pdoy=pdoy,
        quaternion_lut=quaternion_lut,
        oop_grid=oop_grid,
        lut_times=lut_times,
        lut_oop=lut_oop,
    )
    return model


def test_thermoelastic_model_repr_basic() -> None:
    """
    The repr of ThermoelasticModel must summarize pdoy, instruments and LUT sizes.
    """
    model = _build_dummy_thermoelastic_model(n_instruments=2)
    representation = repr(model)

    assert "ThermoelasticModel(" in representation
    assert "n_instruments=2" in representation
    assert "instr_1" in representation
    assert "instr_2" in representation
    assert "lut_times_len=5" in representation
    assert "lut_oop_len=5" in representation
    assert "quat_shape=(3, 4)/(3, 4)" in representation


def test_thermoelastic_model_repr_instrument_preview_truncation() -> None:
    """
    When there are many instruments, the repr must truncate the instrument list
    and use an ellipsis in the preview.
    """
    model = _build_dummy_thermoelastic_model(n_instruments=5)
    representation = repr(model)

    assert "ThermoelasticModel(" in representation
    assert "n_instruments=5" in representation
    # Preview must include the first few names and an ellipsis
    assert "instr_1" in representation
    assert "instr_3" in representation
    assert "..." in representation


def test_thermoelastic_model_repr_never_raises() -> None:
    """
    repr must never raise an exception, even in unexpected situations.
    """
    model = _build_dummy_thermoelastic_model(n_instruments=1)

    try:
        representation = repr(model)
    except Exception as exc:  # pragma: no cover - this should not happen
        pytest.fail(f"ThermoelasticModel.__repr__ raised an exception: {exc!r}")

    assert "repr-error" not in representation
