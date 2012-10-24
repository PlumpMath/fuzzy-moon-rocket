import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.actor.Actor import Actor
from direct.task import Task
import sys

from src import player, enemy, gui, hud, map

class World(ShowBase):

	enemyList = []

	def __init__(self):
		#ShowBase.__init__(self)

		# Set background color
		base.setBackgroundColor(0.1, 0.1, 0.1, 1)

		# Main game node
		self.mainNode = render.attachNewNode('mainNode')

		# Instantiate other classes
		self.mapHandler = map.Map(self.mainNode)

		self.player = player.Player(self.mainNode)

		self.enemy = enemy.Enemy(self.mainNode, 
								self.enemyList, 
								self.player,
								500)
		self.enemy.moveEnemy((0, 0, 1))

		self.gui = gui.GUI()

		self.hud = hud.HUD(self.player)

		self.accept('1', self.setHalfHealth)
		self.accept('2', self.killEnemy)

	def setHalfHealth(self):
		self.player.receiveDamage(self.player.maxHealthPoints / 2)

	def killEnemy(self):
		self.enemy.onDeath()

app = World()
run()
