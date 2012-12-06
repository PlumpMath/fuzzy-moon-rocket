from panda3d.core import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *

import enemy
import utils

class Digger(enemy.Enemy):

    def __init__(self, mainRef):
        enemy.Enemy.__init__(self, mainRef, enemy.koboldSkirmisher) # Change to correct kobold

        self.holeModel = None
        self.isUnderground = False

    def initAttributes(self, attributes):
        super(Digger, self).initAttributes(attributes)

        rangeMultiplier = 1.75
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
        self._soundsHandlerRef.playDiggerIdle()

        stopEnemy = self.enemyModel.actorInterval('pursue-to-idle', startFrame=0, endFrame=12)
        idleEnemy = Func(self.enemyModel.loop, 'idle-walk-to-dig', fromFrame=0, toFrame=60)

        self.stopSequence = Sequence(stopEnemy, idleEnemy)
        self.stopSequence.start()

        self.isSleeping = True

    def setIsUnderground(self):
        self.isUnderground = True

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
        self._soundsHandlerRef.playDiggerDeath()
        self.enemyAIBehaviors.removeAi('all')
        randomDeathAnim = 'death' + str(utils.getDX(3))
        self.enemyModel.play(randomDeathAnim, fromFrame=0, toFrame=12)

    def playAttackAnimation(self):
        self._soundsHandlerRef.playDiggerAttack()
        randomAttackAnim = 'attack' + str(utils.getD4())
        self.enemyModel.play(randomAttackAnim, fromFrame=0, toFrame=12)

    def playHitAnimation(self):
        randomHitAnim = 'hit' + str(utils.getDX(2))
        self.enemyModel.play(randomHitAnim, fromFrame=0, toFrame=12)
