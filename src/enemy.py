from panda3d.core import *
from direct.actor.Actor import Actor

from unit import Unit

class Enemy(Unit):

    # Declare class variables
    EXPAward = 0

    # Declare private variables
    _removeCorpseDelay = 3 # seconds before corpse is cleaned


    def __init__(self, parentNode, enemyList, playerRef, EXPAward):
        print("Enemy class instantiated")

        self._enemyListRef = enemyList

        self.enemy = parentNode.attachNewNode('enemy' + str(len(self._enemyListRef)-1))
        self._enemyListRef.append(self.enemy)

        self.loadEnemyModel(self.enemy)

        self._playerRef = playerRef

        self.setEXPReward(EXPAward)

    def loadEnemyModel(self, enemyNode):
        self.enemyModel = Actor("models/funny_sphere.egg")
        self.enemyModel.reparentTo(enemyNode)

        enemyNode.setPos(-2, 0, 1)
        enemyNode.setScale(0.1)

    def moveEnemy(self, moveTo):
        self.enemy.setPos(moveTo)

    def setEXPReward(self, value):
        self.EXPAward = value

    def onDeath(self):
        if self.getIsDead():
            # Award the player exp
            self._playerRef.giveEXP(self.EXPAward)

            # Change animation to death

            # Remove enemy
            taskMgr.doMethodLater(self._removeCorpseDelay,
                             self.removeCorpse,
                            'RemoveCorpseTask')

    def removeCorpse(self, task):
        # Remove enemy from enemyList
        self._enemyListRef.remove(self.enemy)

        # Cleanup the enemy model
        self.enemyModel.cleanup()

        # Remove the enemy node
        self.enemy.removeNode()

        return task.done
