#from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from panda3d.ai import *
from direct.interval.IntervalGlobal import *

from collections import namedtuple

import utils
from unit import Unit

Attributes = namedtuple('Attributes', ['modelName', 'strength', 'constitution', 'dexterity', 'expAward', 'perceptionRange', 'combatRange', 'movementSpeed', 'mass', 'initiativeBonus', 'fixedHealthPoints', 'armorClass', 'startLevel', 'damageBonus', 'damageRange', 'attackBonus'])

# Kobold Minion uses fixedHealthPoints, which given any other value than 0 will fix the units health to that value
# Mass should be thought of as approximate weight in kilograms
koboldMinion = Attributes(modelName='probe', strength=8, constitution=12, dexterity=16, initiativeBonus=3, fixedHealthPoints=1, armorClass=15, movementSpeed=6, perceptionRange=2, combatRange=1, mass=60, expAward=25, startLevel=1, damageRange=0, damageBonus=4, attackBonus=5)

# Kobold Skirmisher has combatRange of 1, means very short range (melee)
# Perception +1 bonus gives perception range 2
koboldSkirmisher = Attributes(modelName='probe', strength=8, constitution=11, dexterity=16, initiativeBonus=5, fixedHealthPoints=27, armorClass=15, movementSpeed=6, perceptionRange=1, combatRange=1, mass=60, expAward=100, startLevel=1, damageRange=8, damageBonus=0, attackBonus=6)

# Kobold Slinger has combat range 3 (ranged), which means that perception +1 gives perception range 4
# Damage bonus 3 gives constant +3 to damage, while damage range 4 means 1d4 (1-4)
koboldSlinger = Attributes(modelName='probe', strength=9, constitution=12, dexterity=17, fixedHealthPoints=24, initiativeBonus=3, perceptionRange=4, combatRange=3, movementSpeed=6, armorClass=13, mass=60, expAward=100, startLevel=2, damageBonus=3, damageRange=4, attackBonus=5)

# Enemy unit automatically levels up to startLevel
koboldWyrmpriest = Attributes(modelName='probe', strength=9, constitution=12, dexterity=16, initiativeBonus=4, fixedHealthPoints=36, armorClass=17, movementSpeed=6, combatRange=1, perceptionRange=5, mass=70, expAward=150, startLevel=3, damageRange=8, damageBonus=0, attackBonus=7)

class Enemy(FSM, Unit):

    # Declare private variables
    _enemyActive = False
    _removeCorpseDelay = 2 # seconds before corpse is cleaned

    def __init__(self, mainRef, attributes):
        print("Enemy class instantiated")
        Unit.__init__(self)
        FSM.__init__(self, 'playerFSM')

        self._worldRef = mainRef
        self._playerRef = mainRef.player
        self._AIworldRef = mainRef.AIworld
        self._enemyListRef = mainRef.enemyList
        self._ddaHandlerRef = mainRef.DDAHandler
        self._stateHandlerRef = mainRef.stateHandler

        #self.topEnemyNode = mainRef.mainNode.attachNewNode('topEnemyNode')
        self.initEnemyNode(mainRef.mainNode)

        utils.enemyDictionary[self.enemyNode.getName()] = self

        self.loadEnemyModel(attributes.modelName)
        self.initAttributes(attributes)
        self.initEnemyAi()

        self.initEnemyCollisionHandlers()
        self.initEnemyCollisionSolids()

        self.request('Idle')

        # Start enemy updater task
        self.enemyUpdaterTask = taskMgr.add(self.enemyUpdater, 'enemyUpdaterTask')

    def initEnemyNode(self, parentNode):
        enemyName = 'enemy' + str(len(self._enemyListRef))
        self.enemyNode = parentNode.attachNewNode(enemyName)
        self._enemyListRef.append(self)

    def loadEnemyModel(self, modelName):
        modelPrefix = 'models/'
        self.enemyModel = Actor(modelPrefix + modelName + '-model', {
                'walk':modelPrefix+modelName+'-walk',
                'attack':modelPrefix+modelName+'-attack',
                'idle':modelPrefix+modelName+'-idle',
                'awake':modelPrefix+modelName+'-awake',
                'stop':modelPrefix+modelName+'-stop',
                'hit':modelPrefix+modelName+'-hit',
                'death1':modelPrefix+modelName+'-death1',
                'death2':modelPrefix+modelName+'-death2'
            })
        self.enemyModel.reparentTo(self.enemyNode)
        #self.enemyModel.setH(-180)

        self.enemyNode.setPos(Point3.zero())

        self.enemyNode.setDepthOffset(-1)

    def initAttributes(self, attributes):
        perceptionRangeMultiplier = 1.2
        combatRangeMultiplier = .6
        speedMultiplier = .2

        self.strength = attributes.strength
        self.constitution = attributes.constitution
        self.dexterity = attributes.dexterity

        self.mass = attributes.mass
        self.movementSpeed = self._ddaHandlerRef.SpeedFactor * speedMultiplier * attributes.movementSpeed
        self.perceptionRange = perceptionRangeMultiplier * attributes.perceptionRange
        self.combatRange = combatRangeMultiplier * attributes.combatRange
        self.attackBonus = attributes.attackBonus
        self.damageBonus = attributes.damageBonus
        self.damageRange = attributes.damageRange
        self.initiativeBonus = attributes.initiativeBonus
        self.fixedHealthPoints = attributes.fixedHealthPoints
        self.armorClass = attributes.armorClass

        if attributes.startLevel > 1:
            for i in range(attributes.startLevel-1):
                enemy.increaseLevel()

        self.expAward = attributes.expAward

        self.initHealth()

    def initEnemyAi(self):
        self.enemyAI = AICharacter('enemy',
                                self.enemyNode,
                                self.mass, # Mass
                                0.1, # Movt force
                                self.movementSpeed) # Max force
        self._AIworldRef.addAiChar(self.enemyAI)

        self.enemyAIBehaviors = self.enemyAI.getAiBehaviors()
        #self.enemyAIBehaviors.obstacleAvoidance(1.0)

    def initEnemyCollisionHandlers(self):
        self.groundHandler = CollisionHandlerQueue()
        self.collPusher = CollisionHandlerPusher()

    def initEnemyCollisionSolids(self):
        # Enemy ground ray
        groundRay = CollisionRay(0, 0, 2, 0, 0, -1)
        groundColl = CollisionNode('enemyGroundRay')
        groundColl.addSolid(groundRay)

        groundColl.setIntoCollideMask(BitMask32.allOff())
        groundColl.setFromCollideMask(BitMask32.bit(1))

        self.groundRayNode = self.enemyNode.attachNewNode(groundColl)
        #self.groundRayNode.show()

        base.cTrav.addCollider(self.groundRayNode, self.groundHandler)

        # Enemy collision sphere
        collSphereNode = CollisionNode('enemyCollSphere')
        collSphere = CollisionSphere(0, 0, 0.1, 0.2)
        collSphereNode.addSolid(collSphere)

        collSphereNode.setIntoCollideMask(BitMask32.allOff())
        collSphereNode.setFromCollideMask(BitMask32.bit(2))
        
        self.sphereNode = self.enemyNode.attachNewNode(collSphereNode)
        #sphereNode.show()

        base.cTrav.addCollider(self.sphereNode, self.collPusher)
        self.collPusher.addCollider(self.sphereNode, self.enemyNode)

        # Enemy picker collision sphere
        pickerSphereCollNode = CollisionNode(self.enemyNode.getName())
        pickerCollSphere = CollisionSphere(0, 0, 0, 0.5)
        pickerSphereCollNode.addSolid(pickerCollSphere)

        pickerSphereCollNode.setFromCollideMask(BitMask32.allOff())
        pickerSphereCollNode.setIntoCollideMask(BitMask32.bit(1))

        self.pickerNode = self.enemyNode.attachNewNode(pickerSphereCollNode)
        #sphereNodePath.show()

        # Enemy attack collision sphere
        attackCollSphereNode = CollisionNode(self.enemyNode.getName()+'atkSph')
        attackCollSphere = CollisionSphere(0, 0, 0.1, 0.15)
        attackCollSphereNode.addSolid(attackCollSphere)

        attackCollSphereNode.setIntoCollideMask(BitMask32.bit(3))
        attackCollSphereNode.setFromCollideMask(BitMask32.allOff())

        attackSphereNode = self.enemyNode.attachNewNode(attackCollSphereNode)
        #attackSphereNode.show()

    def slowMovementByPercentage(self, percentage=30, slowDuration=30):
        #print self.enemyNode.getName(), ' slowed by ', percentage, ' %'
        oldForce = self.enemyAI.getMaxForce()
        newForce = ((100.0 - percentage) / 100.0) * oldForce

        if newForce < 0.15:
            newForce = 0.15

        self.enemyAI.setMaxForce(newForce)

        taskMgr.doMethodLater(slowDuration, self.removeSlowMovement, 'removeSlowMovementTask', extraArgs=[oldForce], appendTask=True)

    def removeSlowMovement(self, oldForce, task):
        self.enemyAI.setMaxForce(oldForce)
        return task.done

    def checkGroundCollisions(self):
        if self.groundHandler.getNumEntries() > 0:
            self.groundHandler.sortEntries()
            entries = []
            for i in range(self.groundHandler.getNumEntries()):
                entry = self.groundHandler.getEntry(i)
                #print('entry:', entry)
                entries.append(entry)

            entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                         x.getSurfacePoint(render).getZ()))

            for i in range(len(entries)):
                if entries[i].getIntoNode().getName()[:6] == 'ground':
                    #print('entryFound:', entries[0])
                    newZ = entries[i].getSurfacePoint(base.render).getZ()
                    self.enemyNode.setZ(newZ)
                    #print('enemyZ:', newZ)
                    break;

    def enemyUpdater(self, task):
        if self._stateHandlerRef.state != self._stateHandlerRef.PLAY or not self._enemyActive:
            self.enemyModel.stop()
            # Do not do anything when paused
            return task.cont

        self.checkGroundCollisions()

        if self.getIsDead():
            self.onDeath()
            return task.done

        if self._playerRef.getIsDead():
            return task.cont

        playerPos = self._playerRef.playerNode.getPos()
        enemyPos = self.enemyNode.getPos()

        # If player is within enemy perception range
        if utils.getIsInRange(playerPos, enemyPos, self.perceptionRange):

            # If enemy is not doing anything
            if self.state == 'Idle':
                # Start pursuing
                if self.state != 'Pursue':
                    self.request('Pursue')

            # If enemy is already pursueing
            elif self.state == 'Pursue':
                # If player is within combat range
                if utils.getIsInRange(playerPos, enemyPos, self.combatRange):
                    #print 'enemy go to combat'
                    # Go to combat
                    if self.state != 'Combat':
                        self.request('Combat')

            # If enemy is already in combat
            elif self.state == 'Combat':
                # If player has moved out of combat range
                if not utils.getIsInRange(playerPos, enemyPos, self.combatRange):
                    # Start pursuing
                    if self.state != 'Pursue':
                        self.request('Pursue')

        # If player is not within perception range
        else:
            if self.state != 'Idle':
                self.request('Idle')

        return task.cont


    def enterIdle(self):
        print 'enemy enterIdle'
        stopEnemy = self.enemyModel.actorInterval('stop', loop=0)
        idleEnemy = self.enemyModel.actorInterval('idle', startFrame=0, endFrame=1, loop=0)

        self.stopSequence = Sequence(stopEnemy, idleEnemy)
        self.stopSequence.start()

        self.isSleeping = True

    def exitIdle(self):
        #print('enemy exitIdle')
        self.stopSequence.finish()

    def enterPursue(self):
        #print('enemy enterPursue')
        loopWalkEnemy = Func(self.enemyModel.loop, 'walk', fromFrame=0, toFrame=12)
        pursuePlayer = Func(self.enemyAIBehaviors.pursue, self._playerRef.playerNode)

        # Only awake enemy if it comes from idle
        if self.isSleeping: 
            self.isSleeping = False

            awakeEnemy = self.enemyModel.actorInterval('awake', loop=0)
            self.awakeSequence = Sequence(awakeEnemy, loopWalkEnemy, pursuePlayer)
        else:
            self.awakeSequence = Sequence(loopWalkEnemy, pursuePlayer)

        self.awakeSequence.start()

    def exitPursue(self):
        #print('enemy exitPursue')
        self.awakeSequence.finish()
        self.enemyAIBehaviors.removeAi('all')

    def enterCombat(self):
        #print('enemy enterCombat')
        self.enemyModel.stop()

        self.attackTask = taskMgr.doMethodLater(0.1, self.attackPlayer, 'attackPlayerTask')

    def enterDisabled(self):
        print 'enterDisable'

    def exitDisabled(self):
        print 'exitDisable'

    def exitCombat(self):
        #print('enemy exitCombat')
        taskMgr.remove(self.attackTask)

    def enterDeath(self):
        #print('enemy enterDeath')
        self.enemyAIBehaviors.removeAi('all')
        randomDeathAnim = 'death' + str(utils.getD2())
        self.enemyModel.play(randomDeathAnim)



    def attackPlayer(self, task):
        if self._stateHandlerRef.state != self._stateHandlerRef.PLAY or not self._enemyActive:
            # Do not do anything when paused
            return task.again

        attackDelay = utils.getScaledValue(self.getInitiativeRoll(), 0.75, 2.0, 2.0, 30.0)
        if task.delayTime != attackDelay:
            task.delayTime = attackDelay

        if self._playerRef.getIsDead():
            print('player is already dead')
            self.request('Idle')
            return task.done

        else:
            #print('Attack player!')
            # Make sure enemy is facing player when attacking
            pitchRoll = self.enemyNode.getP(), self.enemyNode.getR()
            self.enemyNode.headsUp(self._playerRef.playerNode)
            self.enemyNode.setHpr(self.enemyNode.getH()-180, *pitchRoll)

            self.enemyModel.play('attack', fromFrame=0, toFrame=12)
            self.attack(self._playerRef)

            return task.again

    def moveEnemy(self, x, y):
        self.enemyNode.setPos(x, y, .01)

    def suicide(self):
        print('suicide: ', self)
        # Remove AI behavior
        self.enemyAIBehaviors.removeAi('all')

        # Remove enemy picker sphere (handlerQueue)
        self.pickerNode.removeNode()

        taskMgr.add(self.removeCorpse, 'removeCorpseTask')

    def onDeath(self):
        if self.getIsDead():
            # Remove AI behavior
            self.enemyAIBehaviors.removeAi('all')

            # Award the player exp
            self._playerRef.receiveEXP(self.expAward)

            # Remove enemy picker sphere (handlerQueue)
            self.pickerNode.removeNode()

            # Change state
            self.request('Death')

            # Remove enemy
            taskMgr.doMethodLater(self._removeCorpseDelay, self.removeCorpse, 'removeCorpseTask')

    def removeCorpse(self, task):
        # Remove enemy collision sphere (pusher)
        self.sphereNode.removeNode()

        # Stop the collision pusher
        self.collPusher = None

        # Remove enemy from enemyList
        self._enemyListRef.remove(self)

        # Cleanup the enemy model
        self.enemyModel.cleanup()
        self.enemyModel.delete()

        # Cleanup FSM
        self.cleanup()

        # Cleanup attack sequence
        self.attackSequence = None

        # Remove the enemy node
        self.enemyNode.removeNode()
        #self.topEnemyNode.removeNode()

        # Remove enemy updater tasks
        taskMgr.remove(self.enemyUpdaterTask)

        # Remove the passive regeneration task (from Unit class)
        self.removePassiveRegeneration()

        # Remove references
        self._worldRef = None
        self._playerRef = None
        self._AIworldRef = None
        self._enemyListRef = None
        self._stateHandlerRef = None

        return task.done
