attribute vec3 a_position;
attribute vec3 a_normal;
attribute vec2 a_uv;

uniform vec4 u_light_position[8];
uniform vec4 u_camera_position;
uniform mat4 u_model_matrix;
uniform mat4 u_projection_matrix;
uniform mat4 u_view_matrix;

varying vec4 normal;
varying vec4 s[8];
varying vec4 h[8];
varying vec4 v;
varying vec2 v_uv;

void main(void)
{
    v_uv = a_uv;
	vec4 position = u_model_matrix * vec4(a_position.x, a_position.y, a_position.z, 1);
	normal = u_model_matrix * vec4(a_normal.x, a_normal.y, a_normal.z, 0);

	v = u_camera_position - position;
	for(int i = 0; i < 8; i++) {
		s[i] = u_light_position[i] - position;
		h[i] = s[i] + v;
	}

	gl_Position = u_projection_matrix * (u_view_matrix * position);
}