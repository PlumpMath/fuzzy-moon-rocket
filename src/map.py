from panda3d.core import *
import utils

class Map:
    def __init__(self, parentNode):
        print("Map class instantiated")
        self.initSun(parentNode)
        self.initGround(parentNode)
        self.initFog(parentNode)

    def initSun(self, parentNode):
        # Setup directional light
        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(1, 1, 0.5, 1))

        self.dlightNode = parentNode.attachNewNode(dlight)
        self.dlightNode.setHpr(0, -150, 0)
        parentNode.setLight(self.dlightNode)

    def initGround(self, parentNode):
        # Setup environment (plane)
        self.planeNode = parentNode.attachNewNode('planeNode')
        plane = loader.loadModel("models/grass_plane.egg")
        plane.reparentTo(self.planeNode)
        self.planeNode.setPos(0, 0, 0)
        self.planeNode.setHpr(0, -90, 0)
        self.planeNode.setScale(5)
        self.planeNode.setName('ground')

        collPlane = CollisionPlane(Plane(Vec3(0, 0, .1),
                                    Point3(0, 0, 0)))
        planeCollNodePath = utils.makeCollisionNodePath(self.planeNode, collPlane)

    def initFog(self, parentNode):
        # Setup fog 
        self.fog = Fog('Fog1')
        self.fog.setColor(0.1, 0.25, 0.25)
        self.fog.setExpDensity(0.05)
        #parentNode.setFog(self.fog)

