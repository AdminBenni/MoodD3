from __future__ import annotations
import math

from random import random

numeral = int | float


# 3D vector
class Vec:
	def __init__(self, x: numeral = 0, y: numeral = 0, z: numeral = 0):
		self.x: numeral = x
		self.y: numeral = y
		self.z: numeral = z

	def dot(self, other: Vec) -> numeral:  # Dot product
		return self.x * other.x + self.y * other.y + self.z * other.z

	def cross(self, other: Vec) -> Vec:  # Cross product
		return Vec(self.y*other.z - self.z*other.y, self.z*other.x - self.x*other.z, self.x*other.y - self.y*other.x)

	def normalize(self) -> Vec:  # Normalize vector inplace
		self.x, self.y, self.z, = self.normalized()
		return self

	def normalized(self) -> Vec:  # Return normalized version of vector
		return (self / l) if (l := self.len()) != 0 else Vec.zero()

	def len(self) -> numeral:  # Length of vector
		return (self.x**2 + self.y**2 + self.z**2)**0.5

	def dist(self, other: Vec, axes: Vec = None):  # Distance from this vector to another
		return ((other - self) * (Vec.one() if axes is None else axes)).len()

	def angle(self, other=None) -> numeral:  # Angle between this vector and another, default is x axis
		lens = self.len() * (other := Vec.right() if other is None else other).len()
		return math.acos(self.dot(other) / lens) if lens != 0 else math.nan

	def xvec(self, y: numeral = 0, z: numeral = 0) -> Vec:  # Vector with same x and given y and z, default is 0
		return Vec(self.x, y, z)

	def yvec(self, x: numeral = 0, z: numeral = 0) -> Vec:  # Vector with same y and given x and z, default is 0
		return Vec(x, self.y, z)

	def zvec(self, x: numeral = 0, y: numeral = 0) -> Vec:  # Vector with same z and given x and y, default is 0
		return Vec(x, y, self.z)

	def xyvec(self, z: numeral = 0) -> Vec:  # Vector with same x and y and given z, default is 0
		return Vec(self.x, self.y, z)

	def xzvec(self, y: numeral = 0) -> Vec:  # Vector with same x and z and given y, default is 0
		return Vec(self.x, y, self.z)

	def yzvec(self, x: numeral = 0) -> Vec:  # Vector with same y and z and given x, default is 0
		return Vec(x, self.y, self.z)

	@property
	def X(self) -> Vec:  # Shorthand for xvec(0, 0)
		return self.xvec()

	@property
	def Y(self) -> Vec:  # Shorthand for yvec(0, 0)
		return self.yvec()

	@property
	def Z(self) -> Vec:  # Shorthand for zvec(0, 0)
		return self.zvec()

	@property
	def XY(self) -> Vec:  # Shorthand for xyvec(0)
		return self.xyvec()

	@property
	def XZ(self) -> Vec:  # Shorthand for xzvec(0)
		return self.xzvec()

	@property
	def YZ(self) -> Vec:  # Shorthand for yzvec(0)
		return self.yzvec()
	
	def __neg__(self) -> Vec:  # Negate vector
		return Vec(-self.x, -self.y, -self.z)

	# Next 8 methods all perform Vector and Scalar operations
	def __mul__(self, other: Vec | numeral) -> Vec:
		return Vec(self.x * other.x, self.y * other.y, self.z * other.z) if isinstance(other, Vec) else \
			   Vec(self.x * other, self.y * other, self.z * other)

	def __add__(self, other: Vec | numeral) -> Vec:
		return Vec(self.x + other.x, self.y + other.y, self.z + other.z) if isinstance(other, Vec) else \
			   Vec(self.x + other, self.y + other, self.z + other)

	def __sub__(self, other: Vec | numeral) -> Vec:
		return Vec(self.x - other.x, self.y - other.y, self.z - other.z) if isinstance(other, Vec) else \
			   Vec(self.x - other, self.y - other, self.z - other)

	def __truediv__(self, other: Vec | numeral) -> Vec:
		return Vec(self.x / other.x, self.y / other.y, self.z / other.z) if isinstance(other, Vec) else \
			   Vec(self.x / other, self.y / other, self.z / other)

	def __rsub__(self, other: Vec | numeral) -> Vec:
		return Vec(other.x - self.x, other.y - self.y, other.z - self.z) if isinstance(other, Vec) else \
			   Vec(other - self.x, other - self.y, other - self.z)

	def __rtruediv__(self, other: Vec | numeral) -> Vec:
		return Vec(other.x / self.x, other.y / self.y, other.z / self.z) if isinstance(other, Vec) else \
			   Vec(other / self.x, other / self.y, other / self.z)

	def __rmul__(self, other: Vec | numeral) -> Vec:
		return self * other

	def __radd__(self, other: Vec | numeral) -> Vec:
		return self + other

	# These static methods are shorthands for creating a vector
	@staticmethod
	def up() -> Vec: return Vec(0, 1, 0)

	@staticmethod
	def down() -> Vec: return Vec(0, -1, 0)

	@staticmethod
	def left() -> Vec: return Vec(-1, 0, 0)

	@staticmethod
	def right() -> Vec: return Vec(1, 0, 0)

	@staticmethod
	def forth() -> Vec: return Vec(0, 0, 1)

	@staticmethod
	def back() -> Vec: return Vec(0, 0, -1)

	@staticmethod
	def zero() -> Vec: return Vec(0, 0, 0)

	@staticmethod
	def one() -> Vec: return Vec(1, 1, 1)

	@staticmethod
	def neg() -> Vec: return Vec(-1, -1, -1)

	@staticmethod
	def inf() -> Vec: return Vec(math.inf, math.inf, math.inf)

	@staticmethod
	def all(v) -> Vec: return Vec(v, v, v)

	@staticmethod
	def random(min_x: numeral = 0, max_x: numeral = 1, min_y: numeral = 0, max_y: numeral = 1, min_z: numeral = 0, max_z: numeral = 1) -> Vec:
		return Vec(random() * (max_x-min_x) + min_x, random() * (max_y-min_y) + min_y, random() * (max_z-min_z) + min_z)

	def __lt__(self, other: Vec) -> bool:  # Checks if vector is less than another both in x and y axis
		return (*self,) < (*other,)

	def __eq__(self, other: Vec) -> bool:  # Checks if vectors are equal
		return math.isclose(self.x, other.x) and math.isclose(self.y, other.y) and math.isclose(self.z, other.z)

	def __bool__(self) -> bool:  # Checks if vector is zero
		return self != Vec.zero()

	def __iter__(self) -> numeral:  # Allows you to iterate over [x, y, z] and unpack vectors
		yield self.x
		yield self.y
		yield self.z

	def __repr__(self) -> str:  # String representation of vector
		return f"Vec({self.x}, {self.y}, {self.z})"

	__str__: str = __repr__
