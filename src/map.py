from panda3d.core import *
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.filter.CommonFilters import CommonFilters

from collections import namedtuple

import utils
import enemy

Area = namedtuple('Area', ['modelName', 'enemies'] )

farmArea = Area(modelName='area_1', enemies={enemy.koboldMinion:2})
secondArea = Area(modelName='area_2', enemies={enemy.koboldSkirmisher:2, enemy.koboldMinion:1})

class Map:

    def __init__(self, main):
        print("Map class instantiated")
        self._mainRef = main
        self._enemyListRef = main.enemyList
        self._stateHandlerRef = main.stateHandler

        self.mapNode = main.mainNode.attachNewNode('mapNode')

        # Initialize area list and current area variable
        self.areaList = [farmArea, secondArea]
        self.currentArea = 0

        # Initialze sun
        self.initSun(main.mainNode)

        # Initialize image processing filters
        self.initFilters()

        # Load the first area
        self.loadNextArea()

        self.playerPlaced = False

#===============================================================================
#========================== AREA LOADING AND UNLOADING =========================

    def loadNextArea(self):
        self.currentArea += 1
        if self.currentArea > len(self.areaList):
            print 'No next area to load, loading previous instead'
            self.loadPreviousArea()
        else:
            if self.currentArea > 1:
                self.unloadArea()

            taskMgr.doMethodLater(0.5, self.loadArea, 'loadAreaTask', extraArgs=[self.areaList[self.currentArea-1]])
            taskMgr.doMethodLater(1.0, self.startArea, 'startAreaTask', extraArgs=[])

    def loadPreviousArea(self):
        self.currentArea -= 2
        if self.currentArea < 0:
            print 'No previous area to load, loading next instead'
            self.loadNextArea()
        else:
            self.unloadArea()
            taskMgr.doMethodLater(0.5, self.loadArea, 'loadAreaTask', extraArgs=[self.areaList[self.currentArea-1]])
            taskMgr.doMethodLater(1.0, self.startArea, 'startAreaTask', extraArgs=[])

    def startArea(self):
        print 'startArea'
        if self._playerRef is None:
             # Load player reference
            self._playerRef = self._mainRef.player

        # Reparent areaNode to mainNode
        self.areaNode.reparentTo(self._mainRef.mainNode)

        # Initialize the task to handle enemy spawns
        self.enemySpawnTask = taskMgr.doMethodLater(1.5, self.enemySpawnActivator, 'enemySpawnActivatorTask')

        # Update sun position - does not change the shadows
        self.sunNode.setPos(self.startPos.getX(), self.startPos.getY(), self.startPos.getZ() + 10)

        # Change state to play
        if self._stateHandlerRef.state != self._stateHandlerRef.PLAY:
            self._stateHandlerRef.request(self._stateHandlerRef.PLAY)

        if not self.playerPlaced:
            # Initialize the player position
            self._playerRef.initStartPosition(self.startPos, self.exitPos)
            self.playerPlaced = True
        else:
            self._playerRef.initStartPosition(self.arrivalPos, self.exitPos)

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

        # Make visual geometry collidable with certain objects (camera ray)
        self.areaModel.find('**/geometry').setCollideMask(BitMask32.bit(4))

        # The ground is the walk plane, it collides with mouse ray and player- and enemies ground rays
        for ground in self.areaModel.findAllMatches('**/ground*'):
            ground.setCollideMask(BitMask32.bit(1))

        # Colliders are obstacles in areas, they collide with enemies and the player
        self.collidersGroup = self.areaModel.find('**/colliders')
        self.collidersGroup.setCollideMask(BitMask32.bit(2))

        # Locate starting and exiting positions
        self.startPos = self.areaModel.find('**/startPos').getPos()
        self.exitPos = self.areaModel.find('**/exitPos').getPos()
        self.arrivalPos = self.areaModel.find('**/arrival').getPos()

        # Locate and save enemy spawn points
        self.spawnPointsDict = {}
        for spawnPoint in self.areaModel.findAllMatches('**/spawnPoint*'):
            self.spawnPointsDict[spawnPoint] = 1 # Activate spawn point

        # Initialize inverted sphere
        self.invertedSphere = self.areaNode.attachNewNode(CollisionNode('worldSphere'))
        self.invertedSphere.node().addSolid(CollisionInvSphere(0.0, 0.0, 1.0, 13)) 

        self.invertedSphere.node().setFromCollideMask(BitMask32.allOff())
        self.invertedSphere.node().setIntoCollideMask(BitMask32.bit(2))

        #self.invertedSphere.show()

        # Load in point lights
        taskMgr.doMethodLater(0.5, self.initLights, 'initLightsTask', extraArgs=[])

        # Initialize Exit gate
        taskMgr.doMethodLater(0.5, self.initExitGate, 'initExitGateTask', extraArgs=[])

        # Initialize enemies
        taskMgr.doMethodLater(0.5, self.initEnemies, 'initEnemiesTask', extraArgs=[])

    def unloadArea(self):
        print('unloadArea')

        # Loop through all enemies and clean them up by killing them
        for enemy in self._enemyListRef:
            enemy.suicide()

        # Clear all the point lights
        self.clearAllPointLights()

        # Empty dict of enemy spawn points
        self.spawnPointsDict.clear()

        # Remove area model
        self.areaModel.remove()

        # Remove spawn task
        taskMgr.remove(self.enemySpawnTask)
        taskMgr.remove('areaTransitionCheckerTask')
        taskMgr.remove('updatePlayerLightsTask')

        # Removed animated models
        self.oII.cleanup()
        self.oII.delete()

        # Remove nodes
        self.invertedSphere.removeNode()
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
        station = self.areaModel.find('**/station')
        exitGate = station.find('**/stationGate')
        ground = station.find('**/ground*')

        self.exitGate = Actor('models/exitGate') 
        self.exitGateAnim = self.exitGate.getAnimNames()
        
        self.exitGate.setHpr(render, station.getHpr(render))
        self.exitGate.setPos(render, station.getPos(render))

        self.exitGate.reparentTo(self.areaNode)

        self.oII = Actor('models/oii')
        oIIAnim = self.oII.getAnimNames() # No animation added yet
        # print 'oII anim:', oIIAnim
        self.oII.setPlayRate(0.5, oIIAnim)
        self.oII.loop(oIIAnim, fromFrame=0, toFrame=12)

        self.oII.setPos(ground.getPos(render))
        self.oII.setZ(self.oII, 0.15)

        self.oII.reparentTo(self.areaNode)

        taskMgr.doMethodLater(1, self.areaTransitionChecker, 'areaTransitionCheckerTask')

    def areaTransitionChecker(self, task):
        player = self._playerRef
        playerNode = player.playerNode

        if utils.getIsInRange(self.oII.getPos(render), playerNode.getPos(render), .5):
            if not player.areaTransitioning:
                #print 'fire up area transition dialog'
                player.areaTransitioning = True

                self.exitGate.play(self.exitGateAnim, fromFrame=0, toFrame=12)
        else:
            if player.areaTransitioning:
                #print 'close area transition dialog'
                player.areaTransitioning = False

                self.exitGate.play(self.exitGateAnim, fromFrame=13, toFrame=25)

        return task.again


#==================================================================================
#================= Point Lights ===========================================
    def initLights(self):
        self.pointLightList = []

        pointLightList = self.areaModel.findAllMatches('**/pLight*')
        if len(pointLightList) > 0:
            for i, plight in enumerate(pointLightList):
                plightPos = plight.getPos()

                newPLight = PointLight('plight' + str(i))
                newPLight.setColor(VBase4(0.5, 0.5, 0.1, 1))
                newPLightNode = self.areaNode.attachNewNode(newPLight)
                newPLightNode.setPos(plightPos)

                self.areaModel.find('**/ground').setLight(newPLightNode)

                self.pointLightList.append(newPLightNode)

                for obj in self.areaModel.find('**/geometry').getChildren():
                    self.applyPointLightToObj(newPLightNode, obj)

        taskMgr.doMethodLater(1, self.updatePlayerLights, 'updatePlayerLightsTask')

    def applyPointLightToObj(self, newPLightNode, obj):
        if len(obj.getChildren()) > 1:
            #print 'apply light to the children of:', obj
            for newObj in obj.getChildren():
                self.applyPointLightToObj(newPLightNode, newObj)
        else:
            if utils.getIsInRange(obj.getPos(render), newPLightNode.getPos(render), 2):
                #print 'apply light from ', newPLightNode, ' to ', obj
                obj.setLight(newPLightNode)

    def clearAllPointLights(self):
        for pLight in self.pointLightList:
            for obj in self.areaModel.find('**/geometry').getChildren():
                self.removePointLightFromObj(pLight, obj)

            pLight.removeNode()

    def removePointLightFromObj(self, pLightNode, obj):
        if len(obj.getChildren()) > 1:
            for exObj in obj.getChildren():
                self.removePointLightFromObj(pLightNode, exObj)
        else:
            if obj.hasLight(pLightNode):
                obj.clearLight(pLightNode)

    def updatePlayerLights(self, task):
        # If time between frames is way too much, stop the task here
        if globalClock.getDt() > .5:
            return task.again

        playerNode = self._playerRef.playerNode

        if len(self.pointLightList) > 0:
            # Make point lights light up player as well
            for plight in self.pointLightList:
                if utils.getIsInRange(plight.getPos(render), playerNode.getPos(render), 2):
                    playerNode.setLight(plight)
                else:
                    if playerNode.hasLight(plight):
                        playerNode.clearLight(plight)

        return task.cont

#==================================================================================
#================= Misc. Initialization ===========================================
    def initSun(self, parentNode):
        # Setup directional light (a yellowish sun)
        sun = DirectionalLight('sun')
        sun.setColor(VBase4(0.25, 0.25, 0, 1))
        sun.getLens().setNearFar(5.5, 500)
        sun.getLens().setFilmSize(24, 36)
        #sun.showFrustum()
        sun.setShadowCaster(True, 4096, 4096) 

        self.sunNode = parentNode.attachNewNode(sun)
        self.sunNode.setP(-130)
        #self.sunNode.setPos(0, 0, 10)
        #self.sunNode.lookAt(0, 0, 0)

        parentNode.setLight(self.sunNode)

        # Setup ambient light (a grey/blueish secondary sun color)
        ambientLight = AmbientLight('alight')
        ambientLight.setColor(VBase4(0.1, 0.1, 0.2, 1))

        ambientLightNode = parentNode.attachNewNode(ambientLight)

        parentNode.setLight(ambientLightNode)

    def initFilters(self):
        # Initialize filters
        self.filters = CommonFilters(base.win, base.cam)

        # Cannot get the bloom filter to work
        #self.filters.setBloom(desat=-0.5, intensity=3.0, size='large')

        # Cartoon ink could maybe be nice, with a thin line?
        #self.filters.setCartoonInk(separation=0.5)

        # Nice sun ray effect, although it sets a special mood
        #self.filters.setVolumetricLighting(caster=self.sunNode, numsamples=100, density=1.0, decay=0.98, exposure=0.05)

        # Maybe use a little blur, might be nice? (can also sharpen with values over 1, i.e. blur: 0-1, sharpen:1-2)
        #self.filters.setBlurSharpen(amount=0.8)

        # Could not see an effect
        #self.filters.setAmbientOcclusion()
