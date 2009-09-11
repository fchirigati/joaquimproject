from OpenGL.raw.GLUT import *

class Cube():
    """Class that defines a cube."""
    
    def __init__(self, side, wire=True):
        """Constructor."""
        self.rotationMatrix = []
        self.centralPosition = []
        if wire:
            glutWireCube(side)
        else:
            glutSolidCube(side)
            
    def getRotationMatrix(self):
        return self.rotationMatrix
            
    def setRotationMatrix(self, rotationMatrix):
        self.rotationMatrix = rotationMatrix
        
    def getCentralPosition(self):
        return self.centralPosition
            
    def setCentralPosition(self, centralPosition):
        self.centralPosition = centralPosition
            
class Sphere():
    """Class that defines a sphere."""
    
    def __init__(self, radius, wire=True):
        """Constructor."""
        self.rotationMatrix = []
        self.centralPosition = []
        if wire:
            glutWireSphere(radius, 20, 20)
        else:
            glutSolidSphere(radius, 20, 20)
            
    def getRotationMatrix(self):
        return self.rotationMatrix
            
    def setRotationMatrix(self, rotationMatrix):
        self.rotationMatrix = rotationMatrix
        
    def getCentralPosition(self):
        return self.centralPosition
            
    def setCentralPosition(self, centralPosition):
        self.centralPosition = centralPosition