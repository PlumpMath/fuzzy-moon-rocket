#from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from panda3d.ai import *
from direct.interval.IntervalGlobal import *

import utils
from unit import Unit

class Enemy(FSM, Unit):

    #enemyDictionary[0] = None

    # Declare class variables
    EXPAward = 0
    #perceptionRange # Range that enemies will perceive player
    #combatRange 

    # Declare private variables
    _removeCorpseDelay = 3 # seconds before corpse is cleaned
    _inCombat = False

    def __init__(self, parentNode, enemyList, playerRef, EXPAward, AIworldRef, worldRef):
        print("Enemy class instantiated")
        Unit.__init__(self)
        FSM.__init__(self, 'playerFSM')

        self._enemyListRef = enemyList
        self._AIworldRef = AIworldRef
        self._playerRef = playerRef
        self._worldRef = worldRef

        enemyName = 'enemy' + str(len(self._enemyListRef))
        self.enemyNode = parentNode.attachNewNode(enemyName)
        self._enemyListRef.append(self.enemyNode)

        utils.enemyDictionary[self.enemyNode.getName()] = self

        self.loadEnemyModel()
        self.initAttributes()
        self.initEnemyAi()
        self.initEnemyCollision()

        self.setEXPReward(EXPAward)

    def loadEnemyModel(self):
        self.enemyModel = Actor("models/funny_sphere.egg")
        self.enemyModel.reparentTo(self.enemyNode)

        self.enemyNode.setPos(-2, 0, 1)
        self.enemyNode.setScale(0.1)

    def initEnemyCollision(self):
        self.sphereCollNode = CollisionNode(self.enemyNode.getName())
        self.sphereNodePath = self.enemyNode.attachNewNode(self.sphereCollNode)
        self.collSphere = CollisionSphere(0, 0, 0, 10)
        self.sphereCollNode.addSolid(self.collSphere)

    def initAttributes(self):
        self.strength = 16
        self.constitution = 14
        self.dexterity = 12

        self.movementSpeed = 0.1
        self.maxMovementSpeed = 5
        self.perceptionRange = 10
        self.combatRange = 1

        self.initHealth()

    def initEnemyAi(self):
        self.enemyAI = AICharacter('enemy',
                                self.enemyNode,
                                100, # Mass
                                self.movementSpeed, # Movt force
                                self.maxMovementSpeed) # Max force
        self._AIworldRef.addAiChar(self.enemyAI)

        self.enemyAIBehaviors = self.enemyAI.getAiBehaviors()
        #self.enemyAIBehaviors.obstacleAvoidance(1.0)

        enemyUpdateTask = taskMgr.add(self.enemyUpdater, 'enemyUpdaterTask')
        enemyUpdateTask.last = 0

        self.request('Idle')

    def enemyUpdater(self, task):
        deltaTime = task.time - task.last
        task.last = task.time

        #if deltaTime < .2:
        #    return task.cont

        #print('enemyUpdater')
        if self.state == 'Death':
            return task.done

        playerPos = self._playerRef.playerNode.getPos()
        enemyPos = self.enemyNode.getPos()

        # If player is within enemy perception range
        if utils.getIsInRange(playerPos, enemyPos, self.perceptionRange):
            #print('player in range')
            # If enemy is not doing anything
            if self.state == 'Idle':
                # Start pursuing
                self.request('Pursue')

            # If enemy is already pursueing
            elif self.state == 'Pursue':
                # If player is within combat range
                if utils.getIsInRange(playerPos, enemyPos, self.combatRange):
                    # Go to combat
                    self.request('Combat')

            # If already in combat, attack!
            elif self.state == 'Combat':
                pass # Combat is now handled in attackPlayer method and enterCombat
                #print('in combat')
        # If player is not within perception range
        else:
            # if in combat
            if self.state == 'Combat':
                pass # Combat is now handled in attackPlayer method and enterCombat

            elif self.state != 'Idle':
                self.request('Idle')

        return task.cont

    def enterPursue(self):
        print('enterPursue')
        self.enemyAIBehaviors.pursue(self._playerRef.playerNode)

    def exitPursue(self):
        print('exitPursue')
        self.enemyAIBehaviors.removeAi('pursue')

    def enterCombat(self):
        print('enterCombat')

        delay = Wait(1.5)
        
        attackSequence = Sequence()

        attackPlayer = Func(self.attackPlayer, attackSequence)
        attackEnemy = Func(self._playerRef.attackEnemy, self)

        if self.getInitiativeRoll() > self._playerRef.getInitiativeRoll():
            # Enemy wins initiative roll
            attackSequence.append(attackPlayer)
            attackSequence.append(delay)
            attackSequence.append(attackEnemy)
            attackSequence.append(delay)
        else:
            # Player wins initiative roll
            attackSequence.append(attackEnemy)
            attackSequence.append(delay)
            attackSequence.append(attackPlayer)
            attackSequence.append(delay)

        attackSequence.loop()


    def exitCombat(self):
        print('exitCombat')

    def enterDeath(self):
        print('enterDeath')
        self.enemyAIBehaviors.removeAi('all')

    def enterIdle(self):
        print('enterIdle')
        self.enemyAIBehaviors.wander(2.5, 0, 5)

    def exitIdle(self):
        print('exitIdle')
        self.enemyAIBehaviors.removeAi('wander')

    def attackPlayer(self, attackSequence):
        playerPos = self._playerRef.playerNode.getPos()
        enemyPos = self.enemyNode.getPos()

        if self.getIsDead():
            print('enemy is already dead')
            self.onDeath()
            attackSequence.finish()

        elif self._playerRef.getIsDead():
            print('player is already dead')
            self.request('Idle')
            attackSequence.finish()

        elif utils.getIsInRange(playerPos, enemyPos, self.combatRange) == False:
            print('player fled away from combat range')
            self.request('Pursue')
            attackSequence.finish()

        elif utils.getIsInRange(playerPos, enemyPos, self.perceptionRange) == False:
            print('player fled away from perception range')
            self.request('Idle')
            attackSequence.finish()

        else:
            # Play attack animation
            print('Attack player!')
            if self._playerRef.getArmorClass() <= self.getAttackBonus():
                dmg = self.getDamageBonus()
                print('Enemy hit the player for ' + str(dmg) + ' damage')
                self._playerRef.receiveDamage(dmg)
            else:
                print('Enemy missed the player')

    def setEXPReward(self, value):
        self.EXPAward = value

    def onDeath(self):
        if self.getIsDead():
            # Award the player exp
            self._playerRef.receiveEXP(self.EXPAward)

            # Change state
            self.request('Death')

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

        # Cleanup FSM
        self.cleanup()

        # Remove the enemy node
        self.enemyNode.removeNode()

        return task.done

    def getEnemyNode(self):
        return self.enemyNode

    def moveEnemy(self, x, y):
        self.enemyNode.setPos(x, y, 1)
