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

        rangeMultiplier = 1.5
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

        self.enemyNode.setPos(Point3.zero())

        self.enemyNode.setDepthOffset(-1)

    def enterIdle(self):
        #print 'enemy enterIdle'
        idleTime = 60.0 * 2.0

        stopEnemy = self.enemyModel.actorInterval('pursue-to-idle', startFrame=0, endFrame=12)
        idleEnemy = self.enemyModel.actorInterval('idle-walk-to-dig', startFrame=0, endFrame=60)
        digHole = Parallel(Func(self.createHole), self.enemyModel.actorInterval('idle-walk-to-dig-to-sleep', startFrame=0, endFrame=120))
        #suicide = Func(self.suicide)

        self.stopSequence = Sequence(stopEnemy, idleEnemy,  digHole)
        self.stopSequence.start()

        self.isSleeping = True

    def enterPursue(self):
        #print('enemy enterPursue')
        loopWalkEnemy = Func(self.enemyModel.loop, 'pursue', fromFrame=0, toFrame=24)

        # Only awake enemy if it comes from idle
        if self.isSleeping:
            self.isSleeping = False

            awakeEnemy = self.enemyModel.actorInterval('idle-walk-to-pursue', startFrame=0, endFrame=24)
            self.awakeSequence = Sequence(awakeEnemy, loopWalkEnemy, Func(self.pursuePlayer))
        else:
            self.awakeSequence = Sequence(loopWalkEnemy, Func(self.pursuePlayer))

        self.awakeSequence.start()

    def enterDeath(self):
        #print('enemy enterDeath')
        self.enemyAIBehaviors.removeAi('all')
        randomDeathAnim = 'death' + str(utils.getDX(3))
        self.enemyModel.play(randomDeathAnim, fromFrame=0, toFrame=12)

    def playAttackAnimation(self):
        randomAttackAnim = 'attack' + str(utils.getD4())
        self.enemyModel.play(randomAttackAnim, fromFrame=0, toFrame=12)

    def playHitAnimation(self):
        randomHitAnim = 'hit' + str(utils.getDX(2))
        self.enemyModel.play(randomHitAnim, fromFrame=0, toFrame=12)

    def createHole(self):
        if self.holeModel == None:
            self.holeModel = Actor('models/hole-model',
                                    {'anim':'models/hole-anim'})
            self.holeModel.reparentTo(self._mainRef.mainNode)

            self.holeModel.play('anim', fromFrame=0, toFrame=120)

            pos = self.enemyNode.getPos(render)
            #self.holeModel.setPos(pos.getX(), pos.getY()+.5, pos.getZ()+.01)
            self.holeModel.setPos(pos)

            removeHoleDelay = 6
            taskMgr.doMethodLater(removeHoleDelay, self.removeHole, 'removeHoleTask')

    def removeHole(self, task):
        if self.holeModel != None:
            self.holeModel.cleanup()
            self.holeModel.delete()

            self.holeModel = None

        return task.done
