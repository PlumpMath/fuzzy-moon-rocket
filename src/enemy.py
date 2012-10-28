#from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from direct.actor.Actor import Actor
from panda3d.ai import *

import utils
from unit import Unit

class Enemy(Unit):

    # Declare class variables
    EXPAward = 0
    perceptionRange = 100 # Range that enemies will perceive player

    # Declare private variables
    _removeCorpseDelay = 3 # seconds before corpse is cleaned
    _inCombat = False

    def __init__(self, parentNode, enemyList, playerRef, EXPAward, AIworldRef, worldRef):
        print("Enemy class instantiated")

        self._enemyListRef = enemyList
        self._AIworldRef = AIworldRef
        self._playerRef = playerRef
        self._worldRef = worldRef

        self.enemyNode = parentNode.attachNewNode('enemy' + str(len(self._enemyListRef)-1))
        self._enemyListRef.append(self.enemyNode)

        self.loadEnemyModel()
        self.initEnemyAi()

        self.setEXPReward(EXPAward)

        self.enemyNode.setTag('enemy', '1') 

    def loadEnemyModel(self):
        self.enemyModel = Actor("models/funny_sphere.egg")
        self.enemyModel.reparentTo(self.enemyNode)

        self.enemyNode.setPos(-2, 0, 1)
        self.enemyNode.setScale(0.1)

    def initEnemyAi(self):
        self.enemyAI = AICharacter('enemy',
                                self.enemyNode,
                                100, # Mass
                                0.05, # Movt force
                                4) # Max force
        self._AIworldRef.addAiChar(self.enemyAI)

        self.enemyAIBehaviors = self.enemyAI.getAiBehaviors()

        enemyUpdateTask = taskMgr.add(self.enemyUpdater, 'enemyUpdaterTask')
        enemyUpdateTask.last = 0

    def enemyUpdater(self, task):
        deltaTime = task.time - task.last
        task.last = task.time

        if deltaTime < .2:
            return task.cont

        playerPos = self._playerRef.playerNode.getPos()
        enemyPos = self.enemyNode.getPos()

        if utils.getIsInRange(playerPos, enemyPos, self.perceptionRange):
            if not self._inCombat:
                    self.enemyAIBehaviors.pursue(self._playerRef.playerNode)
                    self._inCombat = True
                    print('start chasing')
            else:
                    self.attack()
                    print('attack!')

        return task.cont

    def setEXPReward(self, value):
        self.EXPAward = value

    def attack(self):
        self._playerRef.receiveDamage(self.getDamageBonus())

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
        self._enemyListRef.remove(self.enemyNode)

        # Cleanup the enemy model
        self.enemyModel.cleanup()
        self.enemyModel.delete()

        # Remove the enemy node
        self.enemyNode.removeNode()

        return task.done

    def getEnemyNode(self):
        return self.enemyNode

    def moveEnemy(self, x, y):
        self.enemyNode.setPos(x, y, 1)
