#from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from panda3d.ai import *
from direct.interval.IntervalGlobal import *

from collections import namedtuple

import utils
from elements import HealthGoblet
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

dropChanceFactor = 5
maxDropChance = 50
dropChance = 0

class Enemy(FSM, Unit):

    # Declare private variables
    _enemyActive = False
    _removeCorpseDelay = 2 # seconds before corpse is cleaned

    def __init__(self, mainRef, attributes):
        print("Enemy instantiated")
        Unit.__init__(self)
        FSM.__init__(self, 'playerFSM')

        self._mainRef = mainRef
        self._playerRef = mainRef.player
        self._AIworldRef = mainRef.AIworld
        self._enemyListRef = mainRef.enemyList
        self._ddaHandlerRef = mainRef.DDAHandler
        self._stateHandlerRef = mainRef.stateHandler
        self._scenarioHandlerRef = mainRef.scenarioHandler

        #self.topEnemyNode = mainRef.mainNode.attachNewNode('topEnemyNode')
        self.initEnemyNode(mainRef.mainNode)

        utils.enemyDictionary[self.enemyNode.getName()] = self

        self.loadEnemyModel(attributes.modelName)
        self.initAttributes(attributes)
        self.initEnemyAi()

        self.initEnemyDDA()

        self.initEnemyCollisionHandlers()
        self.initEnemyCollisionSolids()

        #self.request('Idle')
        self.request('Disabled')

        # Start enemy updater task
        self.enemyUpdaterTask = taskMgr.add(self.enemyUpdater, 'enemyUpdaterTask')

    def initEnemyNode(self, parentNode):
        enemyName = 'enemy' + str(len(self._enemyListRef))
        self.enemyNode = parentNode.attachNewNode(enemyName)
        self._enemyListRef.append(self)

    def loadEnemyModel(self, modelName):
        modelPrefix = 'models/' + modelName
        self.enemyModel = Actor(modelPrefix + '-model', {
                'walk':modelPrefix+'-walk',
                'attack':modelPrefix+'-attack',
                'idle':modelPrefix+'-idle',
                'awake':modelPrefix+'-awake',
                'stop':modelPrefix+'-stop',
                'hit':modelPrefix+'-hit',
                'death1':modelPrefix+'-death1',
                'death2':modelPrefix+'-death2'
            })
        self.enemyModel.reparentTo(self.enemyNode)

        self.enemyNode.setPos(Point3.zero())

        self.enemyNode.setDepthOffset(-1)

    def initAttributes(self, attributes):
        perceptionRangeMultiplier = 1.2
        combatRangeMultiplier = .3
        speedMultiplier = .1

        self.strength = attributes.strength
        self.constitution = attributes.constitution
        self.dexterity = attributes.dexterity

        self.mass = attributes.mass
        self.movementSpeed = speedMultiplier * attributes.movementSpeed
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
                self.increaseLevel()

        self.expAward = attributes.expAward

        self.initHealth()

    def initEnemyDDA(self):
        if self._scenarioHandlerRef.getHasDDA():
            maxLevelDifference = self._ddaHandlerRef.maxLevelDifference

            # Level enemy up to player's level minus maxLevelDifference
            levelDifference = self._playerRef.level - self.level
            if levelDifference >= maxLevelDifference:
                for i in range (levelDifference-maxLevelDifference):
                    self.increaseLevel()

    def getAttackBonus(self):
        modifier = self.getStrengthModifier() if self.getStrengthModifier() > self.getDexterityModifier() else self.getDexterityModifier()
        ab = self.attackBonus + (self.level / 2) + modifier# + utils.getD20()

        if self._scenarioHandlerRef.getHasDDA():
            attackBonusModifier = self._ddaHandlerRef.attackBonusModifier
            if attackBonusModifier < 0:
                ab -= attackBonusModifier
                if ab < 1:
                    ab = 1

        return ab + utils.getD20()

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

    def slowMovementByPercentage(self, percentage=30, slowDuration=20):
        #print self.enemyNode.getName(), ' slowed by ', percentage, ' %'
        oldSpeed = self.movementSpeed
        newSpeed = ((100.0 - percentage) / 100.0) * oldSpeed

        if newSpeed < 1.0:
            newSpeed = 1.0

        self.movementSpeed = newSpeed

        taskMgr.doMethodLater(slowDuration, self.removeSlowMovement, 'removeSlowMovementTask', extraArgs=[oldSpeed], appendTask=True)

    def removeSlowMovement(self, oldSpeed, task):
        self.movementSpeed = oldSpeed
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

            # If enemy is disabled
            elif self.state == 'Disabled':
                if self.enemyAI.getMaxForce() != self.movementSpeed:
                    self.enemyAI.setMaxForce(self.movementSpeed)

        # If player is not within perception range
        else:
            if self.state != 'Idle':
                self.request('Idle')

        return task.cont

    def pursuePlayer(self):
        taskMgr.add(self.pursue, 'pursueTask')

    def pursue(self, task):
        if self.state == 'Pursue' and not self.getIsDead():
            pitchRoll = self.enemyNode.getP(), self.enemyNode.getR()
            self.enemyNode.headsUp(self._playerRef.playerNode)
            self.enemyNode.setHpr(self.enemyNode.getH()-180, *pitchRoll)

            speed = -self.movementSpeed * globalClock.getDt()
            self.enemyNode.setFluidPos(self.enemyNode, 0, speed, 0)

            return task.cont
        else:
            task.done

    def enterIdle(self):
        #print 'enemy enterIdle'
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

        # Only awake enemy if it comes from idle
        if self.isSleeping: 
            self.isSleeping = False

            awakeEnemy = self.enemyModel.actorInterval('awake', loop=0)
            self.awakeSequence = Sequence(awakeEnemy, loopWalkEnemy, Func(self.pursuePlayer))
        else:
            self.awakeSequence = Sequence(loopWalkEnemy, Func(self.pursuePlayer))

        self.awakeSequence.start()

    def exitPursue(self):
        #print('enemy exitPursue')
        self.awakeSequence.finish()

    def enterCombat(self):
        #print('enemy enterCombat')
        self.enemyModel.stop()

        attackDelay = self.getInitiativeRoll()
        self.attackTask = taskMgr.doMethodLater(attackDelay, self.attackPlayer, 'attackPlayerTask')

    def enterDisabled(self):
        #print 'enterDisable'
        pass

    def exitDisabled(self):
        #print 'exitDisable'
        pass

    def exitCombat(self):
        #print('enemy exitCombat')
        taskMgr.remove(self.attackTask)

    def enterDeath(self):
        #print('enemy enterDeath')
        self.enemyAIBehaviors.removeAi('all')
        randomDeathAnim = 'death' + str(utils.getD2())
        self.enemyModel.play(randomDeathAnim)


    def attack(self, other):
        if not self.getIsDead() and not other.getIsDead():
            if self.getAttackBonus() >= other.getArmorClass():
                dmg = self.getDamageBonus()
                #print(self.getName(), ' damaged ', other.getName(), ' for ', dmg, ' damage')
                other.receiveDamage(dmg)

                return 2 # Returns 2 when self damages other

            return 1 # Returns 1 when self attacks other, but misses

        return 0 # Returns 0 when either self or other is dead

    def attackPlayer(self, task):
        if self._stateHandlerRef.state != self._stateHandlerRef.PLAY or not self._enemyActive:
            # Do not do anything when paused
            return task.again

        if self._playerRef.getIsDead():
            print('player is already dead')
            self.request('Idle')
            return task.done

        elif self.getIsDead():
            return task.done

        else:
            #print('Attack player!')
            # Make sure enemy is facing player when attacking
            pitchRoll = self.enemyNode.getP(), self.enemyNode.getR()
            self.enemyNode.headsUp(self._playerRef.playerNode)
            self.enemyNode.setHpr(self.enemyNode.getH()-180, *pitchRoll)

            attacked = self.attack(self._playerRef)
            if attacked != 0:
                self.playAttackAnimation()
                if attacked == 2:
                    self._playerRef.playerModel.play('hit')

            return task.again

    def playAttackAnimation(self):
        self.enemyModel.play('attack', fromFrame=0, toFrame=12)

    def playHitAnimation(self):
        self.enemyModel.play('hit')

    def moveEnemy(self, x, y):
        self.enemyNode.setPos(x, y, .01)

    def handleHealthGlobe(self):
        global dropChanceFactor
        global dropChance
        global maxDropChance

        # if we drop, create health goblet
        chance = dropChanceFactor + dropChance
        if self._scenarioHandlerRef.getHasDDA():
            chance *= self._ddaHandlerRef.healthGobletModifier

        if utils.getD100() <= chance:
            HealthGoblet(self._mainRef, self)
            print 'dropping health goblet'
        # Otherwise, increase dropChance
        else:
            if dropChance+dropChanceFactor <= maxDropChance:
                dropChance += dropChanceFactor

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

            # Increase DDA death count
            if self._scenarioHandlerRef.getHasDDA():
                self._ddaHandlerRef.enemyDeathCount += 1

            # Handle health globe
            self.handleHealthGlobe()

            # Remove enemy corpse and clean up
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

        # Remove the enemy node
        self.enemyNode.removeNode()
        #self.topEnemyNode.removeNode()

        # Remove enemy updater tasks
        taskMgr.remove(self.enemyUpdaterTask)

        # Remove the passive regeneration task (from Unit class)
        self.removePassiveRegeneration()

        # Remove references
        self._mainRef = None
        self._playerRef = None
        self._AIworldRef = None
        self._enemyListRef = None
        self._stateHandlerRef = None

        return task.done
