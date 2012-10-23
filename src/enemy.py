from panda3d.core import *
from direct.actor.Actor import Actor

from unit import Unit

class Enemy(Unit):

	enemyList = []

	def __init__(self, parentNode):
		print("Enemy class instantiated")
		self.createEnemy(parentNode)

	def createEnemy(self, parentNode):
		self.enemy = parentNode.attachNewNode('enemy' + str(len(self.enemyList)))
		self.enemyList.append(self.enemy)

		self.loadEnemyModel(self.enemy)

	def loadEnemyModel(self, enemyNode):
		self.enemyModel = Actor("models/funny_sphere.egg")
		self.enemyModel.reparentTo(enemyNode)

		enemyNode.setPos(-2, 0, 1)
		enemyNode.setScale(0.1)

	def moveEnemy(self, moveTo):
		self.enemy.setPos(moveTo)