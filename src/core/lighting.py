from OpenGL.GL import *

class Lighting(object):
	"""
	This class represents the lighting of the scene.
	"""
	
	def __init__(self):
		"""
		Constructor.
		"""
		
		# Dictionary that contains all the lights of the scene. 
		self.lights = {}
		
	def enableLighting(self):
		"""
		Enables the lighting system.
		"""
		
		glEnable(GL_LIGHTING)
	
	def addLight(self, id):
		"""
		Adds a light in the scene. id should be GL_LIGHTn.
		"""
		
		newLight = Light(id)
		self.lights[id] = newLight
		
	def setLight(self, id, position, diffuse, specular, ambient):
		"""
		Sets the id light. id should be GL_LIGHTn.
		"""
		
		self.lights[id].set(position, diffuse, specular, ambient)
		
	def render(self):
		"""
		Renders all lights.
		"""
		
		for light in self.lights.values():
			light.render()

class Light(object):
	"""
	This class represents an OpenGL light.
	"""
	
	def __init__(self, id):
		"""
		Constructor.
		"""
		
		self.id = id
		glEnable(id)
		
		self.position = []
		self.diffuse = []
		self.specular = []
		self.ambient = []
		
	def set(self, position, diffuse, specular, ambient):
		"""
		Sets the light.
		"""
		
		self.position = position
		self.diffuse = diffuse
		self.specular = specular
		self.ambient = ambient
		
	def render(self):
		"""
		Renders the light.
		"""
				
		glLight(self.id, GL_POSITION, self.position)
		glLight(self.id, GL_DIFFUSE, self.diffuse)
		glLight(self.id, GL_SPECULAR, self.specular)
		glLight(self.id, GL_AMBIENT, self.ambient)