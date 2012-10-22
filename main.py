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

class Unit():

	def __init__(self):
		print("Unit class instantiated")
		self.initAttributes()

	def initAttributes(self):
		self.Strength = 0
		self.Constitution = 0
		self.Dexterity = 0

		self.Damage = 0 # affected by strength
		self.AttackBonus = 0 # Affected by strength
		self.HealthPoints = 0 # affected by constitution
		self.ArmorClass = 0 # affected by dexterity

	def initLevel(self):
		self.Level = 1
		self.Experience = 0

	def giveEXP(self, value):
		self.Experience += value
		if self.Experience % 1000:
			self.increaseLevel()
		

	def increaseLevel(self):
		self.Level += 1

		if self.Level % 4 == 0:
			self.Strength += 1



app = World()
run()


