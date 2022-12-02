from Vec import Vec


class LightingElement:  # Common properties for Lights and Materials
	def __init__(self, diff=None, spec=None, amb=None):
		self.diff = Vec.one() if diff is None else diff
		self.spec = Vec.one() if spec is None else spec
		self.amb = Vec.one() if amb is None else amb

	def __iter__(self):
		yield self.diff
		yield self.spec
		yield self.amb


class Light(LightingElement):  # Positional light
	def __init__(self, diff=None, spec=None, amb=None, pos=None):
		super().__init__(diff, spec, amb)
		self.pos = Vec.zero() if pos is None else pos

	def __iter__(self):  # For iterating and unpacking
		yield self.diff
		yield self.spec
		yield self.amb
		yield self.pos


class Material(LightingElement):  # Material properties of object
	def __init__(self, diff=None, spec=None, amb=None, shine=10):
		super().__init__(diff, spec, amb)
		self.shine = shine

	def __iter__(self):  # For iterating and unpacking
		yield self.diff
		yield self.spec
		yield self.amb
		yield self.shine
