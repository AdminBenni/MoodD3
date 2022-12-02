import numpy as np

from Vec import Vec

from math import sin, cos, tan

from game_resources import look


class Matrix:
	def get_matrix(self) -> list[float]: pass  # Defined by subclass


class ModelMatrix(Matrix):
	def __init__(self):
		self.matrix: np.ndarray = None
		self.load_identity()
		self.stack: list[np.ndarray] = []

	def load_identity(self):
		self.matrix = np.identity(4, np.float64)

	def get_matrix(self) -> list[float]:
		return self.matrix.tolist()

	def push_matrix(self):
		self.stack.append(self.matrix.copy())

	def pop_matrix(self):
		self.matrix = self.stack.pop()

	def transform(self, trans: list[int | float]):
		self.matrix = self.matrix.dot(np.ndarray((4, 4), np.float64, np.array([*map(np.float64, trans)])))

	def translate(self, off: Vec):
		self.transform([
			1.0, 0.0, 0.0, off.x,
			0.0, 1.0, 0.0, off.y,
			0.0, 0.0, 1.0, off.z,
			0.0, 0.0, 0.0, 1.0
		])

	def scale(self, scl: Vec):
		self.transform([
			scl.x, 0    , 0      , 0,
			0    , scl.y, 0      , 0,
			0    , 0    , scl.z  , 0,
			0    , 0    , 0      , 1
		])
	
	def rotate(self, rot: Vec):
		self.rotate_x(rot.x)
		self.rotate_y(rot.y)
		self.rotate_z(rot.z)

	def rotate_x(self, a: int | float):
		self.transform([
			1, 0     , 0     , 0,
			0, cos(a),-sin(a), 0,
			0, sin(a), cos(a), 0,
			0, 0     , 0     , 1
		])

	def rotate_y(self, a: int | float):
		self.transform([
			 cos(a), 0, sin(a), 0,
			 0     , 1, 0     , 0,
			-sin(a), 0, cos(a), 0,
			 0     , 0, 0     , 1
		])

	def rotate_z(self, a: int | float):
		self.transform([
			cos(a),-sin(a), 0, 0,
			sin(a), cos(a), 0, 0,
			0     , 0     , 1, 0,
			0     , 0     , 0, 1
		])


class ViewMatrix(Matrix):
	def __init__(self):
		self.eye = Vec()
		self.u = Vec.left()
		self.v = Vec.up()
		self.n = Vec.forth()

	def look(self, eye: Vec, center: Vec, up: Vec):
		self.eye = eye
		self.n, self.u, self.v = look(eye, center, up)

	def slide(self, f: Vec):
		self.eye += self.u * f.x + self.v * f.y + self.n * f.z

	def rotate(self, f: Vec):
		self.pitch(f.x)
		self.yaw(f.y)
		self.roll(f.z)

	def pitch(self, a: int | float):
		self.n, self.v = self.n * (ca:=cos(a)) + self.v * (sa:=sin(a)),  self.n * -sa + self.v * ca

	def yaw(self, a: int | float):
		self.n, self.u = self.n * (ca:=cos(a)) + self.u * (sa:=sin(a)),  self.n * -sa + self.u * ca

	def roll(self, a: int | float):
		self.u, self.v = self.u * (ca:=cos(a)) + self.v * (sa:=sin(a)),  self.u * -sa + self.v * ca

	def get_matrix(self) -> list[float]:
		neg_eye = -self.eye
		return [*self.u, neg_eye.dot(self.u),
				*self.v, neg_eye.dot(self.v),
				*self.n, neg_eye.dot(self.n),
				0, 0, 0, 1]


class ProjectionMatrix(Matrix):
	def __init__(self):
		self.left = -1
		self.right = 1
		self.bottom = -1
		self.top = 1
		self.near = -1
		self.far = 100
		self.is_ortho = True

	def set_orthographic(self, left, right, bottom, top, near, far):
		self.left = left
		self.right = right
		self.bottom = bottom
		self.top = top
		self.near = near
		self.far = far
		self.is_ortho = True

	def set_perspective(self, fov, aspect, near, far):
		self.near = near
		self.far = far
		self.top = near * tan(fov / 2)
		self.bottom = -self.top
		self.right = self.top * aspect
		self.left = -self.right
		self.is_ortho = False

	def get_matrix(self) -> list[float]:
		if self.is_ortho:
			A = 2 / (self.right - self.left)
			B = -(self.right + self.left) / (self.right - self.left)
			C = 2 / (self.top - self.bottom)
			D = -(self.top + self.bottom) / (self.top - self.bottom)
			E = 2 / (self.near - self.far)
			F = (self.near + self.far) / (self.near - self.far)

			return [A,0,0,B,
					0,C,0,D,
					0,0,E,F,
					0,0,0,1]
		else:
			n2 = 2 * self.near
			A = n2 / (self.right - self.left)
			B = (self.right + self.left) / (self.right - self.left)
			C = n2 / (self.top - self.bottom)
			D = (self.top + self.bottom) / (self.top - self.bottom)
			E = -(self.far + self.near) / (self.far - self.near)
			F = -(n2 * self.far) / (self.far - self.near)

			return [
				A, 0, B, 0,
				0, C, D, 0,
				0, 0, E, F,
				0, 0,-1, 0
			]