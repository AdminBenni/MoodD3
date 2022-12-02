struct Light {
	vec4 diffuse;
	vec4 specular;
	vec4 ambience;
};

struct Material {
	float shininess;
	vec4 diffuse;
	vec4 specular;
	vec4 ambience;
};

uniform sampler2D u_tex01;

uniform Light light[8];
uniform Material material;

uniform float u_fog_start;
uniform float u_fog_end;
uniform vec4 u_fog_color;

varying vec4 normal;
varying vec4 s[8];
varying vec4 h[8];
varying vec4 v;
varying vec2 v_uv;

void main(void)
{
    vec4 tex_col = texture2D(u_tex01, v_uv);
	vec4 mat_amb = material.ambience * tex_col;
	vec4 mat_diff = material.diffuse * tex_col;
	vec4 color = vec4(0.0);
	for(int i = 0; i < 8; i++) {
		float lambert = max(0, dot(normal, s[i])/(length(normal) * length(s[i]))) * max(1, 2/length(s[i]));
		float phong = max(0, dot(h[i], normal)/(length(normal) * length(h[i])));
		color += lambert * light[i].diffuse * mat_diff + pow(phong, material.shininess) * light[i].specular * material.specular + light[i].ambience * mat_amb;
	}

	gl_FragColor = mix(color, u_fog_color, clamp((length(v) - u_fog_start)/(u_fog_end - u_fog_start), 0, 1));
	gl_FragColor.a = mat_amb.a;
}