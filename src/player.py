from panda3d.core import *
from direct.actor.Actor import Actor
from panda3d.ai import *

from utils import MouseHandler
from unit import Unit

class Player(Unit):

    playerStartPos = (0, 0, 1)

    def __init__(self, parentNode, AIworldRef):
        print("Player class instantiated")
        super(Player, self).__init__()

        self._AIworldRef = AIworldRef
        
        self.playerNode = parentNode.attachNewNode('playerNode')
        self.playerNode.setTag('player', '1')
        self.playerNode.setName('player')

        self.initPlayerAttributes()
        self.initPlayerModel(self.playerNode)
        self.initPlayerCamera(self.playerNode)

        self._mouseHandler = MouseHandler(self)

        # Start updating the camera depending on player position after 1 second
        taskMgr.doMethodLater(1, 
                            self.updateCameraPosition, 
                            'updateCameraPositionTask', 
                            extraArgs=[self.playerNode], 
                            appendTask=True)

    def initPlayerAttributes(self):
        # Initialize player attributes
        self.strength = 16
        self.constitution = 14
        self.dexterity = 10

    def initPlayerCamera(self, playerNode): 
        # Initialize the camera
        self._cameraYModifier = -100
        self._cameraZModifier = 5

        base.disableMouse()
        base.camera.setPos(playerNode.getX(),
                           playerNode.getY() + self._cameraYModifier, 
                           playerNode.getZ() + self._cameraZModifier)
        base.camera.lookAt(playerNode)

    def initPlayerModel(self, playerNode):
        print('initPlayerModel')
        # Initialize the player model (Actor)
        self._playerModel = Actor("models/BendingCan.egg")
        self._playerModel.reparentTo(playerNode)

        playerNode.setScale(0.1)
        #playerNode.setPos(0, 0, 1) # Initialize player position

        self.playerAI = AICharacter('player', # model name
                                    self.playerNode, # model node
                                    100,  # Mass
                                    0.05, # movt_force
                                    4) # max_force
        self._AIworldRef.addAiChar(self.playerAI)
        self.playerAIBehaviors = self.playerAI.getAiBehaviors()

        #self.playerAIBehaviors.obstacleAvoidance(1.0)

        #self._playerModel.setFromCollideMask(BitMask32.bit(0))
        #self._playerModel.setIntoCollideMask(BitMask32.allOff())


        self.initPlayerFloorCollider(playerNode)

    def initPlayerFloorCollider(self, playerNode):
        print('initPlayerFloorCollider')
        self.playerGroundRay = CollisionRay()
        self.playerGroundRay.setOrigin(0, 0, 10)
        self.playerGroundRay.setDirection(0, 0, -1)

        self.playerGroundColl = CollisionNode('groundRay')
        self.playerGroundColl.addSolid(self.playerGroundRay)
        self.playerGroundColl.setFromCollideMask(BitMask32.bit(1))
        self.playerGroundColl.setIntoCollideMask(BitMask32.allOff())

        self.playerGroundCollNode = self.playerNode.attachNewNode(self.playerGroundColl)
        self.playerGroundCollNode.show()

        self.collTraverser = CollisionTraverser()
        self.collHandler = CollisionHandlerQueue()

        self.collTraverser.addCollider(self.playerGroundCollNode, self.collHandler)

        self.collTraverser.showCollisions(base.render) # Remove to hide collisions

        base.collTraverser = self.collTraverser

        self.playerNode.setPos(self.playerStartPos)
        self.playerVelocity = Vec3(0, 0, 0)
        self.playerAcceleration = Vec3(0, 0, 0)

        taskMgr.remove('GroundCollisionTask')
        self.groundCollTask = taskMgr.add(self.groundCollisionTask, 'GroundCollisionTask')
        self.groundCollTask.last = 0

    def groundCollisionTask(self, task):
        # Standard technique for finding the amount of time since the last frame
        self.deltaTime = task.time - task.last
        task.last = task.time

        if self.deltaTime > .2: 
            return task.cont

        print('numEntries:' + str(self.collHandler.getNumEntries()))
        for i in range(self.collHandler.getNumEntries()):
            self.entry = self.collHandler.getEntry(i)
            self.entryName = self.entry.getIntoNode().getName()
            self.entryTag = self.entry.getIntoNode().findNetTag()
            print('Name: ', self.entryName)
            #if 'ground' == (self.entryName, self.entryTag):
            if self.entryName == 'ground' or self.entryTag == 'ground':
                #print('Call groundCollisionHandler')
                self.groundCollisionHandler(self.entry)

        self.playerVelocity += self.playerAcceleration * self.deltaTime * 70
        #if self.


        return task.cont

    def groundCollisionHandler(self, colEntry):
        print('groundCollisionHandler')
        self.newZ = colEntry.getSurfacePoint(base.render).getZ()
        self.playerNode.setZ(self.newZ + 0.4)

        self.surfaceNormal = colEntry.getSurfaceNormal(base.render)
        self.accelSide = self.surfaceNormal.cross(UP)

        self.playerAcceleration = self.surfaceNormal.cross(self.accelSide)


    def updateCameraPosition(self, playerNode, task):
        base.camera.lookAt(playerNode)
        base.camera.setPos(playerNode.getX(), 
                           playerNode.getY() + self._cameraYModifier, 
                           playerNode.getZ() + self._cameraZModifier)

        return task.cont
        
    def getPos(self):
        return self.playerNode.getPos()

    def getEXPToNextLevel(self):
        return self._prevEXP + (self.level * 1000)

    def receiveEXP(self, value):
        print("Giving EXP :" + str(value))
        self.experience += value
        if self.experience >= self.getEXPToNextLevel():
            self.increaseLevel()

    def getEXPToNextLevelInPercentage(self):
        return ((float(self.experience) - self._prevEXP) / 
                    (self.level * 1000.0) * 100.0)

    def getPlayerNode(self):
        return self.playerNode

    def move(self, x, y, z):
        # Get mouse position
        self.playerAIBehaviors.pauseAi('seek')
        self.playerAIBehaviors.resumeAi('seek')
        self.playerAIBehaviors.seek(Vec3(x, y, self.playerNode.getZ()))

