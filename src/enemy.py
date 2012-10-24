from panda3d.core import *
from direct.actor.Actor import Actor
from panda3d.ai import *

from unit import Unit

class Enemy(Unit):

    # Declare class variables
    EXPAward = 0

    # Declare private variables
    _removeCorpseDelay = 3 # seconds before corpse is cleaned


    def __init__(self, parentNode, enemyList, playerRef, EXPAward, AIworldRef):
        print("Enemy class instantiated")

        self._enemyListRef = enemyList
        self._AIworldRef = AIworldRef
        self._playerRef = playerRef        

        self.enemy = parentNode.attachNewNode('enemy' + str(len(self._enemyListRef)-1))
        self._enemyListRef.append(self.enemy)

        self.loadEnemyModel(self.enemy)

        self.setEXPReward(EXPAward)

    def loadEnemyModel(self, enemyNode):
        self.enemyModel = Actor("models/funny_sphere.egg")
        self.enemyModel.reparentTo(enemyNode)

        enemyNode.setPos(-2, 0, 1)
        enemyNode.setScale(0.1)

        self.enemyAI = AICharacter('enemy',
                                enemyNode,
                                100, # Mass
                                0.05, # Movt force
                                4) # Max force
        self._AIworldRef.addAiChar(self.enemyAI)

        self.enemyAIBehaviors = self.enemyAI.getAiBehaviors()
        #self.enemyAIBehaviors.pursue(self._playerRef.getPlayerNode())

        #self.enemyAIBehaviors.obstacleAvoidance(1.0)
        #self._AIworldRef.addObstacle(enemyNode)

    def moveEnemy(self, moveTo):
        self.enemy.setPos(moveTo)

    def setEXPReward(self, value):
        self.EXPAward = value

    def onDeath(self):
        if self.getIsDead():
            # Award the player exp
            self._playerRef.receiveEXP(self.EXPAward)

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
        self.enemyModel.delete()

        # Remove the enemy node
        self.enemy.removeNode()

        return task.done

    def getEnemyNode(self):
        return self.enemy
