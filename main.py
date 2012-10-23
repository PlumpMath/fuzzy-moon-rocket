import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from direct.actor.Actor import Actor
from direct.task import Task
import sys

from src import player, enemy

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

		self.player = player.Player(self.mainNode)

		self.enemy = enemy.Enemy(self.mainNode)
		self.enemy.moveEnemy((0, 0, 1))

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
		# Setup initial camera (later overridden by Player)
		base.disableMouse()
		base.camera.setPos(0, 5, 5)
		base.camera.lookAt(initLookAt)		

app = World()
run()
