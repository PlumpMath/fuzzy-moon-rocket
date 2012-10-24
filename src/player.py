from panda3d.core import *
from direct.actor.Actor import Actor

from utils import MouseHandler
from unit import Unit

class Player(Unit):

    def __init__(self, parentNode):
        print("Player class instantiated")
        super(Player, self).__init__()
        
        self.playerNode = parentNode.attachNewNode('playerNode')

        self.initPlayerAttributes()
        self.initPlayerModel(self.playerNode)
        self.initPlayerCamera(self.playerNode)

        self._mouseHandler = MouseHandler()

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
        self._cameraYModifier = -5
        self._cameraZModifier = 5

        base.disableMouse()
        base.camera.setPos(playerNode.getX(),
                           playerNode.getY() + self._cameraYModifier, 
                           playerNode.getZ() + self._cameraZModifier)
        base.camera.lookAt(playerNode)

    def initPlayerModel(self, playerNode):
        # Initialize the player model (Actor)
        self._playerModel = Actor("models/BendingCan.egg")
        self._playerModel.reparentTo(playerNode)

        playerNode.setScale(0.1)
        playerNode.setPos(2, 0, 1) # Initialize player position

    def updateCameraPosition(self, playerNode, task):
        base.camera.setPos(playerNode.getX(), 
                           playerNode.getY() + self._cameraYModifier, 
                           playerNode.getZ() + self._cameraZModifier)
        
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