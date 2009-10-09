import numpy
import objects

class Group(object):
	"""
	This class represents a group of objects.
	"""

	def __init__(self):
		self.objects = []
		
	def __iter__(self):
		return self.objects