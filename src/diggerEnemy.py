from panda3d.core import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *

import enemy
import utils

class Digger(enemy.Enemy):

    def __init__(self, mainRef):
        enemy.Enemy.__init__(self, mainRef, enemy.koboldSkirmisher) # Change to correct kobold

        self.holeModel = None

    def initAttributes(self, attributes):
        super(Digger, self).initAttributes(attributes)

        rangeMultiplier = 2
        self.combatRange *= rangeMultiplier
        self.perceptionRange *= rangeMultiplier

    def loadEnemyModel(self, modelName):
        modelPrefix = 'models/digger-'
        self.enemyModel = Actor(modelPrefix + 'model', {
                'attack1':modelPrefix+'attack1',
                'attack2':modelPrefix+'attack2',
                'attack3':modelPrefix+'attack3',
                'attack4':modelPrefix+'attack4',
                'special-attack':modelPrefix+'special-attack',

                'pursue':modelPrefix+'pursue',
                'pursue-to-idle':modelPrefix+'pursue-stop',

                'idle-walk':modelPrefix+'idle-walk',
                'idle-walk-to-pursue':modelPrefix+'idle-walk-to-pursue',
                'idle-walk-to-dig':modelPrefix+'idle-walk-to-dig',
                'idle-walk-to-dig-to-sleep':modelPrefix+'idle-walk-to-dig-to-sleep',

                'hit1':modelPrefix+'hit1',
                'hit2':modelPrefix+'hit2',

                'death1':modelPrefix+'death1',
                'death2':modelPrefix+'death2',
                'death3':modelPrefix+'death3'
            })
        self.enemyModel.reparentTo(self.enemyNode)
        #self.enemyModel.setH(-180)

        self.enemyNode.setPos(Point3.zero())

        self.enemyNode.setDepthOffset(-1)

    def enterIdle(self):
        #print 'enemy enterIdle'
        stopEnemy = self.enemyModel.actorInterval('pursue-to-idle', loop=0)
        idleEnemy = Func(self.enemyModel.loop, 'idle-walk-to-dig')
        digHole = Func(self.createHole)
        jumpDownHole = self.enemyModel.actorInterval('idle-walk-to-dig-to-sleep')

        self.stopSequence = Sequence(stopEnemy, idleEnemy, Wait(1), digHole, Wait(1), jumpDownHole)
        self.stopSequence.start()

        self.isSleeping = True

    def enterPursue(self):
        #print('enemy enterPursue')
        loopWalkEnemy = Func(self.enemyModel.loop, 'pursue')

        # Only awake enemy if it comes from idle
        if self.isSleeping: 
            self.isSleeping = False

            awakeEnemy = self.enemyModel.actorInterval('idle-walk-to-pursue', loop=0)
            self.awakeSequence = Sequence(awakeEnemy, loopWalkEnemy, Func(self.pursuePlayer))
        else:
            self.awakeSequence = Sequence(loopWalkEnemy, Func(self.pursuePlayer))

        self.awakeSequence.start()

    def enterDeath(self):
        #print('enemy enterDeath')
        self.enemyAIBehaviors.removeAi('all')
        randomDeathAnim = 'death' + str(utils.getDX(3))
        self.enemyModel.play(randomDeathAnim)

    def playAttackAnimation(self):
        randomAttackAnim = 'attack' + str(utils.getD4())
        self.enemyModel.play(randomAttackAnim)

    def playHitAnimation(self):
        randomHitAnim = 'hit' + str(utils.getDX(2))
        self.enemyModel.play(randomHitAnim)

    def createHole(self):
        if self.holeModel == None:
            self.holeModel = Actor('models/hole-model',
                                    {'anim':'models/hole-anim'})
            self.holeModel.reparentTo(self._mainRef.mainNode)

            self.holeModel.play('anim')

            self.holeModel.setPos(self.enemyNode.getPos(render))

            removeHoleDelay = 6
            taskMgr.doMethodLater(removeHoleDelay, self.removeHole, 'removeHoleTask')

    def removeHole(self, task):
        if self.holeModel != None:
            self.holeModel.cleanup()
            self.holeModel.delete()

            self.holeModel = None

        return task.done
