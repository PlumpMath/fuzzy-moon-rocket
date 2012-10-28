from panda3d.core import *
from direct.actor.Actor import Actor
#from panda3d.ai import *

import utils
from unit import Unit

class Player(Unit):

    playerStartPos = (0, 0, 1)
    _cameraYModifier = -22 # Relative to player Y
    _cameraZPos = 20 # Absolute Z position

    def __init__(self, parentNode, AIworldRef):
        print("Player class instantiated")
        super(Player, self).__init__()

        self._AIworldRef = AIworldRef
        
        self.playerNode = parentNode.attachNewNode('playerNode')

        self.initPlayerAttributes()
        self.initPlayerModel()
        self.initPlayerCamera()

        self.initPlayerMovement()
        self.initPlayerCollisionHandlers()
        self.initPlayerCollisionSolids()

        self._mouseHandler = utils.MouseHandler(self)

        playerUpdateTask = taskMgr.add(self.playerUpdate, 'playerUpdateTask')
        playerUpdateTask.last = 0

    def initPlayerAttributes(self):
        # Initialize player attributes
        self.strength = 16
        self.constitution = 14
        self.dexterity = 10

        self.movementSpeed = 5

    def initPlayerModel(self):
        # Initialize the player model (Actor)
        self.playerModel = Actor("models/BendingCan.egg")
        self.playerModel.reparentTo(self.playerNode)
        self.playerModel.setName('playerModel')
        self.playerModel.setCollideMask(BitMask32.allOff())
        self.playerModel.setScale(0.2)

        self.playerNode.setPos(self.playerStartPos)
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
        print("Giving EXP :" + str(value))
        self.experience += value
        if self.experience >= self.getEXPToNextLevel():
            self.increaseLevel()

    def getEXPToNextLevelInPercentage(self):
        return ((float(self.experience) - self._prevEXP) / (self.level * 1000.0) * 100.0)

    def initPlayerMovement(self):
        self.destination = Point3.zero()
        self.velocity = Vec3.zero()

    def initPlayerCollisionHandlers(self):
        self.floorHandler = CollisionHandlerFloor()
        #self.pusherHandler = CollisionHandlerPusher()
        self.floorHandler.setMaxVelocity(14)
        self.floorHandler.setOffset(1)

        self.allMasks = BitMask32.bit(0)
        self.groundMask = BitMask32.bit(1)
        self.wallMask = BitMask32.bit(2)

    def initPlayerCollisionSolids(self):
        utils.fromCol(self.playerNode, self.floorHandler, CollisionRay(0, 0, -1, 0, 0, -1),  self.groundMask)

        #utils.fromCol(self.playerNode, self.pusherHandler, CollisionSphere(0, 0, 1, .5), self.wallMask, True)

    def setPlayerDestination(self, position):
        print('setPlayerPosition: ' + str(position))
        self.destination = position
        pitchRoll = self.playerNode.getP(), self.playerNode.getR()

        self.playerNode.lookAt(self.destination)

        self.playerNode.setHpr(self.playerNode.getH(), *pitchRoll)

        self.velocity = self.destination - self.playerNode.getPos()

        self.velocity.normalize()
        self.velocity *= self.movementSpeed

    def updatePlayerPosition(self, deltaTime):
        #print('updatePlayerPosition')
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
        # Don't run if we're taking too long
        deltaTime = task.time - task.last
        task.last = task.time

        if deltaTime > .2: 
            return task.cont

        self.updatePlayerPosition(deltaTime)

        base.camera.setPos(self.playerNode.getX(),
                           self.playerNode.getY() + self._cameraYModifier,
                           self.playerNode.getZ() + self._cameraZPos)

        return task.cont

