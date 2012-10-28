from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
import random

def getIsInRange(pos1, pos2, threshold=100):
    xDiff = abs(pos1.getX() - pos2.getX())
    yDiff = abs(pos1.getY() - pos2.getY())
    if xDiff < threshold and yDiff < threshold:
        return True 

    return False

def getD6():
    return random.randint(1, 6)

def getD8():
    return random.randint(1, 8)

def getD20():
    return random.randint(1, 20)

def fromCol(parent,handler,type,mask = BitMask32.allOn(),debug=False): 
        """Setup a from collision solid. 
        
        Last I checked CollisionPolygon 's and CollisionTube 's can't be used 
        as from solids. If you pass one, it won't hit anything""" 
        nodepath = parent.attachNewNode(CollisionNode('frmcol')) 
        nodepath.node().addSolid(type)#add the solid to the new collisionNode 
        nodepath.node().setFromCollideMask(mask)#allow selective masking 
        nodepath.setCollideMask(BitMask32.allOff())#it's a from solid only. 
        ####uncomment this line to make the collision solid visible: 
        if debug:
            nodepath.show() 
        
        base.cTrav.addCollider(nodepath, handler)#add to the traverser 
        try:#the next line doesn't work on queues. (not necessary) 
            handler.addCollider(nodepath, parent)#keep the ward out of trouble 
        except: 
            pass#Don't care. This method needs to work on queues too. 
        return nodepath#we might need the new CollisionNode again later.     

class MouseHandler():

    def __init__(self, playerRef):
        self._playerRef = playerRef
        self.setupMouseCollision()

    def setupMouseCollision(self):
        self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))

        DO = DirectObject()
        DO.accept('mouse1', self.onClick)

    def onClick(self):
        #print('click')
        if base.mouseWatcherNode.hasMouse():
            mousePos = base.mouseWatcherNode.getMouse()
            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()

            base.camLens.extrude(mousePos, nearPoint, farPoint)
            if self.plane.intersectsLine(pos3d, 
                        base.render.getRelativePoint(camera, nearPoint),
                        base.render.getRelativePoint(camera, farPoint)):
                #print('Mouse ray intersects ground at ', pos3d)
                self._playerRef.setPlayerDestination(pos3d)
