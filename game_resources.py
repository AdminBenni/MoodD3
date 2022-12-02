import math

from Vec import Vec


def look(origin: Vec, target: Vec, up: Vec):
	"""
		self.eye: Vec = eye
		self.n: Vec = eye - center			c: Vec = self.pos - target
		self.u: Vec = up.cross(self.n)		a: Vec = up.cross(c)
		self.n.normalize()					c.normalize()
		self.u.normalize()					a.normalize()
		self.v: Vec = self.n.cross(self.u)	b: Vec = c.cross(a)
	"""
	n: Vec = origin - target
	u: Vec = up.cross(n)
	v: Vec = n.normalize().cross(u.normalize())
	return n, u, v


def bezier(p1, p2, p3, p4, tmn, tmx):  # 4 point bezier curve
	return lambda ct: (t := (ct - tmn) / (tmx - tmn)) ** 3 * p4 + 3 * (pm := 1 - t) * t ** 2 * p3 + 3 * pm ** 2 * t * p2 + pm ** 3 * p1


def clamp(x, mn, mx):  # Clamps value to given range
	return max(mn, min(x, mx))


# Linearly interpolates range
def lerpr(x, in_min, in_max, out_min, out_max): # Maps a from given input interval to given output interval
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def project(p, l):  # Projects point p onto line l
	return l * (p.dot(l) / l.dot(l))


def in_range(p, l1, l2):  # Checks if point p is in range l1, l2
	if not math.isclose(l1.x, l2.x):
		return l1.x >= p.x >= l2.x or l1.x <= p.x <= l2.x
	return l1.y >= p.y >= l2.y or l1.y <= p.y <= l2.y


def ray(vec_pos: Vec, vec: Vec, line_pos: Vec, line: Vec, line2: Vec) -> bool:  # Probably doesn't work
	perp_line = line.cross(line2)
	if (perp_dot_vec := perp_line.dot(vec)) != 0:
		hit_time = perp_line.dot(line_pos - vec_pos) / perp_dot_vec
		hit_point = vec_pos + vec * hit_time
		print(hit_time)
		return in_range(hit_point, line_pos, line_pos + line)
