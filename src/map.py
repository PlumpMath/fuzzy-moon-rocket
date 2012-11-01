from panda3d.core import *
import utils

from collections import namedtuple

Area = namedtuple('Area', ['modelName', 'numSpawns'] )

farmArea = Area(modelName='area_1', numSpawns=2)
cornFieldArea = Area(modelName='area_2', numSpawns=4)

class Map:
    def __init__(self, parentNode):
        print("Map class instantiated")
        self._mainRef = parentNode
        self.mapNode = parentNode.attachNewNode('mapNode')

        # Load first area
        self.loadArea(farmArea)

        # Initialze sun
        self.initSun(self._mainRef)

    def loadArea(self, area):
        # Setup environment (plane)
        self.areaNode = self.mapNode.attachNewNode(area.modelName+'Node')

        self.areaModel = loader.loadModel('models/'+area.modelName+'.egg')
        self.areaModel.reparentTo(self.areaNode)

        # Make sure area is centered in world
        self.areaNode.setPos(0, 0, 0)

        # Everything should at default be non-collidable
        self.areaModel.setCollideMask(BitMask32.allOff())

        # The ground is the walk plane, it collides with mouse ray and player- and enemies ground rays
        self.ground = self.areaModel.find('**/ground')
        self.ground.setCollideMask(BitMask32.bit(1))

        # Colliders are obstacles in areas, they collide with enemies and the player
        self.collidersGroup = self.areaModel.find('**/colliders')
        self.collidersGroup.setCollideMask(BitMask32.bit(2))

        # Locate starting and exiting positions
        self.startPos = self.areaModel.find('**/startPos').getPos()
        self.exitPos = self.areaModel.find('**/exitPos').getPos()

        # Locate and save enemy spawn points 
        self.enemySpawnPoints = []
        for i in range(area.numSpawns):
            self.enemySpawnPoints.append(self.areaModel.find('**/enemySpawnPoint'+str(i)))

        # Initialize walls
        self.initWalls(self.areaNode)

    def unloadArea(self):
        # Empty list of enemy spawn points
        enemySpawnPoints[:] = []

        # Cleanup and remove area model
        self.areaModel.cleanup()
        self.areaModel.delete()

        # Cleanup and remove walls model
        self.walls.cleanup()
        self.walls.delete()

        # Remove nodes
        self.areaNode.removeNode()

    def initWalls(self, areaNode):
        self.walls = loader.loadModel('models/walls.egg')
        self.walls.reparentTo(areaNode)

        # Visual geometry should be non-collidable
        self.walls.setCollideMask(BitMask32.allOff())

        # Find collision geometry and make it collidable with pushers
        collisionWalls = self.walls.find('**/collisionWalls')
        collisionWalls.setCollideMask(BitMask32.bit(2))

    def initSun(self, areaNode):
        # Setup directional light
        sun = DirectionalLight('sun')
        sun.setColor(VBase4(1, 1, 0.5, 1))

        self.sunNode = areaNode.attachNewNode(sun)
        self.sunNode.setP(-150)

        areaNode.setLight(self.sunNode)