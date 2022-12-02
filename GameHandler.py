import pygame as pg
from pygame.locals import *

from OpenGL.GL import *

from Vec import Vec


# Defines class which Handles game loop
class GenericGameHandler:
	def __init__(self, x_bounds, y_bounds, desired_fps, bg_color=(0.2, 0.2, 0.2, 1.0)):
		self.bounds = Vec(x_bounds, y_bounds)
		self.fps = desired_fps
		self.delta_time = 0
		self.clock = pg.time.Clock()
		self.bg_color = bg_color
		
		pg.display.init()
		pg.font.init()
		pg.mixer.init(channels=8)
		self.screen = pg.display.set_mode((self.bounds.x, self.bounds.y), DOUBLEBUF|OPENGL)

		glClearColor(*bg_color)

		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	def quit(self):  # Quits game
		pg.quit()
		quit()

	def update_input(self):  # What happens when input is updated, Defined by subclass
		pass

	def update(self):  # What happens when game state is updated, Defined by subclass
		pass

	def __display_start(self):  # Runs OpenGL display header
		glEnable(GL_DEPTH_TEST)
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

		glViewport(0, 0, self.bounds.x, self.bounds.y)

	def __display_end(self):  # Runs OpenGL display footer
		pg.display.flip()

	def display(self):  # What happens when game state should be drawn, Defined by subclass
		pass

	def loop(self):  # Game loop
		# Ensures delta time is reasonable value by time program is running
		self.delta_time = self.clock.tick(10000) / 1000
		self.delta_time = self.clock.tick(10000) / 1000
		while True:
			self.delta_time = self.clock.tick(self.fps) / 1000
			self.update_input()
			self.update()
			self.__display_start()
			self.display()
			self.__display_end()