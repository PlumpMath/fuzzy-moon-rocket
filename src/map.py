from panda3d.core import *
#from direct.actor.Actor import Actor

from collections import namedtuple

import utils
import enemy

Area = namedtuple('Area', ['modelName', 'enemies'] )

farmArea = Area(modelName='area_1', enemies={enemy.koboldMinion:1})
cornFieldArea = Area(modelName='area_2', enemies={enemy.koboldMinion:3})

class Map:

    maxSpawnPointsPerArea = 20

    def __init__(self, main):
        print("Map class instantiated")
        self._mainRef = main
        self._enemyListRef = main.enemyList
        self._stateHandlerRef = main.stateHandler

        self.mapNode = main.mainNode.attachNewNode('mapNode')

        # Initialze sun
        self.initSun(main.mainNode)

        self.loadArea(farmArea)

    def startArea(self):
        self.areaNode.reparentTo(self._mainRef.mainNode)

        # Initialize the task to handle enemy spawns
        self.enemySpawnTask = taskMgr.doMethodLater(1.5, self.enemySpawnUpdater, 'enemySpawnTask')

        # Change state to play
        if self._stateHandlerRef.state != self._stateHandlerRef.PLAY:
            self._stateHandlerRef.request(self._stateHandlerRef.PLAY)

        # Exit area task
        self.exitAreaTask = taskMgr.doMethodLater(1.5, self.exitArea, 'exitAreaTask')

    def loadArea(self, area):
        print('loadArea: ', area.modelName)
        # Save area attributes
        self._areaRef = area

        # Initialize player reference
        self._playerRef = None

        # Setup environment (plane)
        self.areaNode = NodePath(area.modelName+'Node')

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

        # Locate exit station within areaModel
        self.exitStation = self.areaModel.find('**/exitStation')

        # Make collision object collidable
        self.exitStation.find('**/ground').setCollideMask(BitMask32.bit(1))

        # Locate and save enemy spawn points 
        self.spawnPointsDict = {}
        i = 1
        spawnPoint = self.areaModel.find('**/enemySpawnPoint'+str(i))
        while spawnPoint.getErrorType() == 0: # While Spawn Point is found OK
            #print('located spawn point: ', spawnPoint)
            self.spawnPointsDict[spawnPoint] = 1 # Activate spawn point

            i += 1
            spawnPoint = self.areaModel.find('**/enemySpawnPoint'+str(i))

            # Implement failsafe in case of errors to avoid infinite loop
            if i >= self.maxSpawnPointsPerArea:
                break

        # Initialize walls
        self.initWalls(self.areaNode)

    def enemySpawnUpdater(self, task):
        if self._playerRef is None:
             # Load player reference
            self._playerRef = self._mainRef.player

        spawnRadius = 75

        playerPos = self._playerRef.playerNode.getPos()

        for spawnPoint, active in self.spawnPointsDict.iteritems():
            if active == 1:
                spawnPos = spawnPoint.getPos()
                if utils.getIsInRange(playerPos, spawnPos, spawnRadius):
                    self.spawnPointsDict[spawnPoint] = 0

                    self.spawnEnemies(spawnPos)


        # Call again after initial delay to reduce overhead
        return task.again

    def spawnEnemies(self, spawnPos):
        for enemyType, enemyAmount in self._areaRef.enemies.iteritems():
            for i in range(enemyAmount):
                newEnemy = enemy.Enemy(self._mainRef, enemyType)
                randomPos = spawnPos.getX() + (utils.getD10()-5), spawnPos.getY() + (utils.getD10()-5)
                newEnemy.moveEnemy(*randomPos)

    def exitArea(self, task):
        if self._playerRef is not None:
            exitRadius = 15

            playerPos = self._playerRef.playerNode.getPos()

            if utils.getIsInRange(playerPos, self.exitPos, exitRadius):
                print('At exit!')
                #self.exitStation.play(self.exitStationAnimation, fromFrame=0, toFrame=12)

                taskMgr.doMethodLater(2, self.unloadArea, 'unloadAreaTask')
                return task.done

        return task.again

    def unloadArea(self, task):
        print('unloadArea')

        # Loop through all enemies and clean them up by killing them
        for enemy in self._enemyListRef:
            enemy.suicide()

        # Empty dict of enemy spawn points
        self.spawnPointsDict.clear()

        # Remove area model
        self.areaModel.remove()

        # Remove walls model
        self.walls.remove()

        # Remove spawn task
        self.enemySpawnTask.remove()
        self.exitAreaTask.remove()

        # Remove nodes
        self.areaNode.removeNode()

        taskMgr.doMethodLater(0.1, self.loadNextArea, 'loadNextAreaTask')

        return task.done

    def loadNextArea(self, task):
        self.loadArea(cornFieldArea)
        taskMgr.doMethodLater(0.5, self.startArea, 'startAreaTask', extraArgs=[])

        return task.done

    def initWalls(self, areaNode):
        self.walls = loader.loadModel('models/walls.egg')
        self.walls.reparentTo(areaNode)

        # Set walls Z-position
        self.walls.setZ(-2)

        # Visual geometry should be non-collidable
        self.walls.setCollideMask(BitMask32.allOff())

        # Find collision geometry and make it collidable with pushers
        collisionWalls = self.walls.find('**/colliders')
        collisionWalls.setCollideMask(BitMask32.bit(2))

    def initSun(self, areaNode):
        # Setup directional light
        sun = DirectionalLight('sun')
        sun.setColor(VBase4(1, 0.75, 0.5, 1))

        self.sunNode = areaNode.attachNewNode(sun)
        self.sunNode.setP(-150)

        areaNode.setLight(self.sunNode)