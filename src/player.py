from panda3d.core import *
from direct.actor.Actor import Actor
from direct.fsm.FSM import FSM
from panda3d.ai import *

import utils
from unit import Unit

class Player(FSM, Unit):

    # Declare private variables
    _playerStartPos = Point3(0, 0, 10)
    _cameraYModifier = -22 # Relative to player Y
    _cameraZPos = 20 # Absolute Z position

    _currentTarget = None

    def __init__(self, parentNode, AIworldRef):
        print("Player class instantiated")
        Unit.__init__(self)
        FSM.__init__(self, 'playerFSM')

        self._AIworldRef = AIworldRef
        
        self.playerNode = parentNode.attachNewNode('playerNode')

        self.initPlayerAttributes()
        self.initPlayerModel()
        self.initPlayerCamera()

        self.initPlayerAi()

        self.initPlayerMovement()
        self.initPlayerCollisionHandlers()
        self.initPlayerCollisionSolids()

        utils.MouseHandler(self)

        playerUpdateTask = taskMgr.add(self.playerUpdate, 'playerUpdateTask')
        playerUpdateTask.last = 0

    def initPlayerAttributes(self):
        # Initialize player attributes
        self.strength = 16
        self.constitution = 14
        self.dexterity = 10

        self.combatRange = 2
        self.movementSpeed = 5

        self.initHealth()

    def initPlayerModel(self):
        # Initialize the player model (Actor)
        self.playerModel = Actor("models/BendingCan.egg")
        self.playerModel.reparentTo(self.playerNode)
        self.playerModel.setName('playerModel')
        self.playerModel.setCollideMask(BitMask32.allOff())
        self.playerModel.setScale(0.2)

        self.playerNode.setPos(self._playerStartPos)
        self.playerNode.setName('playerNode')
        self.playerNode.setCollideMask(BitMask32.allOff())

    def initPlayerCamera(self): 
        # Initialize the camera
        base.disableMouse()
        base.camera.setPos(self.playerNode.getX(),
                           self.playerNode.getY() + self._cameraYModifier, 
                           self.playerNode.getZ() + self._cameraZPos)
        base.camera.lookAt(self.playerNode)

    def getEXPToNextLevel(self):
        return self._prevEXP + (self.level * 1000)

    def receiveEXP(self, value):
       #print("Giving EXP :" + str(value))
        self.experience += value
        if self.experience >= self.getEXPToNextLevel():
            self.increaseLevel()

    def getEXPToNextLevelInPercentage(self):
        return ((float(self.experience) - self._prevEXP) / (self.level * 1000.0) * 100.0)

    def setCurrentTarget(self, enemyTarget):
        #print('setCurrentTarget: ' + str(enemyTarget))
        self._currentTarget = enemyTarget

    def getCurrentTarget(self):
        return self._currentTarget

    def attackEnemy(self, enemy):
        if self.state == 'Death':
            return

        print('attack Enemy!')

        if self.getCurrentTarget() != enemy:
            return

        playerPos = self.playerNode.getPos()
        enemyPos = enemy.enemyNode.getPos()

        if self.getIsDead():
            print('player is already dead')
            self.request('Death')

        elif enemy.getIsDead():
            print('enemy is already dead')
            self.request('Idle')

        elif utils.getIsInRange(playerPos, enemyPos, self.combatRange) == False:
            print('enemy fled away from combat range')

        #elif utils.getIsInRange(playerPos, enemyPos, self.perceptionRange) == False:
        #    print('enemy fled away from perception range')
            #self.request('Idle')

        else:
            # Play attack animation
            if enemy.getArmorClass() <= self.getAttackBonus():
                dmg = self.getDamageBonus()
                print('Player hit the enemy for: ' + str(dmg) + ' damage')
                # We hit the enemy
                enemy.receiveDamage(dmg)

    def initPlayerAi(self):
        self.playerAi = AICharacter('player', self.playerNode, 100, 0.05, 5)
        self._AIworldRef.addAiChar(self.playerAi)
        self.playerAiBehaviors = self.playerAi.getAiBehaviors()
        #self.playerAiBehaviors.obstacleAvoidance(1.0)

    def initPlayerMovement(self):
        self.destination = Point3.zero()
        self.velocity = Vec3.zero()

    def initPlayerCollisionHandlers(self):
        self.groundHandler = CollisionHandlerQueue()

    def initPlayerCollisionSolids(self):
        groundRay = CollisionRay(0, 0, 10, 0, 0, -1)
        groundColl = CollisionNode('groundRay')
        groundColl.addSolid(groundRay)
        groundColl.setIntoCollideMask(BitMask32.allOff())
        groundColl.setFromCollideMask(BitMask32.bit(1))
        self.groundRayNode = self.playerNode.attachNewNode(groundColl)
        self.groundRayNode.show()

        base.cTrav.addCollider(self.groundRayNode, self.groundHandler)

    def checkGroundCollisions(self):
        if self.groundHandler.getNumEntries() > 0:
            self.groundHandler.sortEntries()
            entries = []
            for i in range(self.groundHandler.getNumEntries()):
                entry = self.groundHandler.getEntry(i)
                entries.append(entry)

            entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                        x.getSurfacePoint(render).getZ()))

            if (len(entries) > 0) and (entries[0].getIntoNode().getName() == 'groundcnode'):
                newZ = entries[0].getSurfacePoint(base.render).getZ()
                self.playerNode.setZ(newZ)

    def setPlayerDestination(self, position):
        if self.state == 'Death':
            return
        #print('setPlayerPosition: ' + str(position))
        self.destination = position
        pitchRoll = self.playerNode.getP(), self.playerNode.getR()

        self.playerNode.lookAt(self.destination)

        self.playerNode.setHpr(self.playerNode.getH(), *pitchRoll)

        self.velocity = self.destination - self.playerNode.getPos()

        self.velocity.normalize()
        self.velocity *= self.movementSpeed

    def updatePlayerPosition(self, deltaTime):
        #print('updatePlayerPosition')
        if self.state == 'Death':
            return

        newX = self.playerNode.getX() + self.velocity.getX() * deltaTime
        newY = self.playerNode.getY() + self.velocity.getY() * deltaTime
        newZ = self.playerNode.getZ()

        self.playerNode.setFluidPos(newX, newY, newZ)

        self.velocity = self.destination - self.playerNode.getPos()
        if self.velocity.lengthSquared() < 0.1:
            self.velocity = Vec3.zero()
            #print('destination reached')
        else:
            self.velocity.normalize()
            self.velocity *= self.movementSpeed

    def playerUpdate(self, task):
        if self.state == 'Death':
            return

        # Don't run if we're taking too long
        deltaTime = task.time - task.last
        task.last = task.time

        if deltaTime > .2: 
            return task.cont

        self.updatePlayerPosition(deltaTime)
        self.checkGroundCollisions()

        base.camera.setPos(self.playerNode.getX(),
                           self.playerNode.getY() + self._cameraYModifier,
                           self.playerNode.getZ() + self._cameraZPos)

        return task.cont

    def enterCombat(self):
        print('player enter combat')

    def exitCombat(self):
        print('player exit combat')

    def enterIdle(self):
        print('player enter idle')

    def exitIdle(self):
        print('player exit idle')

    def enterDeath(self):
        print('player dead')

