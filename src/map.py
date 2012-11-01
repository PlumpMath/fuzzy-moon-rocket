from panda3d.core import *

from collections import namedtuple

import utils

import enemy

Area = namedtuple('Area', ['modelName', 'numSpawns', 'numEnemiesPerSpawn'] )

farmArea = Area(modelName='area_1', numSpawns=2, numEnemiesPerSpawn=1)
cornFieldArea = Area(modelName='area_2', numSpawns=4, numEnemiesPerSpawn=2)

class Map:
    def __init__(self, main):
        print("Map class instantiated")
        self._mainRef = main

        self.mapNode = main.mainNode.attachNewNode('mapNode')

        # Initialze sun
        self.initSun(main.mainNode)

        self.loadArea(farmArea)

    def loadArea(self, area):
        # Initialize player reference
        self._playerRef = None

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
        self.spawnPointsDict = {}
        self.spawnPointsList = []
        for i  in range(1, area.numSpawns):
            spawnPoint = self.areaModel.find('**/enemySpawnPoint'+str(i))
            print('located spawn point: ' + str(spawnPoint))
            self.spawnPointsList.append(spawnPoint)
            self.spawnPointsDict[spawnPoint] = 1 # Active

        # Initialize walls
        self.initWalls(self.areaNode)

        enemeySpawnTask = taskMgr.doMethodLater(1.5, self.enemySpawnUpdater, 'enemySpawnTask', extraArgs=[area], appendTask=True)

    def enemySpawnUpdater(self, area, task):
        if self._playerRef is None:
             # Load player reference
            self._playerRef = self._mainRef.player

        spawnRadius = 50

        playerPos = self._playerRef.playerNode.getPos()

        for spawnPoint in self.spawnPointsList:
            spawnPos = spawnPoint.getPos()
            if utils.getIsInRange(playerPos, spawnPos, spawnRadius):
                if self.spawnPointsDict[spawnPoint] == 1:
                    self.spawnPointsDict[spawnPoint] = 0
                    self.spawnEnemies(area.numEnemiesPerSpawn, spawnPos)

        # Call again after initial delay to reduce overhead
        return task.again

    def spawnEnemies(self, amount, spawnPosition):
        for i in range(amount):
            newEnemy = enemy.Enemy(self._mainRef, 'probe', enemy.koboldMinion)
            newEnemy.moveEnemy(spawnPosition.getX(), spawnPosition.getY())


    def unloadArea(self):
        # Empty list of enemy spawn points
        self.spawnPointsList[:] = []
        # Empty dict of enemy spawn point status
        self.spawnPointsDict.clear()

        # Cleanup and remove area model
        self.areaModel.cleanup()
        self.areaModel.delete()

        # Cleanup and remove walls model
        self.walls.cleanup()
        self.walls.delete()

        # Remove spawn task
        enemeySpawnTask.remove()

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