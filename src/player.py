from panda3d.core import *
from direct.actor.Actor import Actor
from panda3d.ai import *

import utils
from unit import Unit

class Player(Unit):

    playerStartPos = (0, 0, 1)
    _cameraYModifier = -10
    _cameraZModifier = 10

    def __init__(self, parentNode, AIworldRef):
        print("Player class instantiated")
        super(Player, self).__init__()

        self._AIworldRef = AIworldRef
        
        self.playerNode = parentNode.attachNewNode('playerNode')
        self.playerNode.setName('player')

        self.initPlayerAttributes()
        self.initPlayerModel()
        self.initPlayerCamera()

        self._mouseHandler = utils.MouseHandler(self)

        # Start updating the camera depending on player position after 1 second
        taskMgr.add(self.updateCameraPosition, 
                    'updateCameraPositionTask', 
                    extraArgs=[self.playerNode], 
                    appendTask=True)

    def initPlayerAttributes(self):
        # Initialize player attributes
        self.strength = 16
        self.constitution = 14
        self.dexterity = 10

    def initPlayerCamera(self): 
        # Initialize the camera
        base.disableMouse()
        base.camera.setPos(self.playerNode.getX(),
                           self.playerNode.getY() + self._cameraYModifier, 
                           self.playerNode.getZ() + self._cameraZModifier)
        base.camera.lookAt(self.playerNode)

    def initPlayerModel(self):
        # Initialize the player model (Actor)
        _playerModel = Actor("models/BendingCan.egg")
        _playerModel.reparentTo(self.playerNode)

        self.playerNode.setScale(0.1)

        self.playerAI = AICharacter('player', # model name
                                    self.playerNode, # model node
                                    100,  # Mass
                                    0.05, # movt_force
                                    4) # max_force
        self._AIworldRef.addAiChar(self.playerAI)
        self.playerAIBehaviors = self.playerAI.getAiBehaviors()

        self.initPlayerFloorCollider()

    def initPlayerFloorCollider(self):
        print('initPlayerFloorCollider')
        base.cTrav = CollisionTraverser()
        self.collHandler = CollisionHandlerQueue()

        groundRay = CollisionRay(0, 0, 10,
                                       0, 0, -1)
        groundRayNode = utils.makeCollisionNodePath(self.playerNode, groundRay)

        base.cTrav.addCollider(groundRayNode, self.collHandler)
        base.cTrav.traverse(base.render)

        groundTask = taskMgr.add(self.groundCollisionTask, 'GroundCollTask')
        groundTask.last = 0

    def groundCollisionTask(self, task):
        # Standard technique for finding the amount of time since the last frame
        deltaTime = task.time - task.last
        task.last = task.time

        if deltaTime > .2: 
            return task.cont

        for i in range(self.collHandler.getNumEntries()):
            entry = self.collHandler.getEntry(i)
            entryName = entry.getIntoNode().getName()
            if entryName == 'ground':
                self.groundCollisionHandler(entry)

        return task.cont

    def groundCollisionHandler(self, colEntry):
        print('groundCollisionHandler')
        newZ = colEntry.getSurfacePoint(colEntry.getIntoNodePath()).getZ()
        self.playerNode.setZ(newZ + 0.5)

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

    def move(self, x, y):
        # Get mouse position
        self.playerAIBehaviors.pauseAi('seek')
        self.playerAIBehaviors.resumeAi('seek')
        self.playerAIBehaviors.seek(Vec3(x, y, self.playerNode.getZ()))

