from Matrix import ModelMatrix
from Vec import Vec
from Shader import Shader3D
from game_resources import look


# Encapsulates a game object's coordinate frame
class Coord:
	def __init__(self, model: ModelMatrix, shader: Shader3D, pos: Vec = None, scale: Vec = None, rotation: Vec = None):
		self.model = model
		self.shader = shader
		self.pos = Vec() if pos is None else pos
		self.scalar = Vec.one() if scale is None else scale
		self.rotation = Vec() if rotation is None else rotation
		self.orientation: list[int | float] | None = None

	def apply(self):
		self.model.push_matrix()
		self.model.translate(self.pos)
		if self.orientation is not None:
			self.model.transform(self.orientation)
		self.model.rotate(self.rotation)
		self.model.scale(self.scalar)
		self.shader.set_model_matrix(self.model.get_matrix())

	def unapply(self):
		self.model.pop_matrix()

	def translate(self, direction: Vec):
		self.pos += direction

	def scale(self, scale: Vec):
		self.scalar += scale

	def rotate(self, rotation: Vec):
		self.rotation += rotation

	def look(self, target: Vec, up: Vec = None):
		c, a, b = look(self.pos, target, Vec.up() if up is None else up)
		self.orientation = [
			a.x, b.x, c.x, 0.0,
			a.y, b.y, c.y, 0.0,
			a.z, b.z, c.z, 0.0,
			0.0, 0.0, 0.0, 1.0
		]
		self.rotation = Vec()
		return c, a, b
