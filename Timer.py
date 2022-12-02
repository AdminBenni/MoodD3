# Made this Timer class some time ago (pun intended, hehe), I use it for a lot of projects :)

from typing import Optional
import time

class Timer:
	"""
		Timer:
			A class representing a timer for a duration of milliseconds
	"""

	def __init__(self, milliseconds: Optional[int] = None):
		self.__milli: int = 0
		self.__start: int = 1
		self.__set: bool = False
		if milliseconds is not None:
			self.start(milliseconds)

	@property
	def start_time(self) -> int:
		return self.__start

	@property
	def milli(self) -> int:
		return self.__milli

	@property
	def is_set(self) -> bool:
		return self.__set

	@property
	def end_time(self) -> int:
		return self.__start + self.__milli

	@property
	def duration(self) -> int:
		return self.end_time - self.start_time

	def start(self, milliseconds: int) -> None:
		self.__milli: int = milliseconds
		self.__start: int = int(time.time() * 1000)
		self.__set: bool = True

	def reset(self) -> None:
		self.__start: int = int(time.time() * 1000)

	def unset(self) -> None:
		self.__init__()

	def passed(self) -> bool:
		return self.milliseconds_left() <= 0 and self.is_set

	def seconds_left(self) -> float:
		return self.end_time / 1000 - time.time()

	def milliseconds_left(self) -> int:
		return self.end_time - int(time.time() * 1000)

	def seconds_passed(self) -> float:
		return time.time() - self.start_time / 1000

	def milliseconds_passed(self) -> int:
		return int(time.time() * 1000) - self.start_time

	def progress(self) -> float:
		return self.milliseconds_passed() * 100 / self.duration
