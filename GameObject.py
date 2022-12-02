from OpenGL.GL import *

from Lighting import Material

from Coord import Coord

from Matrix import ModelMatrix

from Shader import Shader3D

from Vec import Vec

import numpy as np

import json


# Stores information needed to store, move, animate, and draw game objects
class GameObject:
	def __init__(self, model: ModelMatrix, shader: Shader3D, pos=None, scale=None, rotation=None, material=None, tiling=(1,1)):
		self.coord = Coord(model, shader, pos, scale, rotation)
		self.material = Material() if material is None else material
		self.tiling = tiling

	def points(self):  # Points of object, defined by subclass
		pass

	def normals(self):  # Normals of object, defined by subclass
		pass

	def uv(self): # UV coordinates of object's texture, defined by subclass
		pass

	def steps(self):  # How many points per face of object, defined by subclass
		pass

	# Passes object positions and normals to shader
	def set(self):
		self.coord.shader.set_position_attribute(self.points())
		self.coord.shader.set_normal_attribute(self.normals())
		uv = np.array(self.uv())
		uv[::2] *= self.tiling[0]
		uv[1::2] *= self.tiling[1]
		self.coord.shader.set_uv_attribute(uv)

	# Draws with push pop
	def draw(self):
		self.coord.apply()
		self.raw_draw()
		self.coord.unapply()

	# Sets before drawing
	def draw_set(self):
		self.set()
		self.draw()

	# Draws object from its points and with its color
	def raw_draw(self):
		self.coord.shader.set_material(*self.material)

		end, step = len(self.points()) // 3, self.steps()
		for x in range(0, end, step):
			glDrawArrays(GL_TRIANGLE_FAN, x, step)


class Sprite(GameObject):  # Collection of rectangles ;)
	def __init__(self, model: ModelMatrix, shader: Shader3D, pos=None, scale=None, rotation=None, material=None, tiling=(1,1)):
		super().__init__(model, shader, pos, scale, rotation, material, tiling)
		self.__points = [
			-0.5, -0.5, -0.5, -0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5, -0.5, -0.5,
			-0.5, -0.5, 0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.5, 0.5,
			-0.5, -0.5, -0.5, 0.5, -0.5, -0.5, 0.5, -0.5, 0.5, -0.5, -0.5, 0.5,
			-0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5, 0.5, 0.5, -0.5, 0.5, 0.5,
			-0.5, -0.5, -0.5, -0.5, -0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5, -0.5,
			0.5, -0.5, -0.5, 0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.5]

		self.__normals = [
			0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0,
			0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
			0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0,
			0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0,
			-1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0,
			1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

		# Doesn't do much now but this helped when working with sprite atlases / sheets
		self.__frames = {
			"idle": [
				1.0, 1.0,
				1.0, 0.0,
				0.0, 0.0,
				0.0, 1.0,
			]
		}

		self.frame = "idle"

		self.__rest = [0.0] * 48

		self.__steps = 4

	def points(self):
		return self.__points

	def normals(self):
		return self.__normals

	def uv(self):
		return self.__frames[self.frame] + self.__rest

	def steps(self):
		return self.__steps


class Cube(GameObject):  # Collection of rectangles ;)
	def __init__(self, model: ModelMatrix, shader: Shader3D, pos=None, scale=None, rotation=None, material=None, tiling=(1,1)):
		super().__init__(model, shader, pos, scale, rotation, material, tiling)
		self.__points = [
			-0.5, -0.5, -0.5, -0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5, -0.5, -0.5,
			-0.5, -0.5, 0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.5, 0.5,
			-0.5, -0.5, -0.5, 0.5, -0.5, -0.5, 0.5, -0.5, 0.5, -0.5, -0.5, 0.5,
			-0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5, 0.5, 0.5, -0.5, 0.5, 0.5,
			-0.5, -0.5, -0.5, -0.5, -0.5, 0.5, -0.5, 0.5, 0.5, -0.5, 0.5, -0.5,
			0.5, -0.5, -0.5, 0.5, -0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, -0.5]

		self.__normals = [
			0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0,
			0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
			0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0,
			0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0,
			-1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0,
			1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

		self.__uv = [
			1.0, 1.0,
			1.0, 0.0,
			0.0, 0.0,
			0.0, 1.0,

			1.0, 1.0,
			1.0, 0.0,
			0.0, 0.0,
			0.0, 1.0,

			1.0, 0.0,
			0.0, 0.0,
			0.0, 1.0,
			1.0, 1.0,

			1.0, 0.0,
			0.0, 0.0,
			0.0, 1.0,
			1.0, 1.0,

			1.0, 1.0,
			0.0, 1.0,
			0.0, 0.0,
			1.0, 0.0,

			1.0, 1.0,
			0.0, 1.0,
			0.0, 0.0,
			1.0, 0.0
		]

		self.__steps = 4

	def points(self):
		return self.__points

	def normals(self):
		return self.__normals

	def uv(self):
		return self.__uv

	def steps(self):
		return self.__steps


# Loads a model from file to be drawn
class Mesh(GameObject):
	def __init__(self, model: ModelMatrix, shader: Shader3D, filename: str, pos=None, scale=None, rotation=None, material=None, tiling=(1,1)):
		super().__init__(model, shader, pos, scale, rotation, material, tiling)
		with open(filename) as f:  # Assuming file type .g3dj
			self.__file = json.load(f)
		materials = {
			m["id"]: Material(
				Vec(*m["diffuse"]), Vec(*m["specular"]), Vec(*m["ambient"]), m["shininess"]
			) for m in self.__file["materials"]
		}
		meshes = {  # Assuming type triangles
			mesh["parts"][0]["id"]: {  # Assuming attributes ["POSITION", "NORMAL", "TEXCOORD0"]
				"vertices": [v for i in range(0, len(mesh["vertices"]), 8) for v in mesh["vertices"][i:i+3]],
				"normals":  [v for i in range(3, len(mesh["vertices"]), 8) for v in mesh["vertices"][i:i+3]],
				"uv":       [v for i in range(6, len(mesh["vertices"]), 8) for v in mesh["vertices"][i:i+2]],
				"indices": mesh["parts"][0]["indices"]
			} for mesh in self.__file["meshes"]
		}
		self.__nodes = [{
			"coord": Coord(
				model, shader,
				Vec(*node["translation"]) if "translation" in node else Vec(),
				Vec(*node["scale"]) if "scale" in node else Vec(),
				Vec(),  # Quaternion rotation conversion out of scope but would go here
			),
			"material": materials[node["parts"][0]["materialid"]] if "materialid" in node["parts"][0] else Material(),
			"mesh": meshes[node["parts"][0]["meshpartid"]]
		} for node in self.__file["nodes"]]

	# Passes object positions and normals to shader
	def set(self):
		pass

	def draw_set(self):
		self.draw()

	def __set(self, node):
		self.coord.shader.set_position_attribute(node["mesh"]["vertices"])
		self.coord.shader.set_normal_attribute(node["mesh"]["normals"])
		uv = np.array(node["mesh"]["uv"])
		uv[::2] *= self.tiling[0]
		uv[1::2] *= self.tiling[1]
		self.coord.shader.set_uv_attribute(uv)

	# Draws object from its points and with its color
	def raw_draw(self):
		for node in self.__nodes:
			node["coord"].apply()
			self.coord.shader.set_material(*node["material"])
			self.__set(node)
			glDrawElements(GL_TRIANGLES, len(node["mesh"]["indices"]), GL_UNSIGNED_SHORT, node["mesh"]["indices"])
			node["coord"].unapply()


class ShapeTree:  # Object hierarchy
	def __init__(self, model: ModelMatrix, shader: Shader3D, pos=None, rot=None, children=None):
		self.coord = Coord(model, shader, pos, rotation=rot)
		self.children = [] if children is None else children

	def draw(self):
		self.coord.apply()

		for child in self.children:
			child.draw()

		self.coord.unapply()
