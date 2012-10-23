from panda3d.core import *
from direct.actor.Actor import Actor

from utils import MouseHandler
from unit import Unit

class Player(Unit):

	def __init__(self, parentNode):
		print("Player class instantiated")
		super(Player, self).__init__()
		
		self.playerNode = parentNode.attachNewNode('playerNode')

		self.initPlayerAttributes()
		self.initPlayerModel(self.playerNode)
		self.initPlayerCamera(self.playerNode)

		self._mouseHandler = MouseHandler()

	def initPlayerAttributes(self):
		# Initialize player attributes
		self.strength = 16
		self.constitution = 14
		self.dexterity = 10

	def initPlayerCamera(self, playerNode):	
		# Initialize the camera
		base.disableMouse()	
		base.camera.setPos(playerNode.getX(), 
						   playerNode.getY() - 5, 
						   playerNode.getZ() + 5)
		base.camera.lookAt(playerNode)

	def initPlayerModel(self, playerNode):
		# Initialize the player model (Actor)
		self._playerModel = Actor("models/BendingCan.egg")
		self._playerModel.reparentTo(playerNode)

		playerNode.setScale(0.1)
		playerNode.setPos(2, 0, 1)

	def getPos(self):
		return self.playerNode.getPos()
