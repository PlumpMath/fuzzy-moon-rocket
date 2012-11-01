from panda3d.core import *
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from panda3d.ai import *

import utils
from unit import Unit

class Player(FSM, Unit):

    # Declare private variables
    _cameraYModifier = -75 # Relative to player Y position
    _cameraZModifier = 60 # Relative to player Z position

    _currentTarget = None

    def __init__(self, mainRef, playerStartPos, playerExitPos):
        print("Player class instantiated")
        Unit.__init__(self)
        FSM.__init__(self, 'playerFSM')

        self._AIworldRef = mainRef.AIworld
        
        self.playerNode = mainRef.mainNode.attachNewNode('playerNode')

        self.initPlayerAttributes()
        self.initPlayerModel()
        self.initPlayerCamera()

        self.initPlayerAi()

        self.initPlayerMovement(playerStartPos, playerExitPos)
        self.initPlayerCollisionHandlers()
        self.initPlayerCollisionSolids()

        self.initSelector()

        # Start mouse picking and movement
        utils.MouseHandler(self)

        # Start player update task
        playerUpdateTask = taskMgr.add(self.playerUpdate, 'playerUpdateTask')
        playerUpdateTask.last = 0

        # Initialize player FSM state
        self.request('Idle')

    def initPlayerAttributes(self):
        # Initialize player attributes
        self.strength = 16
        self.constitution = 14
        self.dexterity = 10

        self.combatRange = 10 # Melee
        self.movementSpeed = 20 # ?
        self.attackBonus = 6 # ?
        self.damageBonus = 0 # ?
        self.damageRange = 8 # = Longsword
        self.initiativeBonus = 1 # ?
        self.armorClass = 10 + 8 # Base armor class + fullplate armor
        self.mass = 90

        self.initHealth()

    def initPlayerModel(self):
        # Initialize the player model (Actor)
        modelPrefix = 'models/player-'
        self.playerModel = Actor(modelPrefix + 'model.egg', {
            'run':modelPrefix+'run.egg',
            'attack':modelPrefix+'attack.egg',
            'stop':modelPrefix+'stop.egg',
            'death':modelPrefix+'death.egg',
            'idle':modelPrefix+'idle.egg'
            })

        self.playerModel.reparentTo(self.playerNode)

        # Make sure that visible geometry does not collide
        self.playerModel.setCollideMask(BitMask32.allOff())
        # Model is backwards, fix by changing the heading
        self.playerModel.setH(180)

        # Initialize selector variable
        self.selector = None

    def initPlayerCamera(self): 
        # Initialize the camera
        base.disableMouse()
        base.camera.setPos(self.playerNode.getX(),
                           self.playerNode.getY() + self._cameraYModifier, 
                           self.playerNode.getZ() + self._cameraZModifier)
        base.camera.lookAt(self.playerNode)

        self.stopCamera = False

    def initPlayerAi(self):
        self.playerAi = AICharacter('player', self.playerNode, self.mass, 0.05, self.movementSpeed)
        self._AIworldRef.addAiChar(self.playerAi)
        self.playerAiBehaviors = self.playerAi.getAiBehaviors()
        #self.playerAiBehaviors.obstacleAvoidance(1.0)

    def initPlayerMovement(self, playerStartPos, playerExitPos):
        # Make sure the player starts at the starting position
        self.exitPos = playerExitPos
        self.startPos = playerStartPos
        self.playerNode.setPos(playerStartPos)
        self.destination = Point3(playerStartPos)
        self.velocity = Vec3.zero()

        self.playerNode.lookAt(playerExitPos)

    def initPlayerCollisionHandlers(self):
        self.groundHandler = CollisionHandlerQueue()
        self.collPusher = CollisionHandlerPusher()

    def initPlayerCollisionSolids(self):
        groundRay = CollisionRay(0, 0, 10, 0, 0, -1)
        groundColl = CollisionNode('groundRay')
        groundColl.addSolid(groundRay)
        groundColl.setIntoCollideMask(BitMask32.allOff())
        groundColl.setFromCollideMask(BitMask32.bit(1))
        self.groundRayNode = self.playerNode.attachNewNode(groundColl)
        #self.groundRayNode.show()

        base.cTrav.addCollider(self.groundRayNode, self.groundHandler)

        collSphereNode = CollisionNode('playerCollSphere')
        collSphere = CollisionSphere(0, 0, 3, 4)
        collSphereNode.addSolid(collSphere)

        collSphereNode.setIntoCollideMask(BitMask32.bit(2))
        collSphereNode.setFromCollideMask(BitMask32.bit(2))
        
        sphereNode = self.playerNode.attachNewNode(collSphereNode)
        #sphereNode.show()

        base.cTrav.addCollider(sphereNode, self.collPusher)
        self.collPusher.addCollider(sphereNode, self.playerNode)

    def initSelector(self):
        self.selector = Actor('models/selector.egg')
        self.selector.setCollideMask(BitMask32.allOff())

        self.selectorAnimName = self.selector.getAnimNames()


    def addSelectorToEnemy(self, enemyTarget):
        if enemyTarget is not None:
            self.selector.reparentTo(enemyTarget.enemyNode)
            self.selector.loop(self.selectorAnimName[0], fromFrame=0, toFrame=12)

    def removeSelectorFromEnemy(self):
        if self.selector is not None:
            self.selector.stop()
            self.selector.detachNode()

    def setPlayerDestination(self, position):
        if self.getIsDead():
            return
        #print('setPlayerPosition: ' + str(position))
        self.destination = position
        pitchRoll = self.playerNode.getP(), self.playerNode.getR()

        self.playerNode.lookAt(self.destination)

        self.playerNode.setHpr(self.playerNode.getH(), *pitchRoll)

        self.velocity = self.destination - self.playerNode.getPos()

        self.velocity.normalize()
        self.velocity *= self.movementSpeed

        if self.state != 'Run':
            self.request('Run')

    def attackEnemy(self, enemy):
        if self.getIsDead():
            if self.state != 'Death':
                self.request('Death')
            return

        if self.getCurrentTarget() != enemy:
            return

        playerPos = self.playerNode.getPos()
        enemyPos = enemy.enemyNode.getPos()

        if self.getIsDead():
            print('player is already dead')
            self.request('Death')

        elif enemy.getIsDead():
            #print('enemy is already dead')
            self.request('Idle')
            enemy = None

        elif not utils.getIsInRange(playerPos, enemyPos, self.combatRange):
            print('Enemy fled away from combat range')
            #if self.state == 'Combat':
            #    self.request('Idle')

        else:
            print('Attack enemy!')
            # Make the player look at the enemy
            pitchRoll = (self.playerNode.getP(), self.playerNode.getR())
            self.playerNode.lookAt(enemy.enemyNode)
            self.playerNode.setHpr(self.playerNode.getH(), *pitchRoll)

            if self.state != 'Combat':
                self.request('Combat')

            self.playerModel.play('attack', fromFrame=0, toFrame=12)

            if enemy.getArmorClass() <= self.getAttackBonus():
                dmg = self.getDamageBonus()
                print('Player hit the enemy for: ' + str(dmg) + ' damage')
                # We hit the enemy
                taskMgr.doMethodLater(0.5, enemy.receiveDamage, 'receiveDamageTask', extraArgs=[dmg])


    def checkGroundCollisions(self):
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
                self.playerNode.setZ(newZ)

    def updatePlayerPosition(self, deltaTime):
        #print('updatePlayerPosition')
        newX = self.playerNode.getX() + self.velocity.getX() * deltaTime
        newY = self.playerNode.getY() + self.velocity.getY() * deltaTime
        newZ = self.playerNode.getZ()

        self.playerNode.setFluidPos(newX, newY, newZ)

        self.velocity = self.destination - self.playerNode.getPos()
        if self.velocity.lengthSquared() < 5:
            self.velocity = Vec3.zero()
            #print('destination reached')
            if self.state == 'Run':
                self.request('Idle')
        else:
            self.velocity.normalize()
            self.velocity *= self.movementSpeed

    def updatePlayerTarget(self):
        enemy = self.getCurrentTarget()

        if enemy is not None and enemy.getIsDead():
            self.setCurrentTarget(None)
            if self.state != 'Run':
                self.request('Idle')

    def playerUpdate(self, task):
        if self.getIsDead():
            if self.state != 'Death':
                self.request('Death')
            return task.cont

        # Don't run if we're taking too long
        deltaTime = task.time - task.last
        task.last = task.time

        if deltaTime > .2: 
            return task.cont

        self.updatePlayerPosition(deltaTime)
        self.checkGroundCollisions()
        self.updatePlayerTarget()

        base.camera.setPos(self.playerNode.getX(),
                       self.playerNode.getY() + self._cameraYModifier,
                       self.playerNode.getZ() + self._cameraZModifier)

        return task.cont


    def getEXPToNextLevel(self):
        return self._prevEXP + (self.level * 1000)

    def receiveEXP(self, value):
        self.experience += value
        if self.experience >= self.getEXPToNextLevel():
            self.increaseLevel()

    def getEXPToNextLevelInPercentage(self):
        return ((float(self.experience) - self._prevEXP) / (self.level * 1000.0) * 100.0)

    def setCurrentTarget(self, enemyTarget):
        #print('setCurrentTarget: ' + str(enemyTarget))
        self._currentTarget = enemyTarget

        if enemyTarget is not None:
            if not enemyTarget.getIsDead():
                self.addSelectorToEnemy(enemyTarget)

    def getCurrentTarget(self):
        return self._currentTarget

    def respawn(self, task):
        # Move player back to start pos
        self.destination = self.startPos
        self.playerNode.setPos(self.startPos)

        # Heal the player again
        self.fullHeal()

        # Make sure that isDead variable is set to false
        self.setIsNotDead()

        # Reset state back to idle
        self.request('Idle')

        return task.done

        
    def playIdleAnimation(self, task):
        if self.state == 'Idle':
            self.playerModel.loop('idle', fromFrame=0, toFrame=50)

        return task.done

    def enterRun(self):
        self.playerModel.loop('run', fromFrame=0, toFrame=12)

    def exitRun(self):
        pass

    def enterCombat(self):
        # Attacks are handled by attackEnemy
        self.destination = self.playerNode.getPos()

    def exitCombat(self):
        self.playerModel.stop()

    def enterIdle(self):
        self.playerModel.stop()
        self.playerModel.play('stop')

        taskMgr.doMethodLater(3, self.playIdleAnimation, 'idleAnimationTask')

    def exitIdle(self):
        self.playerModel.stop()

    def enterDeath(self):
        self.playerModel.play('death')

        taskMgr.doMethodLater(3, self.respawn, 'respawnTask')

    def exitDeath(self):
        self.playerModel.stop()



