from panda3d.core import *

class Map:
    def __init__(self, parentNode):
        print("Map class instantiated")
        self.initSun(parentNode)
        self.initGround(parentNode)
        self.initFog(parentNode)

    def initSun(self, parentNode):
        # Setup directional light
        self.dlight = DirectionalLight('dlight')
        self.dlight.setColor(VBase4(1, 1, 0.5, 1))

        self.dlightNode = parentNode.attachNewNode(self.dlight)
        self.dlightNode.setHpr(0, -150, 0)
        parentNode.setLight(self.dlightNode)

    def initGround(self, parentNode):
        # Setup environment (plane)
        self.planeNode = parentNode.attachNewNode('planeNode')
        self.plane = loader.loadModel("models/grass_plane.egg")

        self.plane.setPos(0, 0, 0)
        self.plane.setHpr(0, -90, 0)
        self.plane.setScale(5)

        self.plane.reparentTo(self.planeNode)

        self.planeNode.setName('ground')
        #self.planeNode.setTag('ground, '1')

        self.plane.node().setIntoCollideMask(BitMask32.bit(1))

    def initFog(self, parentNode):
        # Setup fog 
        self.fog = Fog('Fog1')
        self.fog.setColor(0.1, 0.25, 0.25)
        self.fog.setExpDensity(0.05)
        parentNode.setFog(self.fog)