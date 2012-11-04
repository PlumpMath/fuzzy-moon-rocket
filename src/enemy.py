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
    _removeCorpseDelay = 3 # seconds before corpse is cleaned

    def __init__(self, mainRef, attributes):
        print("Enemy class instantiated")
        Unit.__init__(self)
        FSM.__init__(self, 'playerFSM')

        self._worldRef = mainRef
        self._playerRef = mainRef.player
        self._AIworldRef = mainRef.AIworld
        self._enemyListRef = mainRef.enemyList
        self._stateHandlerRef = mainRef.stateHandler

        self.topEnemyNode = mainRef.mainNode.attachNewNode('topEnemyNode')
        self.initEnemyNode()

        utils.enemyDictionary[self.enemyNode.getName()] = self

        self.loadEnemyModel(attributes.modelName)
        self.initAttributes(attributes)
        self.initEnemyAi()
        
        self.initEnemyCollisionHandlers()
        self.initEnemyCollisionSolids()

        self.request('Idle')

    def initEnemyNode(self):
        enemyName = 'enemy' + str(len(self._enemyListRef))
        self.enemyNode = self.topEnemyNode.attachNewNode(enemyName)
        self._enemyListRef.append(self)

    def loadEnemyModel(self, modelName):
        modelPrefix = 'models/'
        self.enemyModel = Actor(modelPrefix + modelName + '-model.egg', {
                'walk':modelPrefix+modelName+'-walk.egg',
                'attack':modelPrefix+modelName+'-attack.egg',
                'idle':modelPrefix+modelName+'-idle.egg',
                'awake':modelPrefix+modelName+'-awake.egg',
                'death1':modelPrefix+modelName+'-death1.egg',
                'death2':modelPrefix+modelName+'-death2.egg'
            })
        self.enemyModel.reparentTo(self.enemyNode)

        self.enemyNode.setPos(Point3.zero())

    def initAttributes(self, attributes):
        perceptionRangeMultiplier = 2
        rangeMultiplier = 8
        speedMultiplier = 3

        self.strength = attributes.strength
        self.constitution = attributes.constitution
        self.dexterity = attributes.dexterity

        self.mass = attributes.mass
        self.movementSpeed = speedMultiplier * attributes.movementSpeed
        self.perceptionRange = perceptionRangeMultiplier * rangeMultiplier * attributes.perceptionRange
        self.combatRange = rangeMultiplier * attributes.combatRange
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

        self.enemyUpdater = taskMgr.add(self.enemyUpdater, 'enemyUpdaterTask')

    def initEnemyCollisionHandlers(self):
        self.groundHandler = CollisionHandlerQueue()
        self.collPusher = CollisionHandlerPusher()

    def initEnemyCollisionSolids(self):
        pickerSphereCollNode = CollisionNode(self.enemyNode.getName())
        pickerSphereNodePath = self.enemyNode.attachNewNode(pickerSphereCollNode)
        pickerCollSphere = CollisionSphere(0, 0, 1, 6)
        pickerSphereCollNode.addSolid(pickerCollSphere)
        pickerSphereCollNode.setFromCollideMask(BitMask32.allOff())
        pickerSphereCollNode.setIntoCollideMask(BitMask32.bit(1))
        #sphereNodePath.show()

        collSphereNode = CollisionNode('enemyCollSphere')
        collSphere = CollisionSphere(0, 0, 1, 3)
        collSphereNode.addSolid(collSphere)

        collSphereNode.setIntoCollideMask(BitMask32.allOff())
        collSphereNode.setFromCollideMask(BitMask32.bit(2))
        
        self.sphereNode = self.enemyNode.attachNewNode(collSphereNode)
        #sphereNode.show()

        base.cTrav.addCollider(self.sphereNode, self.collPusher)
        self.collPusher.addCollider(self.sphereNode, self.enemyNode)

        groundRay = CollisionRay(0, 0, 10, 0, 0, -1)
        groundColl = CollisionNode('groundRay')
        groundColl.addSolid(groundRay)
        groundColl.setIntoCollideMask(BitMask32.allOff())
        groundColl.setFromCollideMask(BitMask32.bit(1))
        self.groundRayNode = self.topEnemyNode.attachNewNode(groundColl)
        #self.groundRayNode.show()

        base.cTrav.addCollider(self.groundRayNode, self.groundHandler)


    def checkGroundCollisions(self):
        zModifier = .5

        if self.groundHandler.getNumEntries() > 0:
            self.groundHandler.sortEntries()
            entries = []
            for i in range(self.groundHandler.getNumEntries()):
                entry = self.groundHandler.getEntry(i)
                entries.append(entry)

            entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                        x.getSurfacePoint(render).getZ()))

            if (len(entries) > 0) and (entries[0].getIntoNode().getName() == 'ground'):
                newZ = entries[0].getSurfacePoint(base.render).getZ()
                self.enemyNode.setZ(zModifier + newZ)

    def enemyUpdater(self, task):
        if self._stateHandlerRef.state != self._stateHandlerRef.PLAY:
            self.enemyModel.stop()
            # Do not do anything when paused
            return task.cont

        self.checkGroundCollisions()

        if self.getIsDead():
            return task.done

        if self._playerRef.getIsDead():
            return task.cont

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
        # If player is not within perception range
        else:
            if self.state != 'Idle':
                self.request('Idle')

        return task.cont

    def pursuePlayer(self, task):
        self.enemyAIBehaviors.pursue(self._playerRef.playerNode)
        self.enemyModel.loop('walk', fromFrame=0, toFrame=12)

        return task.done

    def enterIdle(self):
        #print('enemy enterIdle')
        self.enemyModel.pose('idle', 0) # Hold first frame

    def exitIdle(self):
        #print('enemy exitIdle')
        self.enemyModel.play('awake')

    def enterPursue(self):
        #print('enemy enterPursue')
        taskMgr.doMethodLater(1, self.pursuePlayer, 'pursuePlayerTask')

    def exitPursue(self):
        #print('enemy exitPursue')
        self.enemyAIBehaviors.removeAi('pursue')

    def enterCombat(self):
        #print('enemy enterCombat')
        self.enemyModel.stop()

        delay = Wait(1.5)
        
        self.attackSequence = Sequence()

        attackPlayer = Func(self.attackPlayer, self.attackSequence)
        attackEnemy = Func(self._playerRef.attackEnemy, self)

        if self.getInitiativeRoll() > self._playerRef.getInitiativeRoll():
            # Enemy wins initiative roll
            self.attackSequence.append(attackPlayer)
            self.attackSequence.append(delay)
            self.attackSequence.append(attackEnemy)
            self.attackSequence.append(delay)
        else:
            # Player wins initiative roll
            self.attackSequence.append(attackEnemy)
            self.attackSequence.append(delay)
            self.attackSequence.append(attackPlayer)
            self.attackSequence.append(delay)

        self.attackSequence.loop()

    def exitCombat(self):
        #print('enemy exitCombat')
        self.attackSequence.finish()

    def enterDeath(self):
        #print('enemy enterDeath')
        self.enemyAIBehaviors.removeAi('all')

        randomDeathAnim = 'death' + str(utils.getD2())
        self.enemyModel.play(randomDeathAnim)



    def attackPlayer(self, attackSequence):
        if self._stateHandlerRef.state != self._stateHandlerRef.PLAY:
            # Do not do anything when paused
            return 

        playerPos = self._playerRef.playerNode.getPos()
        enemyPos = self.enemyNode.getPos()

        if self.getIsDead():
            print('enemy is already dead')
            self.onDeath()

        elif self._playerRef.getIsDead():
            print('player is already dead')
            self.request('Idle')

        elif utils.getIsInRange(playerPos, enemyPos, self.combatRange) == False:
            print('player fled away from combat range')
            self.request('Pursue')

        elif utils.getIsInRange(playerPos, enemyPos, self.perceptionRange) == False:
            print('player fled away from perception range')
            self.request('Idle')

        else:
            print('Attack player!')
            self.enemyModel.play('attack', fromFrame=0, toFrame=12)

            # Make sure enemy is facing player when attacking
            pitchRoll = self.enemyNode.getP(), self.enemyNode.getR()
            self.enemyNode.lookAt(self._playerRef.playerNode)
            self.enemyNode.setHpr(self.enemyNode.getH()-180, *pitchRoll)

            if self._playerRef.getArmorClass() <= self.getAttackBonus():
                dmg = self.getDamageBonus()
                print('Enemy hit the player for ' + str(dmg) + ' damage')
                self._playerRef.receiveDamage(dmg)
            else:
                print('Enemy missed the player')

    def moveEnemy(self, x, y):
        self.enemyNode.setPos(x, y, 1)

    def suicide(self):
        # Remove AI behavior
        self.enemyAIBehaviors.removeAi('all')

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
        self.topEnemyNode.removeNode()

        # Remove enemy updater task
        self.enemyUpdater.remove()

        # Remove reference to main
        self._worldRef = None

    def onDeath(self):
        if self.getIsDead():
            # Award the player exp
            self._playerRef.receiveEXP(self.expAward)

            # Change state
            self.request('Death')

            # Remove enemy
            taskMgr.doMethodLater(self._removeCorpseDelay,
                             self.removeCorpse,
                            'RemoveCorpseTask')

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
        self.topEnemyNode.removeNode()

        # Remove enemy updater task
        self.enemyUpdater.remove()

        return task.done
