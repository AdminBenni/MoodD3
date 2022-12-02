from OpenGL.GL import *

from Vec import Vec


class ShaderError(Exception): pass


class Shader3D:
	def __init__(self):
		vert_shader = glCreateShader(GL_VERTEX_SHADER)
		with open("simple3D.vert") as shader_file:
			glShaderSource(vert_shader, shader_file.read())
		glCompileShader(vert_shader)
		if glGetShaderiv(vert_shader, GL_COMPILE_STATUS) != 1:  # shader didn't compile
			print("Couldn't compile vertex shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(vert_shader)))

		frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
		with open("simple3D.frag") as shader_file:
			glShaderSource(frag_shader, shader_file.read())
		glCompileShader(frag_shader)
		if glGetShaderiv(frag_shader, GL_COMPILE_STATUS) != 1:  # shader didn't compile
			print("Couldn't compile fragment shader\nShader compilation Log:\n" + str(glGetShaderInfoLog(frag_shader)))

		self.program_id = glCreateProgram()
		glAttachShader(self.program_id, vert_shader)
		glAttachShader(self.program_id, frag_shader)
		glLinkProgram(self.program_id)

		self.pos_loc = glGetAttribLocation(self.program_id, "a_position")
		glEnableVertexAttribArray(self.pos_loc)

		self.norm_loc = glGetAttribLocation(self.program_id, "a_normal")
		glEnableVertexAttribArray(self.norm_loc)

		self.uv_loc = glGetAttribLocation(self.program_id, "a_uv")
		glEnableVertexAttribArray(self.uv_loc)

		self.light_pos_loc = [glGetUniformLocation(self.program_id, f"u_light_position[{x}]") for x in range(8)]
		self.cam_pos_loc = glGetUniformLocation(self.program_id, "u_camera_position")

		self.locs = {  # Generates locations for light and material variables
			"light": {mb: [glGetUniformLocation(self.program_id, f"light[{x}].{mb}") for x in range(8)] for mb in ["diffuse", "specular", "ambience"]},
			"material": {mb: glGetUniformLocation(self.program_id, f"material.{mb}") for mb in ["diffuse", "specular", "ambience", "shininess"]}
		}
		self.model_matrix_loc = glGetUniformLocation(self.program_id, "u_model_matrix")
		self.view_matrix_loc = glGetUniformLocation(self.program_id, "u_view_matrix")
		self.proj_matrix_loc = glGetUniformLocation(self.program_id, "u_projection_matrix")
		self.diff_tex_loc = glGetUniformLocation(self.program_id, "tex01")

		self.fog_start_loc = glGetUniformLocation(self.program_id, "u_fog_start")
		self.fog_end_loc = glGetUniformLocation(self.program_id, "u_fog_end")
		self.fog_color_loc = glGetUniformLocation(self.program_id, "u_fog_color")

	def use(self):
		try: glUseProgram(self.program_id)   
		except OpenGL.error.GLError as e:
			raise ShaderError(f"{e}\n{glGetProgramInfoLog(self.program_id)}")

	def set_model_matrix(self, matrix_array):
		glUniformMatrix4fv(self.model_matrix_loc, 1, True, matrix_array)

	def set_projection_matrix(self, matrix_array):
		glUniformMatrix4fv(self.proj_matrix_loc, 1, True, matrix_array)

	def set_view_matrix(self, matrix_array):
		glUniformMatrix4fv(self.view_matrix_loc, 1, True, matrix_array)

	def set_position_attribute(self, vertex_array):
		glVertexAttribPointer(self.pos_loc, 3, GL_FLOAT, False, 0, vertex_array)

	def set_normal_attribute(self, vertex_array):
		glVertexAttribPointer(self.norm_loc, 3, GL_FLOAT, False, 0, vertex_array)

	def set_uv_attribute(self, vertex_array):
		glVertexAttribPointer(self.uv_loc, 2, GL_FLOAT, False, 0, vertex_array)

	def set_diffuse_texture(self, tex):
		glUniform1f(self.diff_tex_loc, tex)

	def set_material(self, diff, spec, amb, shine):
		self.set_material_diffuse(diff)
		self.set_material_specular(spec)
		self.set_material_ambience(amb)
		self.set_shininess(shine)

	def set_light(self, diff, spec, amb, pos, ind=0):
		self.set_light_diffuse(diff, ind)
		self.set_light_specular(spec, ind)
		self.set_light_ambience(amb, ind)
		self.set_light_position(pos, ind)

	def set_material_diffuse(self, diff):
		glUniform4f(self.locs["material"]["diffuse"], *diff, 1.0)

	def set_light_position(self, pos, ind=0):
		glUniform4f(self.light_pos_loc[ind], *pos, 1.0)

	def set_light_diffuse(self, diff, ind=0):
		glUniform4f(self.locs["light"]["diffuse"][ind], *diff, 1.0)

	def set_camera_position(self, pos):
		glUniform4f(self.cam_pos_loc, *pos, 1.0)

	def set_light_specular(self, spec, ind=0):
		glUniform4f(self.locs["light"]["specular"][ind], *spec, 1.0)

	def set_material_specular(self, spec):
		glUniform4f(self.locs["material"]["specular"], *spec, 1.0)

	def set_shininess(self, shine):
		glUniform1f(self.locs["material"]["shininess"], shine)

	def set_light_ambience(self, amb, ind=0):
		glUniform4f(self.locs["light"]["ambience"][ind], *amb, 1.0)

	def set_material_ambience(self, amb):
		glUniform4f(self.locs["material"]["ambience"], *amb, 1.0)

	def set_fog(self, color: Vec, start: float, end: float):
		glUniform4f(self.fog_color_loc, *color, 1)
		glUniform1f(self.fog_start_loc, start)
		glUniform1f(self.fog_end_loc, end)
