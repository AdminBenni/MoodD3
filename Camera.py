from Matrix import ViewMatrix, ProjectionMatrix
from Shader import Shader3D
from Vec import Vec, numeral


# Used to have ideal getter / setter for camera pos property
class VecWrapper(Vec):
	def __init__(self, v: ViewMatrix, shader: Shader3D):
		self.v = v
		self.shader: Shader3D = shader

	@property
	def x(self) -> numeral:
		return self.v.eye.x

	@property
	def y(self) -> numeral:
		return self.v.eye.y

	@property
	def z(self) -> numeral:
		return self.v.eye.z

	@x.setter
	def x(self, other: numeral):
		self.v.eye.x = other
		self.shader.set_view_matrix(self.v.get_matrix())

	@y.setter
	def y(self, other: numeral):
		self.v.eye.y = other
		self.shader.set_view_matrix(self.v.get_matrix())

	@z.setter
	def z(self, other: numeral):
		self.v.eye.z = other
		self.shader.set_view_matrix(self.v.get_matrix())


# Encapsulates view and projection matrix
class Camera:
	def __init__(self, shader: Shader3D):
		self.view = ViewMatrix()
		self.projection = ProjectionMatrix()
		self.shader = shader
		self.shader.set_view_matrix(self.view.get_matrix())
		self.shader.set_projection_matrix(self.projection.get_matrix())
		self.shader.set_fog(Vec(0.2, 0.2, 0.2), 10, 30)

	@property
	def pos(self):
		return VecWrapper(self.view, self.shader)

	@pos.setter
	def pos(self, vec: Vec):
		assert isinstance(vec, Vec), "Camera position must be of type Vec"
		self.view.eye = vec
		self.shader.set_view_matrix(self.view.get_matrix())
		self.shader.set_camera_position(self.view.eye)

	def look(self, target: Vec, up: Vec = None):
		self.view.look(self.view.eye, target, Vec.up() if up is None else up)
		self.shader.set_view_matrix(self.view.get_matrix())

	def slide(self, axis: Vec):
		self.view.slide(axis)
		self.shader.set_view_matrix(self.view.get_matrix())
		self.shader.set_camera_position(self.view.eye)

	def rotate(self, angles: Vec):
		self.view.rotate(angles)
		self.shader.set_view_matrix(self.view.get_matrix())

	def set_orthographic(self, left, right, bottom, top, near, far):
		self.projection.set_orthographic(left, right, bottom, top, near, far)
		self.shader.set_projection_matrix(self.projection.get_matrix())

	def set_perspective(self, fov, aspect, near, far):
		self.projection.set_perspective(fov, aspect, near, far)
		self.shader.set_projection_matrix(self.projection.get_matrix())
