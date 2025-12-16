from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Optional, Tuple, Union

import numpy as np

Numeric = Union[int, float]


@dataclass
class _Vector(ABC):
    x: Numeric
    y: Numeric
    z: Optional[Numeric] = None

    @property
    def xy(self):
        return self.x, self.y

    @property
    def yx(self):
        return self.y, self.x

    @property
    def xyz(self):
        return self.x, self.y, self.z

    @property
    def yxz(self):
        return self.y, self.x, self.z

    @property
    def zyx(self):
        return self.z, self.y, self.x

    @property
    def area(self):
        return self.x * self.y * self.z if self.z is not None else self.x * self.y

    def __add__(self, other):
        if self.z is None or other.z is None:
            return xy2vector((self.x + other.x, self.y + other.y))
        return xyz2vector((self.x + other.x, self.y + other.y, self.z + other.z))

    def __sub__(self, other):
        if self.z is None or other.z is None:
            return xy2vector((self.x - other.x, self.y - other.y))
        return xyz2vector((self.x - other.x, self.y - other.y, self.z - other.z))

    def __mul__(self, other):
        if self.z is None or other.z is None:
            return xy2vector((self.x * other.x, self.y * other.y))
        return xyz2vector((self.x * other.x, self.y * other.y, self.z * other.z))

    def __truediv__(self, other):
        if self.z is None or other.z is None:
            return xy2vector((self.x / other.x, self.y / other.y))
        return xyz2vector((self.x / other.x, self.y / other.y, self.z / other.z))

    def scale(self, scalar: float):
        if self.z is None:
            return xy2vector((self.x * scalar, self.y * scalar))
        return xyz2vector((self.x * scalar, self.y * scalar, self.z * scalar))


class IntVector(_Vector):
    x: int
    y: int
    z: Optional[int] = None

    @classmethod
    def from_zyx(cls, zyx: Tuple[int, int, int]) -> IntVector:
        return IntVector(z=zyx[0], y=zyx[1], x=zyx[2])

    @classmethod
    def from_xyz(cls, xyz: Tuple[int, int, int]) -> IntVector:
        return IntVector(x=xyz[0], y=xyz[1], z=xyz[2])

    @classmethod
    def from_yx(cls, yx: Tuple[int, int]) -> IntVector:
        return IntVector(y=yx[0], x=yx[1])

    @classmethod
    def from_xy(cls, xy: Tuple[int, int]) -> IntVector:
        return IntVector(x=xy[0], y=xy[1])


class FloatVector(_Vector):
    x: float
    y: float
    z: Optional[float] = None

    def floor(self) -> IntVector:
        if self.z is None:
            return IntVector(x=int(self.x), y=int(self.y))
        return IntVector(x=int(self.x), y=int(self.y), z=int(self.z))

    def round(self) -> IntVector:
        if self.z is None:
            return IntVector(x=int(round(self.x)), y=int(round(self.y)))
        return IntVector(x=int(round(self.x)), y=int(round(self.y)), z=int(round(self.z)))

    @classmethod
    def from_zyx(cls, zyx: Tuple[float, float, float]) -> FloatVector:
        return FloatVector(z=zyx[0], y=zyx[1], x=zyx[2])

    @classmethod
    def from_xyz(cls, xyz: Tuple[float, float, float]) -> FloatVector:
        return FloatVector(x=xyz[0], y=xyz[1], z=xyz[2])

    @classmethod
    def from_yx(cls, yx: Tuple[float, float]) -> FloatVector:
        return FloatVector(y=yx[0], x=yx[1])

    @classmethod
    def from_xy(cls, xy: Tuple[float, float]) -> FloatVector:
        return FloatVector(x=xy[0], y=xy[1])


VectorType = Union[FloatVector, IntVector]


def zyx2vector(zyx: Tuple[Numeric, Numeric, Numeric]) -> VectorType:
    if type(zyx[0]) in [int, np.int_]:
        return IntVector.from_zyx(zyx)
    if type(zyx[0]) in [float, np.float64]:
        return FloatVector.from_zyx(zyx)
    raise TypeError(f"Expected type int or float, got {type(zyx[0])}")


def xyz2vector(xyz: Tuple[Numeric, Numeric, Numeric]) -> VectorType:
    if type(xyz[0]) in [int, np.int_]:
        return IntVector.from_xyz(xyz)
    if type(xyz[0]) in [float, np.float64]:
        return FloatVector.from_xyz(xyz)
    raise TypeError(f"Expected type int or float, got {type(xyz[0])}")


def xy2vector(xy: Tuple[Numeric, Numeric]) -> VectorType:
    if type(xy[0]) in [int, np.int_]:
        return IntVector.from_xy(xy)
    if type(xy[0]) in [float, np.float64]:
        return FloatVector.from_xy(xy)
    raise TypeError(f"Expected type int or float, got {type(xy[0])}")


def yx2vector(yx: Tuple[Numeric, Numeric]) -> VectorType:
    if type(yx[0]) in [int, np.int_]:
        return IntVector.from_yx(yx)
    if type(yx[0]) in [float, np.float64]:
        return FloatVector.from_yx(yx)
    raise TypeError(f"Expected type int or float, got {type(yx[0])}")
