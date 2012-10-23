from panda3d.core import *
from direct.actor.Actor import Actor

from utils import MouseHandler
from unit import Unit
class Player(Unit):

	def __init__(self, parentNode):
		print("Player class instantiated")
		super(Player, self).__init__()
		
		self.initPlayerAttributes()

		self.playerNode = parentNode.attachNewNode('playerNode')

		self.initPlayerModel(self.playerNode)
		self.updatePlayerCamera(self.playerNode)

		self._mouseHandler = MouseHandler()

	def initPlayerAttributes(self):
		self.strength = 16
		self.constitution = 14
		self.dexterity = 10

		#self.damage += self.getCurrentdamageModifier()

	def updatePlayerCamera(self, playerNode):	
		base.disableMouse()	
		base.camera.setPos(playerNode.getX(), 
						   playerNode.getY() - 5, 
						   playerNode.getZ() + 5)
		base.camera.lookAt(playerNode)

	def initPlayerModel(self, playerNode):
		self._playerModel = Actor("models/BendingCan.egg")
		self._playerModel.reparentTo(playerNode)

		playerNode.setScale(0.1)
		playerNode.setPos(2, 0, 1)

	def getPos(self):
		return self.playerNode.getPos()