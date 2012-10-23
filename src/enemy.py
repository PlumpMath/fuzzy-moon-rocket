from panda3d.core import *
from direct.actor.Actor import Actor

from unit import Unit

class Enemy(Unit):

	def __init__(self, parentNode, enemyList):
		print("Enemy class instantiated")

		self.enemy = parentNode.attachNewNode('enemy' + str(len(enemyList)))
		enemyList.append(self.enemy)

		self.loadEnemyModel(self.enemy)

	def loadEnemyModel(self, enemyNode):
		self.enemyModel = Actor("models/funny_sphere.egg")
		self.enemyModel.reparentTo(enemyNode)

		enemyNode.setPos(-2, 0, 1)
		enemyNode.setScale(0.1)

	def moveEnemy(self, moveTo):
		self.enemy.setPos(moveTo)