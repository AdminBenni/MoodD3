from GameHandler import GenericGameHandler

from Shader import Shader3D

from Matrix import ModelMatrix

from Lighting import Light, Material

from GameObject import Cube, Sprite, Mesh

from Vec import Vec

from OpenGL.GL import *

import pygame as pg

from math import pi

from Camera import Camera

from Timer import Timer

from random import choice


class GameHandler(GenericGameHandler):
	def __init__(self, x_bounds, y_bounds, desired_fps, bg_color=(0.2, 0.2, 0.2, 1.0)):
		super().__init__(x_bounds, y_bounds, desired_fps, bg_color)

		# GAME LOGIC VARIABLES
		self.muzzle_timer = Timer(0)
		self.muzzle_time = 75
		self.shot = False

		self.hit_margin = 0.1  # How accurate you have to be to hit shots, lower = more accurate

		self.mov_spd = 4
		self.rot_spd = 3.5
		self.mov_vec = Vec.zero()
		self.rot_vec = Vec.zero()
		self.radius = 0.2  # Radius for collision

		self.max_hp = 100
		self.max_ammo = 20
		self.max_clip = 5
		self.hp = self.max_hp
		self.ammo = self.max_ammo
		self.clip = self.max_clip

		# How many milliseconds between damage
		self.hp_drain_timer = Timer(0)
		self.hp_drain_time = 325

		self.enemy_speed = 1.5
		self.enemy_detection_radius = 10
		self.enemy_state_update_time = 200
		self.enemy_state_update_timer = Timer(self.enemy_state_update_time)

		# SHADER, MODEL, CAMERA (VIEW, PROJECTION)
		self.shader = Shader3D()
		self.shader.use()

		self.model = ModelMatrix()

		self.camera = Camera(self.shader)  # This will be our main player controller

		self.camera.set_perspective(45, x_bounds / y_bounds, 0.142, 100)
		self.camera.pos = Vec(-20.5, 0.5, 11.5)
		self.camera.look(Vec(0, 0.5, -1))

		# LIGHTS
		self.lights = (
			Light(Vec(0, 0, 0.25), Vec(), Vec(0, 0, 0.25), Vec(-14.5, 0.5, 5.75)),
			Light(Vec(0, 0.25, 0), Vec(), Vec(0, 0.25, 0), Vec(1.75, 0.5, 6.5)),
			Light(Vec(0.5, 0, 0), Vec(), Vec(0.25, 0, 0), Vec(18.75, 0.5, 7.5)),
			Light(Vec(0, 0.25, 0.25), Vec(), Vec(0, 0.5, 0.5), Vec(25, 0.5, -5)),
			Light(Vec(0.35), Vec(), Vec.zero(), Vec(22.5, 0.5, -19.5)),
			Light(Vec(0.35), Vec(), Vec.zero(), Vec(4.5, 0.5, -1.5)),
			Light(Vec(0.35), Vec(), Vec.zero(), Vec(-14.5, 0.5, -6)),
		)

		# Pass lights to shader
		for ind, light in enumerate(self.lights):
			self.shader.set_light(*light, ind)

		self.gun_flash = Light(Vec(), Vec(), Vec())  # Light which follows the gun and is only active when firing

		# GAME OBJECTS

		# Floor & ceiling
		floor_mat = Material(Vec.one(), Vec.one(), Vec.all(0.3), 50)
		ceiling_mat = Material(Vec.one(), Vec.one(), Vec.all(0.025))
		self.floor = Cube(self.model, self.shader, Vec(5, -0.05, 5), Vec(100, 0.1, 100), material=floor_mat, tiling=(32, 32))
		self.ceiling = Cube(self.model, self.shader, Vec(5, 1.55, 5), Vec(100, 0.1, 100), material=ceiling_mat, tiling=(16, 16))

		self.enemies = [
			Sprite(self.model, self.shader, Vec(-4.5, 1.468/4, 3.5), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(7, 1.468/4, 8), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(3, 1.468/4, 3.5), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(19.5, 1.468/4, 9.5), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(18, 1.468/4, -11.75), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(15.25, 1.468/4, -23.75), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(26.75, 1.468/4, -21.5), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(21, 1.468/4, -23.75), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(-7.75, 1.468/4, 2.5), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(-10, 1.468/4, 4.5), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(-20.5, 1.468/4, 4), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(-20.5, 1.468/4, -11), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(-11, 1.468/4, -11.5), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(-8.5, 1.468/4, -9), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(-11, 1.468/4, -9.25), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(-16.5, 1.468/4, -3.25), Vec(1/2, 1.468/2, 1/2)),
			Sprite(self.model, self.shader, Vec(-18.25, 1.468/4, -0.25), Vec(1/2, 1.468/2, 1/2)),
		]

		self.enemy_states = ["idle"] * len(self.enemies)

		self.walls = [
			Cube(self.model, self.shader, Vec(3, 1.5/2, 12), Vec(32*1.5, 1.5, 0.1), tiling=(32,1)),
			Cube(self.model, self.shader, Vec(18*1.5, 1.5/2, 12-24*1.5/2), Vec(0.1, 1.5, 24*1.5), tiling=(24,1)),
			Cube(self.model, self.shader, Vec(-14*1.5, 1.5/2, 12-16*1.5/2), Vec(0.1, 1.5, 16*1.5), tiling=(16,1)),
			Cube(self.model, self.shader, Vec(-14.25, 1.5 / 2, 5), Vec(9 * 1.5, 1.5, 0.1), tiling=(9, 1)),
			Cube(self.model, self.shader, Vec(-14.25, 1.5 / 2, -12), Vec(9 * 1.5, 1.5, 0.1), tiling=(9, 1)),
			Cube(self.model, self.shader, Vec(-9.5 * 1.5, 1.5 / 2, 12 - 3 * 1.5 / 2), Vec(0.1, 1.5, 3 * 1.5), tiling=(3, 1)),
			Cube(self.model, self.shader, Vec(-5 * 1.5, 1.5 / 2, 9.5 - 6 * 1.5 / 2), Vec(0.1, 1.5, 6 * 1.5), tiling=(6, 1)),
			Cube(self.model, self.shader, Vec(-5 * 1.5, 1.5 / 2, -10 * 1.5 / 2), Vec(0.1, 1.5, 6 * 1.5), tiling=(6, 1)),
			Cube(self.model, self.shader, Vec(-1 * 1.5, 1.5 / 2, 6 * 1.5 / 2), Vec(0.1, 1.5, 2 * 1.5), tiling=(2, 1)),
			Cube(self.model, self.shader, Vec(3 * 1.5, 1.5 / 2, 12 * 1.5 / 2), Vec(0.1, 1.5, 2 * 1.5), tiling=(2, 1)),
			Cube(self.model, self.shader, Vec(5 * 1.5, 1.5 / 2, 8 * 1.5 / 2), Vec(2 * 1.5, 1.5, 0.1), tiling=(2, 1)),
			Cube(self.model, self.shader, Vec(-3 * 1.5, 1.5 / 2, 10 * 1.5 / 2), Vec(2 * 1.5, 1.5, 0.1), tiling=(2, 1)),
			Cube(self.model, self.shader, Vec(11.5 * 1.5, 1.5 / 2, -22.5 * 1.5 / 2), Vec(3 * 1.5, 1.5, 0.1), tiling=(3, 1)),
			Cube(self.model, self.shader, Vec(17.5 * 1.5, 1.5 / 2, -25 * 1.5 / 2), Vec(1 * 1.5, 1.5, 0.1), tiling=(1, 1)),
			Cube(self.model, self.shader, Vec(15 * 1.5, 1.5 / 2, -31 * 1.5 / 2), Vec(0.1, 1.5, 1 * 1.5), tiling=(1, 1)),
			Cube(self.model, self.shader, Vec(7 * 1.5, 1.5 / 2, 12 - 6 * 1.5 / 2), Vec(0.1, 1.5, 6 * 1.5), tiling=(6, 1)),
			Cube(self.model, self.shader, Vec(8.25, 1.5 / 2, 0.5), Vec(21 * 1.5, 1.5, 0.1), tiling=(21, 1)),
			Cube(self.model, self.shader, Vec(16 * 1.5, 1.5 / 2, 9.5 - 6 * 1.5 / 2), Vec(0.1, 1.5, 6 * 1.5), tiling=(6, 1)),
			Cube(self.model, self.shader, Vec(21, 1.5 / 2, -24), Vec(8 * 1.5, 1.5, 0.1), tiling=(8, 1)),
			Cube(self.model, self.shader, Vec(22.1, 1.5 / 2, -12), Vec(6.5 * 1.5, 1.5, 0.1), tiling=(6.5, 1)),
			Cube(self.model, self.shader, Vec(17.25, 1.5 / 2, -7.5), Vec(0.1, 1.5, 6 * 1.5), tiling=(6, 1)),
			Cube(self.model, self.shader, Vec(15, 1.5 / 2, -13.5), Vec(0.1, 1.5, 14 * 1.5), tiling=(14, 1)),
			Cube(self.model, self.shader, Vec(20.6, 1.5 / 2, -3), Vec(4.5 * 1.5, 1.5, 0.1), tiling=(4.5, 1)),
			Cube(self.model, self.shader, Vec(3.75, 1.5 / 2, -3), Vec(15.0625 * 1.5, 1.5, 0.1), tiling=(15.0625, 1)),
		]

		self.keycards = {
			"red": Sprite(self.model, self.shader, Vec(26, 0.2 / 2, -23), Vec.all(0.2)),
			"blue": Sprite(self.model, self.shader, Vec(-8, 0.2 / 2, 4.5), Vec.all(0.2)),
			"yellow": Sprite(self.model, self.shader, Vec(-8, 0.2 / 2, -11.5), Vec.all(0.2)),
		}

		self.ammoboxes = [
			Sprite(self.model, self.shader, Vec(26, 0.1, -11), Vec(0.2 * 1.75, 0.2, 0.2)),
			Sprite(self.model, self.shader, Vec(18, 0.1, -7), Vec(0.2 * 1.75, 0.2, 0.2)),
		]

		self.medkits = [
			Sprite(self.model, self.shader, Vec(18, 0.1, -11), Vec(0.2 * 2.315, 0.2, 0.2))
		]

		self.door = Cube(self.model, self.shader, Vec(-20.9, 1.5 / 2, -1.25), Vec(0.1, 1.5, 1.5))

		self.gun = Sprite(self.model, self.shader, Vec(), Vec.all(0.2))

		self.muzzle = Sprite(self.model, self.shader, Vec(), Vec.all(0.2))

		self.doom_logo = Mesh(self.model, self.shader, "models/doomtext.g3dj", Vec(-14.5, 0.5, 5.1), Vec(0.005, 0.005, 0.0025), tiling=(3,2))

		# TEXTURES
		self.default_tex = self.load_texture("textures/default.png")
		self.wall_tex = self.load_texture("textures/BROWN96.png")
		self.floor_tex = self.load_texture("textures/STONE2.png")
		self.ceiling_tex = self.load_texture("textures/SKIN2.png")
		self.door_tex = self.load_texture("textures/DOOR3.png")
		self.gun_tex = self.load_texture("textures/Pistol.png")
		self.muzzle_tex = self.load_texture("textures/Muzzle.png")
		self.ammobox_tex = self.load_texture("textures/ammo.png")
		self.medkit_tex = self.load_texture("textures/medkit.png")

		self.keycard_tex = {
			"red": self.load_texture("textures/KeycardRed.png"),
			"blue": self.load_texture("textures/KeycardBlue.png"),
			"yellow": self.load_texture("textures/KeycardYellow.png")
		}

		self.enemy_state_tex = {
			"idle": self.load_texture("textures/impidle.png"),
			"walk0": self.load_texture("textures/impwalk0.png"),
			"walk1": self.load_texture("textures/impwalk1.png"),
			"walk2": self.load_texture("textures/impwalk2.png"),
			"attack": self.load_texture("textures/impattack.png"),
		}

		# MUSIC & SFX
		pg.mixer.music.load("sounds/doomE1M1.wav")
		pg.mixer.music.play(-1)
		pg.mixer.music.set_volume(0.1)

		self.pistol_sfx = pg.mixer.Sound("sounds/pistol.wav")
		self.pistol_click_sfx = pg.mixer.Sound("sounds/pistol_click.wav")
		self.pistol_reload_sfx = pg.mixer.Sound("sounds/pistol_reload.wav")
		self.pistol_sfx.set_volume(0.5)
		self.pistol_click_sfx.set_volume(0.5)
		self.pistol_reload_sfx.set_volume(0.5)

		self.pickup_sfx = pg.mixer.Sound("sounds/pickup.wav")
		self.pickup_sfx.set_volume(0.5)

		self.oof_sfx = pg.mixer.Sound("sounds/oof.wav")
		self.oof_sfx.set_volume(0.5)

		self.death1_sfx = pg.mixer.Sound("sounds/impdeath1.wav")
		self.death2_sfx = pg.mixer.Sound("sounds/impdeath2.wav")
		self.death1_sfx.set_volume(0.5)
		self.death2_sfx.set_volume(0.5)

	def load_texture(self, path_string: str = "textures/default.png"):
		surface = pg.image.load(path_string)
		tex_string = pg.image.tostring(surface, "RGBA", False)
		width = surface.get_width()
		height = surface.get_height()
		tex_id = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, tex_id)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_string)
		return tex_id

	def render_text(self, text: str, position: Vec, color: Vec, size: int, font_file: str = "fonts/DoomLeft.ttf"):
		font = pg.font.Font(font_file, size)
		text_surface = font.render(text, True, (*color,))
		text_data = pg.image.tostring(text_surface, "RGBA", True)
		glWindowPos2i(position.x, position.y)
		glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

	def collide_objects(self, old_pos, new_pos, pos, objects):
		for ob in objects:
			if ob.coord.pos.x - ob.coord.scalar.x/2 - self.radius < old_pos.x < ob.coord.pos.x + ob.coord.scalar.x/2 + self.radius:
				if old_pos.z + self.radius <= ob.coord.pos.z - ob.coord.scalar.z / 2:
					if not (new_pos.z + self.radius <= ob.coord.pos.z - ob.coord.scalar.z / 2):
						pos.z = ob.coord.pos.z - ob.coord.scalar.z / 2 - self.radius
				elif old_pos.z - self.radius >= ob.coord.pos.z + ob.coord.scalar.z / 2:
					if not (new_pos.z - self.radius >= ob.coord.pos.z + ob.coord.scalar.z / 2):
						pos.z = ob.coord.pos.z + ob.coord.scalar.z / 2 + self.radius
				else:
					if old_pos.z < ob.coord.pos.z:
						pos.z = ob.coord.pos.z - ob.coord.scalar.z / 2 - self.radius
					else:
						pos.z = ob.coord.pos.z + ob.coord.scalar.z / 2 + self.radius
			elif ob.coord.pos.z - ob.coord.scalar.z/2 - self.radius < old_pos.z < ob.coord.pos.z + ob.coord.scalar.z/2 + self.radius:
				if old_pos.x + self.radius <= ob.coord.pos.x - ob.coord.scalar.x / 2:
					if not (new_pos.x + self.radius <= ob.coord.pos.x - ob.coord.scalar.x / 2):
						pos.x = ob.coord.pos.x - ob.coord.scalar.x / 2 - self.radius
				elif old_pos.x - self.radius >= ob.coord.pos.x + ob.coord.scalar.x / 2:
					if not (new_pos.x - self.radius >= ob.coord.pos.x + ob.coord.scalar.x / 2):
						pos.x = ob.coord.pos.x + ob.coord.scalar.x / 2 + self.radius
				else:
					if old_pos.x < ob.coord.pos.x:
						pos.x = ob.coord.pos.x - ob.coord.scalar.x / 2 - self.radius
					else:
						pos.x = ob.coord.pos.x + ob.coord.scalar.x / 2 + self.radius

	def update(self):
		old_pos = self.camera.view.eye
		self.camera.rotate(self.rot_vec * self.rot_spd * self.delta_time)
		self.camera.slide(self.mov_vec * self.mov_spd * self.delta_time)
		new_pos = self.camera.view.eye

		self.collide_objects(old_pos, new_pos, self.camera.pos, self.walls)  # Collide player with textures

		# Gun is a little in front of and below camera
		self.gun.coord.pos = self.camera.pos - self.camera.view.n * 0.5 - self.camera.view.v * 0.175
		self.gun.coord.look(self.camera.pos)  # Gun sprite is looking at the camera
		# Gun sprite is rotated forward a little to catch light better and to minimize weird bar above it :/
		self.gun.coord.rotate(Vec(0.2))
		# Muzzle is in front of gun
		self.muzzle.coord.pos = self.camera.pos - self.camera.view.n - self.camera.view.v * 0.175 + self.camera.view.u * 0.025
		self.muzzle.coord.look(self.camera.pos)  # Muzzle sprite is looking at player
		self.gun_flash.pos = self.camera.pos - self.camera.view.n * 0.1  # Gun flash-light follows the gun

		hit = False
		for x, enemy in enumerate(self.enemies):
			dist = enemy.coord.pos.dist(self.camera.pos)  # Distance from enemy to camera (player)
			if dist <= 4 * self.radius:  # Within attack range
				self.enemy_states[x] = "attack"
				if self.hp_drain_timer.passed():  # Only take damage if enough time has passed since last damage taken
					self.hp -= 5
					self.oof_sfx.play()
					hit = True
			elif dist <= self.enemy_detection_radius:  # Player is close enough to enemy to be detected
				direction = self.camera.pos - enemy.coord.pos  # Direction to player
				old_pos = enemy.coord.pos
				enemy.coord.pos += direction * self.enemy_speed * self.delta_time  # Move towards player
				new_pos = enemy.coord.pos
				# Enemy collides with all other enemies and textures
				self.collide_objects(old_pos, new_pos, enemy.coord.pos, self.enemies[:x] + self.enemies[x+1:] + self.walls)
				if self.enemy_state_update_timer.passed():  # Ensures animation frames don't change each game frame
					if self.enemy_states[x].startswith("walk"):  # Next frame in walk cycle
						self.enemy_states[x] = f"walk{(int(self.enemy_states[x][-1])+1)%3}"
					else:  # First frame in walk cycle
						self.enemy_states[x] = "walk0"
			else:
				self.enemy_states[x] = "idle"

			n, _, _ = enemy.coord.look(self.camera.pos)  # Enemy looks at player, we store forward direction for enemy
			# If the player has shot last frame, enemy is within range, and forward vectors of player and enemy are
			# near opposites, then the player has hit.
			if self.shot and dist <= 2 * self.enemy_detection_radius and pi - self.camera.view.n.angle(n) < self.hit_margin:
				choice((self.death1_sfx, self.death2_sfx)).play()  # Random death sound for enemy
				del self.enemies[x]  # Delete enemy

		if hit:  # If the player was hit this frame, start damage immunity timer
			self.hp_drain_timer.start(self.hp_drain_time)

		if self.enemy_state_update_timer.passed():  # Reset animation delay timer
			self.enemy_state_update_timer.reset()

		if self.shot:  # If player shot recently, subtract bullet from clip and show flash-light, else reset flash-light
			self.clip -= 1
			self.gun_flash.diff = Vec(0.75, 0.25)
			self.gun_flash.spec = Vec(0.2, 0.1, 0.1)
			self.shader.set_light(*self.gun_flash, len(self.lights))
			self.shot = False
		elif self.muzzle_timer.passed() and self.gun_flash.diff.x != 0:
			self.gun_flash.diff = Vec()
			self.gun_flash.spec = Vec()
			self.shader.set_light(*self.gun_flash, len(self.lights))

		for key, card in [*self.keycards.items()]:  # Key-card pickup
			card.coord.look(self.camera.pos)  # Card sprite is looking at camera
			if card.coord.pos.dist(self.camera.pos) <= 3 * self.radius:
				self.pickup_sfx.play()
				del self.keycards[key]

		for x, ammobox in enumerate(self.ammoboxes):  # Ammo-box pickup
			ammobox.coord.look(self.camera.pos)  # Ammo sprite is looking at camera
			if ammobox.coord.pos.dist(self.camera.pos) <= 3 * self.radius and self.ammo < self.max_ammo:
				self.ammo += min(self.max_ammo-self.ammo, self.max_clip)
				self.pickup_sfx.play()
				del self.ammoboxes[x]

		for x, medkit in enumerate(self.medkits):  # Med-kit pickup
			medkit.coord.look(self.camera.pos)  # Kit is looking at camera
			if medkit.coord.pos.dist(self.camera.pos) <= 3 * self.radius and self.hp < self.max_hp:
				self.hp += min(self.max_hp-self.hp, 15)
				self.pickup_sfx.play()
				del self.medkits[x]

		# Win lose conditions
		if len(self.keycards) == 0 and self.door.coord.pos.dist(self.camera.pos) <= 0.75:
			print(f"""__   _______ _   _   _    _ _____ _   _ 
\ \ / /  _  | | | | | |  | |_   _| \ | |
 \ V /| | | | | | | | |  | | | | |  \| |
  \ / | | | | | | | | |/\| | | | | . ` |
  | | \ \_/ / |_| | \  /\  /_| |_| |\  |
  \_/  \___/ \___/   \/  \/ \___/\_| \_/

It took you {pg.time.get_ticks()/1000} seconds.""")
			self.quit()
		elif self.hp <= 0:
			print(f"""__   _______ _   _   _     _____ _____ _____ 
\ \ / /  _  | | | | | |   |  _  /  ___|  ___|
 \ V /| | | | | | | | |   | | | \ `--.| |__  
  \ / | | | | | | | | |   | | | |`--. \  __| 
  | | \ \_/ / |_| | | |___\ \_/ /\__/ / |___ 
  \_/  \___/ \___/  \_____/\___/\____/\____/ 

It took you {pg.time.get_ticks()/1000} seconds.""")
			self.quit()

	def display(self):
		self.model.load_identity()  # Reset model matrix

		glBindTexture(GL_TEXTURE_2D, self.ceiling_tex)
		self.doom_logo.draw()

		glBindTexture(GL_TEXTURE_2D, self.wall_tex)
		for wall in self.walls:
			wall.draw_set()

		glBindTexture(GL_TEXTURE_2D, self.floor_tex)
		self.floor.draw_set()

		glBindTexture(GL_TEXTURE_2D, self.door_tex)
		self.door.draw_set()

		glBindTexture(GL_TEXTURE_2D, self.ceiling_tex)
		self.ceiling.draw_set()

		for key, card in self.keycards.items():
			glBindTexture(GL_TEXTURE_2D, self.keycard_tex[key])
			card.draw_set()

		glBindTexture(GL_TEXTURE_2D, self.ammobox_tex)
		for ammobox in self.ammoboxes:
			ammobox.draw_set()

		glBindTexture(GL_TEXTURE_2D, self.medkit_tex)
		for medkit in self.medkits:
			medkit.draw_set()

		for x, enemy in enumerate(self.enemies):
			glBindTexture(GL_TEXTURE_2D, self.enemy_state_tex[self.enemy_states[x]])
			enemy.draw_set()

		glClear(GL_DEPTH_BUFFER_BIT)  # Clear depth buffer so that following objects render on top

		if not self.muzzle_timer.passed():
			glBindTexture(GL_TEXTURE_2D, self.muzzle_tex)
			self.muzzle.draw_set()

		glBindTexture(GL_TEXTURE_2D, self.gun_tex)
		self.gun.draw_set()

		self.render_text(f"{self.clip}/{self.ammo}", Vec(15, 90), Vec(255), 48)
		self.render_text(str(self.hp), Vec(15, 0), Vec(255), 96)
		self.render_text(
			f"R: {int('red'not in self.keycards)}  B: {int('blue'not in self.keycards)}  Y: {int('yellow'not in self.keycards)}",
			Vec(self.bounds.x-175, 0), Vec(255), 48, "fonts/DoomRight.ttf"
		)

	def update_input(self):
		for event in pg.event.get():
			if event.type == pg.QUIT:
				self.quit()
			elif event.type == pg.KEYDOWN:
				if event.key == pg.K_RETURN:
					print(self.camera.pos)
				if event.key == pg.K_ESCAPE:
					self.quit()
				if event.key == pg.K_RIGHT:
					self.rot_vec.y -= 1
				if event.key == pg.K_LEFT:
					self.rot_vec.y += 1
				if event.key == pg.K_d:
					self.mov_vec.x += 1
				if event.key == pg.K_a:
					self.mov_vec.x -= 1
				if event.key == pg.K_SPACE and self.muzzle_timer.passed():  # Shooting
					if self.clip > 0:
						self.muzzle_timer.start(self.muzzle_time)
						self.pistol_sfx.play()
						self.shot = True
					else:
						self.pistol_click_sfx.play()
				if event.key == pg.K_r:  # Reloading
					if self.ammo > 0 and self.clip != self.max_clip:
						carry = min(self.max_clip - self.clip, self.ammo)
						self.clip += carry
						self.ammo -= carry
						self.pistol_reload_sfx.play()
					else:
						self.pistol_click_sfx.play()
				if event.key == pg.K_LSHIFT:
					self.mov_spd *= 1.5
				if event.key == pg.K_s:
					self.mov_vec.z += 1
				if event.key == pg.K_w:
					self.mov_vec.z -= 1
			elif event.type == pg.KEYUP:
				if event.key == pg.K_RIGHT:
					self.rot_vec.y += 1
				if event.key == pg.K_LEFT:
					self.rot_vec.y -= 1
				if event.key == pg.K_d:
					self.mov_vec.x -= 1
				if event.key == pg.K_a:
					self.mov_vec.x += 1
				if event.key == pg.K_LSHIFT:
					self.mov_spd /= 1.5
				if event.key == pg.K_s:
					self.mov_vec.z -= 1
				if event.key == pg.K_w:
					self.mov_vec.z += 1


gh = GameHandler(1280, 720, 60)
gh.loop()