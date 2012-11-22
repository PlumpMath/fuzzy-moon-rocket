from panda3d.core import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.filter.CommonFilters import CommonFilters

from collections import namedtuple

import utils
import enemy

Area = namedtuple('Area', ['modelName', 'enemies'] )

farmArea = Area(modelName='area_1', enemies={enemy.koboldMinion:1})

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

        self.initFilters()

        self.loadArea(farmArea)

#===============================================================================
#========================== AREA LOADING AND UNLOADING =========================

    def loadNextArea(self):
        self.loadArea(cornFieldArea)
        taskMgr.doMethodLater(0.5, self.startArea, 'startAreaTask', extraArgs=[])

    def startArea(self):
        if self._playerRef is None:
             # Load player reference
            self._playerRef = self._mainRef.player

        # Reparent areaNode to mainNode
        self.areaNode.reparentTo(self._mainRef.mainNode)

        # Initialize the task to handle enemy spawns
        self.enemySpawnTask = taskMgr.doMethodLater(1.5, self.enemySpawnActivator, 'enemySpawnActivatorTask')

        # Update sun position
        self.sunNode.setPos(self.startPos.getX(), self.startPos.getY(), self.startPos.getZ() + 10)

        # Change state to play
        if self._stateHandlerRef.state != self._stateHandlerRef.PLAY:
            self._stateHandlerRef.request(self._stateHandlerRef.PLAY)

        # Initialize the player position
        self._playerRef.initStartPosition(self.startPos, self.exitPos)

    def loadArea(self, area):
        print('loadArea: ', area.modelName)
        # Save area attributes
        self._areaRef = area

        # Initialize player reference
        self._playerRef = None

        # Setup environment (plane)
        self.areaNode = NodePath(area.modelName+'Node')

        self.areaModel = loader.loadModel('models/'+area.modelName)
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
        #self.exitStation = self.areaModel.find('**/exitStation')
        self.exitStation = loader.loadModel('models/exitStation')
        self.exitStation.setCollideMask(BitMask32.allOff())
        self.exitStation.reparentTo(self.areaNode)

        if area.modelName == 'area_1':
            self.exitStation.setH(-90)
        elif area.modelName == 'area_2':
            self.exitStation.setH(90)

        self.exitStation.setPos(self.exitPos)

        # Make collision object collidable
        self.exitStation.find('**/ground*').setCollideMask(BitMask32.bit(1))

        # Locate and save enemy spawn points
        self.spawnPointsDict = {}
        i = 1
        spawnPoint = self.areaModel.find('**/spawnPoint'+str(i))
        while spawnPoint.getErrorType() == 0: # While Spawn Point is found OK
            #print('located spawn point: ', spawnPoint)
            self.spawnPointsDict[spawnPoint] = 1 # Activate spawn point

            i += 1
            spawnPoint = self.areaModel.find('**/spawnPoint'+str(i))

            # Implement failsafe in case of errors to avoid infinite loop
            if i >= self.maxSpawnPointsPerArea:
                break

        # Initialize inverted sphere
        self.invertedSphere = self.areaNode.attachNewNode(CollisionNode('worldSphere'))
        self.invertedSphere.node().addSolid(CollisionInvSphere(0.0, 0.0, 1.0, 13)) # Adjust when new areas come

        self.invertedSphere.node().setFromCollideMask(BitMask32.allOff())
        self.invertedSphere.node().setIntoCollideMask(BitMask32.bit(2))

        #self.invertedSphere.show()


        # Initialize walls
        #self.initWalls(self.areaNode)

        # Initialize Exit gate
        #taskMgr.doMethodLater(0.25, self.initExitGate, 'initExitGateTask', extraArgs=[])

        # Initialize enemies
        taskMgr.doMethodLater(0.5, self.initEnemies, 'initEnemiesTask', extraArgs=[])

    def unloadArea(self):
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
        #self.enemySpawnTask.remove()
        #self.exitAreaTask.remove()
        taskMgr.remove(self.enemySpawnTask)

        # Remove nodes
        self.invertedSphere.removeNode()
        self.highlightTextNode.removeNode()
        self.walls.removeNode()
        self.exitStation.removeNode()
        self.areaNode.removeNode()

#=============================================================
#========== ENEMY SPAWNING ===================================
    def initEnemies(self):
        for spawnPoint, active in self.spawnPointsDict.iteritems():
            if active == 1:
                spawnPos = spawnPoint.getPos()

                self.spawnPointsDict[spawnPoint] = 0
                self.spawnEnemies(spawnPos)

    def spawnEnemies(self, spawnPos):
        for enemyType, enemyAmount in self._areaRef.enemies.iteritems():
            for i in range(enemyAmount):
                newEnemy = enemy.Enemy(self._mainRef, enemyType)
                randomPos = spawnPos.getX() + (utils.getD10()-5)*.1, spawnPos.getY() + (utils.getD10()-5)*.1
                newEnemy.moveEnemy(*randomPos)

                newEnemy.enemyNode.hide()

    def enemySpawnActivator(self, task):
        if self._playerRef is None:
             # Load player reference
            self._playerRef = self._mainRef.player

        #spawnRadius = 15

        playerPos = self._playerRef.playerNode.getPos()

        for enemy in self._enemyListRef:
            if not enemy._enemyActive:
                node = enemy.enemyNode
                if utils.getIsInRange(playerPos, node.getPos(), enemy.perceptionRange * 2):
                    node.show()
                    enemy._enemyActive = True
                    #print('activate enemy')

        # Call again after initial delay to reduce overhead
        return task.again

#=============================================================
#======== EXIT GATE ==========================================
    def initExitGate(self):
        self.exitGate = self.exitStation.find('**/exitGate')
        self.animatedExitGate = Actor('models/exitGate')
        self.gateAnimation = self.animatedExitGate.getAnimNames()
        self.animatedExitGate.reparentTo(self.areaNode)

        if self._areaRef.modelName == 'area_1':
            self.animatedExitGate.setH(-90)
        elif self._areaRef.modelName == 'area_2':
            self.animatedExitGate.setH(90)

        self.animatedExitGate.setZ(-0.5)

        self.animatedExitGate.setPos(self.exitPos)

        self.animatedExitGate.hide()
        self.exitGateIsHidden = True

        pickerTube = self.exitStation.find('**/collider')
        pickerTube.setCollideMask(BitMask32.bit(1) | BitMask32.bit(2))
        pickerTube.setName('exitGate')
        pickerTube.setZ(pickerTube.getZ()+1)

        highlightText = TextNode('exitGateHighlightText')
        highlightText.setText('Click to exit area')
        highlightText.setAlign(TextNode.ACenter)
        #self.highlightTextNode = self.exitGate.attachNewNode(highlightText)
        self.highlightTextNode = aspect2d.attachNewNode(highlightText)
        self.highlightTextNode.setScale(0.1)
        #self.highlightTextNode.setZ(self.exitGate.getZ() + 1)
        self.highlightTextNode.setPos(0, 0, 0.5)

        self.highlightTextNode.hide()

    def setGateIsNotHidden(self):
        self.exitGateIsHidden = True

    def playExitGateCloseAnimation(self):
        self.animatedExitGate.play(self.gateAnimation, fromFrame=13, toFrame=25)

    def showExitGate(self):
        self.exitGate.show()

    def hideAnimatedExitGate(self):
        self.animatedExitGate.hide()

    def hideHighlightTextNode(self):
        self.highlightTextNode.hide()

    def highlightExitGate(self, highlightExitGate):
        if not self.areaNode.isEmpty():
            if highlightExitGate and self.exitGateIsHidden:
                self.exitGateIsHidden = False

                self.animatedExitGate.show()
                self.exitGate.hide()
                self.highlightTextNode.show()

                self.animatedExitGate.play(self.gateAnimation, fromFrame=0, toFrame=12)
                print('highlight gate')
            elif not highlightExitGate and not self.exitGateIsHidden:
                Sequence(
                    Func(self.playExitGateCloseAnimation),
                    Wait(0.5),
                    Func(self.hideHighlightTextNode),
                    Parallel(Func(self.setGateIsNotHidden), Func(self.showExitGate), Func(self.hideAnimatedExitGate))
                ).start()

                print('hide gate')

    def clickExitGate(self):
        print('gate clicked')
        self.unloadArea()
        taskMgr.doMethodLater(0.5, self.loadNextArea, 'loadNextAreaTask', extraArgs=[])

#==================================================================================
#================= Misc. Initialization ===========================================
    def initWalls(self, areaNode):
        self.walls = loader.loadModel('models/walls')
        self.walls.reparentTo(areaNode)

        # Fix self-shadowing for thin objects
        self.walls.setDepthOffset(1)

        # Set walls Z-position
        self.walls.setZ(-2)

        # Visual geometry should be non-collidable
        self.walls.setCollideMask(BitMask32.allOff())

        # Find collision geometry and make it collidable with pushers
        collisionWalls = self.walls.find('**/colliders')
        collisionWalls.setCollideMask(BitMask32.bit(2))

    def initSun(self, parentNode):
        # Setup directional light (a yellowish sun)
        sun = DirectionalLight('sun')
        sun.setColor(VBase4(0.75, 0.75, 0.25, 1))
        sun.getLens().setNearFar(5, 1000)
        sun.getLens().setFilmSize(24, 36)
        #sun.showFrustum()
        sun.setShadowCaster(True, 4096, 4096) # Enable these shadows when the scene is scaled down (if)

        self.sunNode = parentNode.attachNewNode(sun)
        self.sunNode.setP(-130)
        #self.sunNode.setPos(self.startPos.getX(), self.startPos.getY(), 10)
        #self.sunNode.lookAt(0, 0, 0)

        parentNode.setLight(self.sunNode)

        # Setup ambient light (a grey/blueish secondary sun color)
        ambientLight = AmbientLight('alight')
        ambientLight.setColor(VBase4(0.1, 0.1, 0.2, 1))

        ambientLightNode = parentNode.attachNewNode(ambientLight)

        parentNode.setLight(ambientLightNode)

    def initFilters(self):
        pass
        # Initialize filters
        self.filters = CommonFilters(base.win, base.cam)

        # Cannot get the bloom filter to work
        #self.filters.setBloom(mintrigger=0.5, intensity=100.0, size='large')

        # Cartoon ink could maybe be nice, with a thin line?
        #self.filters.setCartoonInk(separation=0.5)

        # Nice sun ray effect, although it sets a special mood
        #self.filters.setVolumetricLighting(caster=self.sunNode, numsamples=100, density=1.0, decay=0.98, exposure=0.05)

        # Maybe use a little blur, might be nice? (can also sharpen with values over 1, i.e. blur: 0-1, sharpen:1-2)
        #self.filters.setBlurSharpen(amount=0.8)

        # Could not see an effect
        #self.filters.setAmbientOcclusion()
