import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from direct.actor.Actor import Actor
from direct.task import Task
import sys

class World(DirectObject):
	
	def __init__(self):
		# Set background color
		base.setBackgroundColor(0.5, 0.5, 0.5, 1)

		# Models directory
		self.modelsDir = "models/"

		# Main game node
		self.mainNode = render.attachNewNode('mainNode')	

		self.initSun(self.mainNode)

		self.initGround(self.mainNode)

		self.initCamera(self.plane)

		self.player = Player(self.mainNode)

	def initSun(self, parentNode):
		# Setup directional light
		self.dlight = DirectionalLight('dlight')
		self.dlight.setColor(VBase4(1, 1, 0.5, 1))

		self.dlightNode = self.mainNode.attachNewNode(self.dlight)
		self.dlightNode.setHpr(0, -140, 0)
		parentNode.setLight(self.dlightNode)	

	def initGround(self, parentNode):
		# Setup environment (plane)
		self.plane = loader.loadModel(self.modelsDir + "grass_plane.egg")

		self.plane.setPos(0, 0, 0)
		self.plane.setHpr(0, -90, 0)
		self.plane.setScale(5)

		self.plane.reparentTo(parentNode)		

	def initCamera(self, initLookAt):
		base.disableMouse()
		base.camera.setPos(0, 5, 5)
		base.camera.lookAt(initLookAt)		


class Unit(object):

	strength = 0
	constitution = 0
	dexterity = 0
	damage = 0
	attackBonus = 0
	maxHealthPoints = 0
	armorClass = 0
	movementSpeed = 0

	level = 0
	experience = 0
	prevEXP = 0

	def __init__(self):
		print("Unit class instantiated")
		self.initAttributes()
		self.initlevel()

	def initAttributes(self):
		self.strength = 0
		self.constitution = 0
		self.dexterity = 0

		self.damage = 0 # affected by strength
		self.attackBonus = 0 # Affected by strength
		self.maxHealthPoints = 0 # affected by constitution
		self.armorClass = 0 # affected by dexterity

		self.movementSpeed = 0.5 # Not affected by attributes

		self._currentHealthPoints = self.maxHealthPoints
		self._damageModifier = 1 # Added to damage to calculate total damage

		self.updateHealthPoints() # initialize the hit points

	def initlevel(self):
		self.level = 1
		self.experience = 0
		self.prevEXP = 0

	def getCurrentdamage(self):
		return self.damage + self._damageModifier

	def increaseStrength(self):
		self.strength += 1

	def getCurrentdamageModifier(self):
		self._damageModifier = 1 + (self.strength - 10) / 2
		return self._damageModifier

	def giveEXP(self, value):
		self.experience += value
		if self.experience > self.prevEXP + (self.level * 1000):
			self.increaseLevel()

	def increaseLevel(self):
		self.prevEXP += (self.level * 1000) # increment prevExp
		self.level += 1 # increment level
		self.updateHealthPoints() # Make sure the player's health is updated

		if self.level % 4 == 0: # Every 4th level increase attribute
			self.increaseStrength()
			
	def updateHealthPoints(self):
		self.maxHealthPoints = (self.level * (10 + ((self.constitution - 10) / 2)))





class Player(Unit):

	def __init__(self, parentNode):
		print("Player class instantiated")
		super(Player, self).__init__()
		
		self.initPlayerAttributes()

		self.playerNode = parentNode.attachNewNode('playerNode')

		self.initPlayerModel(self.playerNode)
		self.updatePlayerCamera(self.playerNode)

		#self.initPlayerControls()
		self.mouseHandler = MouseHandler()

	def initPlayerAttributes(self):
		self.strength = 16
		self.constitution = 14
		self.dexterity = 10

		self.damage += self.getCurrentdamageModifier()

	def updatePlayerCamera(self, playerNode):		
		base.camera.setPos(playerNode.getX(), 
						   playerNode.getY() - 5, 
						   playerNode.getZ() + 5)
		base.camera.lookAt(playerNode)

	def initPlayerModel(self, playerNode):
		self._playerModel = Actor("models/BendingCan.egg")

		#self._playerModel.setPos(2, 0, 1)
		#self._playerModel.setScale(0.1)		

		self._playerModel.reparentTo(playerNode)

		playerNode.setScale(0.1)
		playerNode.setPos(2, 0, 1)



class MouseHandler(DirectObject):

	mouseX = 0
	mouseY = 0

	def __init__(self):
		self.initMouseControls()

	def initMouseControls(self):
		# Initialize movement controls

		self.accept('mouse1', self.move)

	def move(self):
		# Get mouse position
		if base.mouseWatcherNode.hasMouse():
			self.mouseX = base.mouseWatcherNode.getMouseX()
			self.mouseY = base.mouseWatcherNode.getMouseY()

		print ("x: " + str(self.mouseX) + ", y: " + str(self.mouseY))



app = World()
run()


