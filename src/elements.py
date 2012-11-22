from panda3d.core import *

import utils

class HealthGoblet():

    healthGivenFactor = 8
    minHealthGiven = 5

    def __init__(self, mainRef, enemyRef):
        self._enemyRef = enemyRef
        self._playerRef = mainRef.player

        self.healthGobletNode = mainRef.mainNode.attachNewNode('healthGobletNode')

        self.initAttributes()
        self.initModel()

        taskMgr.doMethodLater(1.5, self.updateHealthGoblet, 'updateHealthGobletTask')


    def initAttributes(self):
        self.healthGiven = utils.getDXY(self.minHealthGiven, self._enemyRef.level * self.healthGivenFactor)
        self.perceptionRange = 0.5

        self.healthGobletNode.setPos(self._enemyRef.enemyNode.getPos())

    def initModel(self):
        pass

    def updateHealthGoblet(self, task):
        playerNode = self._playerRef.playerNode
        if utils.getIsInRange(playerNode.getPos(), self.healthGobletNode.getPos(), self.perceptionRange):
            print 'healed player for:', self.healthGiven
            self._playerRef.heal(self.healthGiven)

            self.suicide()
            return task.done

        return task.again

    def suicide(self):
        # Cleanup the healthGobletModel
        #self.healthGobletModel.cleanup()
        #self.healthGobletModel.delete()

        self.healthGobletNode.removeNode()

        self._enemyRef = None
        self._playerRef = None