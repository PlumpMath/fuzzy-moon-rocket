import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from direct.actor.Actor import Actor
from direct.task import Task

class World(DirectObject):
	
	def __init__(self):
		# Set background color
		base.setBackgroundColor(0.5, 0.5, 0.5, 1)

		# Models directory
		self.modelsDir = "models/"

		# Main game node
		self.mainNode = render.attachNewNode('mainNode')	

		# Setup directional light
		dlight = DirectionalLight('dlight')
		dlight.setColor(VBase4(1, 1, 0.5, 1))

		dlightNode = self.mainNode.attachNewNode(dlight)
		dlightNode.setHpr(0, -60, 0)
		self.mainNode.setLight(dlightNode)		

		# Setup environment (plane)
		plane = loader.loadModel(self.modelsDir + "grass_plane.egg")

		plane.setPos(0, 0, 0)
		plane.setHpr(0, -90, 0)
		plane.setScale(5)

		plane.reparentTo(self.mainNode)

		player = Player(self.mainNode)



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

	def initPlayerAttributes(self):
		self.strength = 16
		self.constitution = 14
		self.dexterity = 10

		self.damage += self.getCurrentdamageModifier()

	def updatePlayerCamera(self, playerNode):
		base.camera.lookAt(playerNode)
		base.camera.setPos(playerNode.getX(), 
						   playerNode.getY() - 4, 
						   playerNode.getZ() + 5)

	def initPlayerModel(self, playerNode):
		self._playerModel = Actor("models/BendingCan.egg")

		self._playerModel.setPos(2, 0, 1)
		self._playerModel.setScale(0.1)		

		self._playerModel.reparentTo(playerNode)

app = World()
run()


