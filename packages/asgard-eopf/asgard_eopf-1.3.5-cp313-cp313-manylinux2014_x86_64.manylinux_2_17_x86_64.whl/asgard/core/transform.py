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
Module for transform classes
"""

from __future__ import annotations

import pprint
from abc import ABC, abstractmethod
from typing import Any, Dict

import numpy as np
from scipy.spatial.transform import Rotation as R

from asgard.core.math import reorder_euler_angles
from asgard.core.schema import (
    ASCII_TIMESTAMP_SCHEMA,
    TIMESCALE_NAME_SCHEMA,
    does_validate,
    validate_or_throw,
)


class StaticTransform:
    """
    Static transformation, either a single one or a batch
    """

    def __init__(
        self,
        translation: np.ndarray | None = None,
        matrix: np.ndarray | None = None,
    ):
        """
        Constructor

        :param np.ndarray translation: translation to apply (single 3D vector or Nx3 array)
        :param np.ndarray matrix: 3x3 matrix to apply (single or a stack)
        """

        if translation is None:
            self.translation = np.zeros((3,), dtype="float64")
        elif isinstance(translation, np.ndarray):
            self.translation = translation
        else:
            self.translation = np.array(translation)

        self._matrix = None
        if matrix is None:
            self._matrix = np.eye(3, dtype="float64")
        elif isinstance(matrix, np.ndarray):
            self._matrix = matrix
        else:
            self._matrix = np.array(matrix)

        # check shapes
        assert self.translation.shape[-1] == 3, "Expect 3 components as last dimension for translation"
        assert (
            len(self._matrix.shape) >= 2 and self._matrix.shape[-1] == 3 and self._matrix.shape[-2] == 3
        ), "Expect 3x3 matrices"

        # check sizes
        nb_translation = self.translation.size // 3
        nb_matrices = self._matrix.size // 9

        # check determinant
        min_det = np.min(np.abs(np.linalg.det(self._matrix)))
        if min_det < 1e-9:
            raise RuntimeError(f"Matrix determinant too small ({min_det})")

        if nb_translation > 1 and nb_matrices > 1 and nb_translation != nb_matrices:
            raise RuntimeError(
                f"Mismatch between sizes of translation array ({nb_translation})" f" and matrices array ({nb_matrices})"
            )

    @property
    def matrix(self):
        """
        Accessor to internal matrix
        """
        return self._matrix

    def transform_position(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a position

        :param np.ndarray vec: 3D vector to transform
        """
        return self.translation + self.transform_direction(vec)

    def transform_direction(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a direction (i.e. no translation applied)

        :param np.ndarray vec: 3D vector to transform
        """

        vec_array = vec if isinstance(vec, np.ndarray) else np.array(vec, dtype="float64")
        if len(vec_array.shape) > 1:
            output = self._matrix @ vec_array[..., np.newaxis]
            return output[..., 0]
        return self._matrix @ vec_array

    def __len__(self) -> int:
        """
        Length operator
        """
        nb_translation = self.translation.size // 3
        nb_matrices = self._matrix.size // 9

        return max(nb_translation, nb_matrices)

    def __repr__(self) -> str:
        """
        Return a compact representation of this StaticTransform.

        For scalar transforms (single translation vector and 3x3 matrix),
        the translation values and matrix rows are shown explicitly. For
        batched transforms, only the shapes and the batch size are reported.
        This method must never raise.
        """
        try:
            batch_size = len(self)

            # Scalar case: translation (3,), matrix (3, 3)
            if (
                self.translation.ndim == 1
                and self.translation.shape == (3,)
                and self.matrix.ndim == 2
                and self.matrix.shape == (3, 3)
            ):
                t_list = [float(value) for value in self.translation]
                row_strings = []
                for row in self.matrix:
                    row_values = [float(value) for value in row]
                    row_strings.append("[" + ", ".join(f"{value:g}" for value in row_values) + "]")
                matrix_str = "[" + " ; ".join(row_strings) + "]"
                return f"StaticTransform(translation={t_list}, matrix={matrix_str})"

            # Batched or generic case: shapes + batch size
            return (
                "StaticTransform("
                f"translation_shape={self.translation.shape}, "
                f"matrix_shape={self.matrix.shape}, "
                f"batch_size={batch_size})"
            )
        except Exception as exc:  # pragma: no cover - defensive path
            return f"<StaticTransform repr-error: {exc!r}>"

    def inv(self):
        """
        Compute inverse transform

        :return: Inverse transform
        :rtype: StaticTransform
        """
        inv_trans = StaticTransform(matrix=np.linalg.inv(self.matrix))
        inv_trans.translation = -inv_trans.transform_direction(self.translation)
        return inv_trans

    def __mul__(self, other):
        """
        Compose with an other transform
        """
        # check other instance
        if not isinstance(other, StaticTransform):
            return NotImplemented

        # check they have the same length if both are arrays
        my_length = len(self)
        their_length = len(other)
        if my_length > 1 and their_length > 1 and my_length != their_length:
            raise RuntimeError("Can't combine two transformation arrays of different size")

        combined = StaticTransform(matrix=self.matrix @ other.matrix)
        combined.translation = self.translation + self.transform_direction(other.translation)

        return combined

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this transform into a JSON-serializable dictionary.

        :return: A dictionary representation of this transform.
        """
        return {
            "type": "StaticTransform",
            "translation": self.translation.tolist(),
            "matrix": self.matrix.tolist(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> StaticTransform:
        """
        Reconstruct a StaticTransform instance from a serialized dictionary.

        :param data: Dictionary produced by to_dict().
        :return: A reconstructed StaticTransform instance.
        :raises KeyError: If required keys are missing.
        :raises TypeError: If the stored values are not list-like.
        :raises ValueError: If the shapes of the arrays are not compatible.
        """
        if "translation" not in data:
            raise KeyError("Missing 'translation' key in StaticTransform.from_dict payload")
        if "matrix" not in data:
            raise KeyError("Missing 'matrix' key in StaticTransform.from_dict payload")

        translation_raw = data["translation"]
        matrix_raw = data["matrix"]

        if not isinstance(translation_raw, list):
            raise TypeError(
                "Invalid type for 'translation' in StaticTransform.from_dict payload: "
                f"{type(translation_raw)!r}, expected list"
            )
        if not isinstance(matrix_raw, list):
            raise TypeError(
                "Invalid type for 'matrix' in StaticTransform.from_dict payload: "
                f"{type(matrix_raw)!r}, expected list"
            )

        translation = np.asarray(translation_raw, dtype="float64")
        matrix = np.asarray(matrix_raw, dtype="float64")

        if translation.ndim not in (1, 2) or translation.shape[-1] != 3:
            raise ValueError(
                "Invalid translation shape in StaticTransform.from_dict payload: "
                f"{translation.shape}, expected (3,) or (N, 3)"
            )

        if matrix.ndim not in (2, 3) or matrix.shape[-2] != 3 or matrix.shape[-1] != 3:
            raise ValueError(
                "Invalid matrix shape in StaticTransform.from_dict payload: "
                f"{matrix.shape}, expected (3, 3) or (N, 3, 3)"
            )

        return cls(translation=translation, matrix=matrix)

    def dump(self) -> dict:
        """
        Dump the transform content to a dict
        """
        return {"translation": self.translation, "matrix": self.matrix}


class RigidTransform(StaticTransform):
    """
    Rigid transformation (translation + rotation), either a single one or a batch
    """

    def __init__(
        self,
        translation: np.ndarray | None = None,
        rotation: np.ndarray | None = None,
        euler_order: str | None = None,
    ):
        """
        Constructor

        :param np.ndarray translation: translation to apply (single 3D vector or Nx3 array)
        :param np.ndarray rotation: rotation to apply (single or a stack)
        :param str euler_order: Order of rotation for Euler angles (default to "XYZ")
        """

        # Call parent constructor
        super().__init__(translation=translation)

        self.rotation = None
        self._build_rotation(rotation, euler_order)

        # check sizes
        nb_translation = self.translation.size // 3
        try:
            nb_rotation = len(self.rotation)
        except TypeError:
            nb_rotation = 1
        if nb_translation > 1 and nb_rotation > 1 and nb_translation != nb_rotation:
            raise RuntimeError(
                f"Mismatch between sizes of translation array ({nb_translation})" f" and rotation array ({nb_rotation})"
            )

    def _build_rotation(self, rotation: np.ndarray, euler_order: str):
        """
        Build the rotation and choose between different kind of definition (quaternion, ...)

        :param np.ndarray rotation: rotation coefficients
        :param str euler_order: Order of rotation for Euler angles (default to "XYZ"). When given,
            the arrays of shape (3, 3) are understood as 3 rotations with Euler angles. Otherwise,
            it is a single 3x3 rotation matrix.
        """
        if rotation is None:
            rot_shape = ()
        elif isinstance(rotation, np.ndarray):
            rot_shape = rotation.shape
        else:
            rot_shape = np.array(rotation).shape

        order = euler_order or "XYZ"

        if rot_shape == (3, 3) and not euler_order:
            # check determinant is close to 1
            det = np.linalg.det(rotation)
            if np.abs(det - 1) > 0.1:
                raise RuntimeError(f"Matrix determinant too far from 1 for a rotation ({det})")
            self.rotation = R.from_matrix(rotation)
        elif rot_shape == (4,):
            self.rotation = R.from_quat(rotation)
        elif rot_shape == (3,):
            self.rotation = R.from_euler(order, reorder_euler_angles(rotation, order))
        elif len(rot_shape) == 3 and rot_shape[1:] == (3, 3):
            # check determinant is close to 1
            det = np.linalg.det(rotation)
            min_det = np.min(det)
            max_det = np.max(det)
            if np.max(np.abs(det - 1)) > 0.1:
                raise RuntimeError(f"Matrix determinants too far from 1 for a rotation [{min_det}, {max_det}]")
            self.rotation = R.from_matrix(rotation)
        elif len(rot_shape) == 2 and rot_shape[1:] == (4,):
            self.rotation = R.from_quat(rotation)
        elif len(rot_shape) == 2 and rot_shape[1:] == (3,):
            self.rotation = R.from_euler(order, reorder_euler_angles(rotation, order))
        else:
            self.rotation = R.identity()

    @property
    def matrix(self):
        """
        Accessor to internal matrix
        """
        return self.rotation.as_matrix()

    def transform_position(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a position

        :param np.ndarray vec: 3D vector to transform
        """
        return self.translation + self.rotation.apply(vec)

    def transform_direction(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a direction (i.e. no translation applied)

        :param np.ndarray vec: 3D vector to transform
        """
        return self.rotation.apply(vec)

    def __len__(self) -> int:
        """
        Length operator
        """
        nb_translation = self.translation.size // 3
        try:
            nb_rotation = len(self.rotation)
        except TypeError:
            nb_rotation = 1

        return max(nb_translation, nb_rotation)

    def __repr__(self) -> str:
        """
        Return a compact one-line representation of this RigidTransform.

        For scalar transforms, the translation and rotation (as Euler angles in
        degrees with a fixed 'XYZ' order) are displayed explicitly. For batched
        transforms, only the shapes and the batch size are reported. This method
        must never raise.
        """
        try:
            batch_size = len(self)

            # Scalar case: translation (3,), single rotation
            if self.translation.ndim == 1 and self.translation.shape == (3,):
                try:
                    euler = self.rotation.as_euler("XYZ", degrees=True)
                    if euler.ndim == 1 and euler.shape == (3,):
                        t_list = self.translation.tolist()
                        euler_list = [float(angle) for angle in euler]
                        return (
                            "RigidTransform(" f"translation={t_list}, " f"euler_deg={euler_list}, " "euler_order='XYZ')"
                        )
                except Exception:
                    # Fallback to quaternion representation if Euler extraction fails
                    quat = self.rotation.as_quat()
                    if quat.ndim == 1 and quat.shape == (4,):
                        t_list = self.translation.tolist()
                        q_list = quat.tolist()
                        return "RigidTransform(" f"translation={t_list}, " f"rotation_quat={q_list})"

            # Batched or generic case
            quat = self.rotation.as_quat()
            return (
                "RigidTransform("
                f"translation_shape={self.translation.shape}, "
                f"rotation_shape={quat.shape}, "
                f"batch_size={batch_size})"
            )

        except Exception as exc:  # pragma: no cover - defensive
            return f"<RigidTransform repr-error: {exc!r}>"

    def inv(self):
        """
        Compute inverse transform

        :return: Inverse transform
        :rtype: RigidTransform
        """
        inv_trans = RigidTransform()
        inv_trans.rotation = self.rotation.inv()
        inv_trans.translation = -inv_trans.rotation.apply(self.translation)
        return inv_trans

    def __mul__(self, other):
        """
        Compose with an other transform
        """
        # check other instance
        if not isinstance(other, StaticTransform):
            return NotImplemented

        if not isinstance(other, RigidTransform):
            return super().__mul__(other)

        # check they have the same length if both are arrays
        my_length = len(self)
        their_length = len(other)
        if my_length > 1 and their_length > 1 and my_length != their_length:
            raise RuntimeError("Can't combine two transformation arrays of different size")

        # R_out = self.R * other.R
        combined = RigidTransform()
        combined.rotation = self.rotation * other.rotation
        combined.translation = self.translation + self.rotation.apply(other.translation)

        return combined

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this rigid transform into a JSON-serializable dictionary.

        The rotation is serialized as quaternions using scipy Rotation.as_quat(),
        which yields either a single quaternion (shape (4,)) or an array of
        quaternions (shape (N, 4)).

        :return: A dictionary representation of this rigid transform.
        """
        return {
            "type": "RigidTransform",
            "translation": self.translation.tolist(),
            "rotation": self.rotation.as_quat().tolist(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RigidTransform:
        """
        Reconstruct a RigidTransform instance from a serialized dictionary.

        The dictionary is expected to contain a translation and a rotation,
        where the rotation is stored as quaternions compatible with
        scipy.spatial.transform.Rotation.from_quat.

        :param data: Dictionary produced by to_dict().
        :return: A reconstructed RigidTransform instance.
        :raises KeyError: If required keys are missing.
        :raises TypeError: If the stored values are not list-like.
        :raises ValueError: If the shapes of the arrays are not compatible.
        """
        if "translation" not in data:
            raise KeyError("Missing 'translation' key in RigidTransform.from_dict payload")
        if "rotation" not in data:
            raise KeyError("Missing 'rotation' key in RigidTransform.from_dict payload")

        translation_raw = data["translation"]
        rotation_raw = data["rotation"]

        if not isinstance(translation_raw, list):
            raise TypeError(
                "Invalid type for 'translation' in RigidTransform.from_dict payload: "
                f"{type(translation_raw)!r}, expected list"
            )
        if not isinstance(rotation_raw, list):
            raise TypeError(
                "Invalid type for 'rotation' in RigidTransform.from_dict payload: "
                f"{type(rotation_raw)!r}, expected list"
            )

        translation = np.asarray(translation_raw, dtype="float64")
        rotation = np.asarray(rotation_raw, dtype="float64")

        if translation.ndim not in (1, 2) or translation.shape[-1] != 3:
            raise ValueError(
                "Invalid translation shape in RigidTransform.from_dict payload: "
                f"{translation.shape}, expected (3,) or (N, 3)"
            )

        if rotation.ndim not in (1, 2) or rotation.shape[-1] != 4:
            raise ValueError(
                "Invalid rotation shape in RigidTransform.from_dict payload: "
                f"{rotation.shape}, expected (4,) or (N, 4)"
            )

        return cls(translation=translation, rotation=rotation)

    def dump(self) -> dict:
        """
        Dump the transform content to a dict
        """
        return {"translation": self.translation, "rotation": self.rotation.as_quat()}


class HomothetyTransform(StaticTransform):
    """
    Homothety transformation, either a single one or a batch
    """

    def __init__(
        self,
        homothety: np.ndarray | None = None,
    ):
        """
        Constructor

        :param np.ndarray homothety: homothety to apply (single or a stack)
        """

        # Call parent constructor
        super().__init__()

        if homothety is None:
            self.homothety = np.ones((3,), dtype="float64")
        elif isinstance(homothety, np.ndarray):
            self.homothety = homothety
        else:
            self.homothety = np.array(homothety)

        # check sizes
        if self.homothety.shape[-1] != 3:
            raise RuntimeError(f"Wrong number of components in homothety, got {self.homothety.shape[-1]}, expected 3")

    @property
    def matrix(self):
        """
        Accessor to internal matrix
        """
        return np.eye(3) * self.homothety[..., np.newaxis]

    def transform_position(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a position

        :param np.ndarray vec: 3D vector to transform
        """

        vec_array = vec if isinstance(vec, np.ndarray) else np.array(vec, dtype="float64")
        if len(self) != 1 and self.homothety.shape != vec_array.shape:
            raise ValueError(
                f"Mismatch between transform shape ({self.homothety.shape}) and coordinates shape ({vec_array.shape})"
            )
        return self.homothety * vec_array

    def transform_direction(self, vec: np.ndarray) -> np.ndarray:
        """
        Apply transformation to a direction (i.e. no translation applied)

        :param np.ndarray vec: 3D vector to transform
        """
        return self.transform_position(vec)

    def __len__(self) -> int:
        """
        Length operator
        """
        return self.homothety.size // 3

    def __repr__(self) -> str:
        """
        Return a compact one-line representation of this HomothetyTransform.

        For scalar transforms, the homothety vector is displayed explicitly.
        For batched transforms, only the shape and the batch size are reported.
        This method must never raise.
        """
        try:
            batch_size = len(self)

            if self.homothety.ndim == 1 and self.homothety.shape == (3,):
                h_list = [float(value) for value in self.homothety]
                return f"HomothetyTransform(homothety={h_list})"

            return "HomothetyTransform(" f"homothety_shape={self.homothety.shape}, " f"batch_size={batch_size})"

        except Exception as exc:  # pragma: no cover - defensive
            return f"<HomothetyTransform repr-error: {exc!r}>"

    def inv(self):
        """
        Compute inverse transform

        :return: Inverse transform
        :rtype: HomothetyTransform
        """
        inv_trans = HomothetyTransform()
        inv_trans.homothety = 1.0 / self.homothety
        return inv_trans

    def __mul__(self, other):
        """
        Compose with an other transform
        """
        # check other instance
        if not isinstance(other, StaticTransform):
            return NotImplemented

        if not isinstance(other, HomothetyTransform):
            return super().__mul__(other)

        # check they have the same length if both are arrays
        my_length = len(self)
        their_length = len(other)
        if my_length > 1 and their_length > 1 and my_length != their_length:
            raise RuntimeError("Can't combine two transformation arrays of different size")

        combined = HomothetyTransform()
        combined.homothety = self.homothety * other.homothety

        return combined

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this homothety transform into a JSON-serializable dictionary.

        :return: A dictionary representation of this homothety transform.
        """
        return {
            "type": "HomothetyTransform",
            "homothety": self.homothety.tolist(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> HomothetyTransform:
        """
        Reconstruct a HomothetyTransform instance from a serialized dictionary.

        The dictionary is expected to contain a homothety array compatible with
        the HomothetyTransform constructor, i.e. a single 3D vector or an (N, 3) array.

        :param data: Dictionary produced by to_dict().
        :return: A reconstructed HomothetyTransform instance.
        :raises KeyError: If required keys are missing.
        :raises TypeError: If the stored values are not list-like.
        :raises ValueError: If the shapes of the arrays are not compatible.
        """
        if "homothety" not in data:
            raise KeyError("Missing 'homothety' key in HomothetyTransform.from_dict payload")

        homothety_raw = data["homothety"]

        if not isinstance(homothety_raw, list):
            raise TypeError(
                "Invalid type for 'homothety' in HomothetyTransform.from_dict payload: "
                f"{type(homothety_raw)!r}, expected list"
            )

        homothety = np.asarray(homothety_raw, dtype="float64")

        if homothety.ndim not in (1, 2) or homothety.shape[-1] != 3:
            raise ValueError(
                "Invalid homothety shape in HomothetyTransform.from_dict payload: "
                f"{homothety.shape}, expected (3,) or (N, 3)"
            )

        return cls(homothety=homothety)

    def dump(self) -> dict:
        """
        Dump the transform content to a dict
        """
        return {"homothety": self.homothety}


class TimeBasedTransform(ABC):
    """
    Time based transformation
    """

    @classmethod
    def build(cls, **kwargs):
        """
        Create a TimeBasedTransform from a config dictionnary
        """
        for subcls in cls.__subclasses__():
            if does_validate(kwargs, subcls.init_schema()):
                return subcls(**kwargs)

        raise RuntimeError("No model found")

    @classmethod
    @abstractmethod
    def init_schema(cls):
        """
        Define the initialization schema
        """

    def __repr__(self) -> str:
        """
        Generic debug representation of a time-based transform.

        This base implementation reports high-level metadata when available
        (e.g. time_scale, reference_time, n_times). Subclasses are encouraged
        to override this method to expose the parameters that best characterize
        the model. This method must never raise.
        """
        try:
            cls_name = type(self).__name__

            # Optional metadata — subclasses may or may not define these
            time_scale = getattr(self, "time_scale", None)
            reference_time = getattr(self, "reference_time", None)
            n_times = getattr(self, "n_times", None)

            parts = []
            if time_scale is not None:
                parts.append(f"time_scale={time_scale!r}")
            if reference_time is not None:
                parts.append(f"reference_time={reference_time!r}")
            if n_times is not None:
                parts.append(f"n_times={n_times}")

            joined = ", ".join(parts)
            return f"{cls_name}({joined})"

        except Exception as exc:  # pragma: no cover — defensive path
            return f"<{type(self).__name__} repr-error: {exc!r}>"

    @abstractmethod
    def estimate(self, time_array: dict) -> StaticTransform:
        """
        Estimate a series of transforms for input given times

        :param dict time_array: input time array structure (see TIME_ARRAY)
        :return: a :class:`StaticTransform` object with all the transforms stacked
        """

    @abstractmethod
    def inv(self):
        """
        Generate a new :class:`Thermoelastic` model with inversed quaternions
        """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this time-based transform into a JSON-serializable dictionary.

        Subclasses must implement this method and return a dictionary containing
        all the information required to reconstruct the instance with from_dict().

        :return: A dictionary representation of this time-based transform.
        """

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> TimeBasedTransform:
        """
        Reconstruct a time-based transform instance from a serialized dictionary.

        Subclasses must implement this method and be able to rebuild a valid
        instance from the data structure returned by to_dict().

        :param data: Dictionary produced by to_dict().
        :return: A reconstructed time-based transform instance.
        """


class DynamicRotation(TimeBasedTransform):
    """
    Dynamic rotation with polynomial coefficients
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """

        # check input args
        validate_or_throw(kwargs, DynamicRotation.init_schema())

        self.polynomial = kwargs["rotation"]
        self.epoch = kwargs.get("epoch", "2000-01-01T00:00:00")
        self.unit = kwargs.get("unit", "d")
        self.time_scale = kwargs.get("ref", "GPS")
        self.central_time = kwargs.get("central_time", 0.0)
        self.euler_order = kwargs.get("euler_order", "XYZ")

    @classmethod
    def init_schema(cls):
        """
        Define the initialization schema
        """
        return {
            "type": "object",
            "properties": {
                "rotation": {
                    "type": "array",
                    "shape": [":", 3],
                    "description": "Polynomial coefficient for rotation angles (in radians) of shape "
                    "(D, 3) where D is the maximum degree of the polynomial",
                },
                "epoch": ASCII_TIMESTAMP_SCHEMA,
                "unit": {"type": "string", "pattern": "^(d|s)$"},
                "ref": TIMESCALE_NAME_SCHEMA,
                "central_time": {
                    "type": "number",
                    "description": "Time offset corresponding to x=0 in polynome",
                },
                "euler_order": {"type": "string", "description": "Axis order for Euler angles (default: 'XYZ')"},
            },
            "required": ["rotation"],
            "additionalProperties": False,
        }

    def __repr__(self) -> str:
        """
        Return a compact readable representation of this DynamicRotation.

        Shows:
        - polynomial degree + number of coeffs
        - a small preview of the polynomial coefficients
        - temporal metadata (epoch/unit/ref/etc.)

        This method must never raise.
        """
        try:
            poly = np.asarray(self.polynomial)

            # Basic polynomial info
            n_coeffs = poly.shape[0] if poly.ndim >= 1 else None
            n_components = poly.shape[1] if poly.ndim >= 2 else None
            degree = n_coeffs - 1 if n_coeffs is not None else None

            # Build preview of polynomial coefficients (first 3 rows max)
            preview_lines = []
            if n_coeffs is not None and n_components is not None:
                max_preview = min(n_coeffs, 3)
                for i in range(max_preview):
                    row = ", ".join(f"{float(v):.3g}" for v in poly[i])
                    preview_lines.append(f"[{row}]")
                if n_coeffs > 3:
                    preview_lines.append("...")

            preview_str = "[" + ", ".join(preview_lines) + "]" if preview_lines else "<?>"

            parts = [
                f"degree={degree}",
                f"n_coeffs={n_coeffs}",
                f"n_components={n_components}",
                f"coeffs={preview_str}",
                f"epoch={self.epoch!r}",
                f"unit={self.unit!r}",
                f"ref={self.time_scale!r}",
                f"central_time={float(self.central_time)}",
                f"euler_order={self.euler_order!r}",
            ]

            return "DynamicRotation(" + ", ".join(parts) + ")"

        except Exception as exc:  # pragma: no cover
            return f"<DynamicRotation repr-error: {exc!r}>"

    def estimate(self, time_array: dict) -> StaticTransform:
        """
        Estimate a series of transforms for input given times

        :param dict time_array: input time array structure (see TIME_ARRAY)
        :return: a :class:`StaticTransform` object with all the transforms stacked
        """

        scale = time_array.get("ref", "GPS")
        if scale != self.time_scale:
            raise RuntimeError(f"The time scale given ({scale}) is different from the expected one ({self.time_scale})")

        size = len(time_array["offsets"])

        # handle conversion to target epoch, unit

        # pylint: disable=import-outside-toplevel
        from asgard.models.time import TimeReference

        tr = TimeReference()
        target_time_array = tr.change_epoch_and_unit(time_array, epoch=self.epoch, unit=self.unit)

        # center times around central_time
        time_offsets = target_time_array["offsets"] - self.central_time

        # compute angles
        time_exp = np.ones((size,), dtype="float64")
        angles = np.outer(time_exp, self.polynomial[0])
        for coeff in self.polynomial[1:]:
            time_exp = time_exp * time_offsets
            angles += np.outer(time_exp, coeff)

        # build rotations
        return RigidTransform(rotation=angles, euler_order=self.euler_order)

    def inv(self):
        """
        Generate a new :class:`DynamicRotation` model with inversed rotations. All polynomial
        coefficients are multiplied by -1, and the Euler order is reversed.

        :return: DynamicRotation with inversed rotations
        """

        config = {
            "rotation": -self.polynomial,
            "epoch": self.epoch,
            "unit": self.unit,
            "ref": self.time_scale,
            "central_time": self.central_time,
            "euler_order": self.euler_order[::-1],
        }

        return DynamicRotation(**config)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this dynamic rotation into a JSON-serializable dictionary.

        The polynomial coefficients are serialized under the 'rotation' key, using
        the same convention as the DynamicRotation initialization schema.
        """
        return {
            "type": "DynamicRotation",
            "rotation": np.asarray(self.polynomial, dtype="float64").tolist(),
            "epoch": self.epoch,
            "unit": self.unit,
            "ref": self.time_scale,
            "central_time": float(self.central_time),
            "euler_order": self.euler_order,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DynamicRotation:
        """
        Reconstruct a DynamicRotation instance from a serialized dictionary.

        The dictionary is expected to contain the fields required by the
        DynamicRotation constructor:
        - rotation: polynomial coefficients for Euler angles in radians, of shape (D, 3)
        - epoch: ISO-8601 date-time string
        - unit: time unit (e.g. 's' or 'd')
        - ref: time scale name (e.g. 'GPS')
        - central_time: central time in the given unit
        - euler_order: axis order for Euler angles (default: 'XYZ')

        :param data: Dictionary produced by to_dict().
        :return: A reconstructed DynamicRotation instance.
        :raises KeyError: If required keys are missing.
        :raises TypeError: If the stored values are not of the expected types.
        :raises ValueError: If the shapes of the arrays are not compatible.
        """
        if "rotation" not in data:
            raise KeyError("Missing 'rotation' key in DynamicRotation.from_dict payload")

        rotation_raw = data["rotation"]

        if not isinstance(rotation_raw, list):
            raise TypeError(
                "Invalid type for 'rotation' in DynamicRotation.from_dict payload: "
                f"{type(rotation_raw)!r}, expected list"
            )

        rotation = np.asarray(rotation_raw, dtype="float64")

        # We expect a polynomial of shape (D, 3)
        if rotation.ndim != 2 or rotation.shape[1] != 3:
            raise ValueError(
                "Invalid rotation shape in DynamicRotation.from_dict payload: " f"{rotation.shape}, expected (D, 3)"
            )

        epoch = data.get("epoch", "2000-01-01T00:00:00")
        unit = data.get("unit", "d")
        time_scale = data.get("ref", "GPS")
        central_time = float(data.get("central_time", 0.0))
        euler_order = data.get("euler_order", "XYZ")

        if not isinstance(epoch, str):
            raise TypeError(
                "Invalid type for 'epoch' in DynamicRotation.from_dict payload: " f"{type(epoch)!r}, expected str"
            )
        if not isinstance(unit, str):
            raise TypeError(
                "Invalid type for 'unit' in DynamicRotation.from_dict payload: " f"{type(unit)!r}, expected str"
            )
        if not isinstance(time_scale, str):
            raise TypeError(
                "Invalid type for 'ref' in DynamicRotation.from_dict payload: " f"{type(time_scale)!r}, expected str"
            )
        if not isinstance(euler_order, str):
            raise TypeError(
                "Invalid type for 'euler_order' in DynamicRotation.from_dict payload: "
                f"{type(euler_order)!r}, expected str"
            )

        config = {
            "rotation": rotation,
            "epoch": epoch,
            "unit": unit,
            "ref": time_scale,
            "central_time": central_time,
            "euler_order": euler_order,
        }

        return cls(**config)
