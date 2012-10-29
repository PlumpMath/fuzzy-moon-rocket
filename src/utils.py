from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
import random

enemyDictionary = {}

def getIsInRange(pos1, pos2, threshold=10):
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

class MouseHandler():

    def __init__(self, playerRef):
        self._playerRef = playerRef
        self.setupMouseCollision()

    def setupMouseCollision(self):
        self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))

        DO = DirectObject()
        DO.accept('mouse1', self.onClick)

        self.collisionHandler = CollisionHandlerQueue()

        self.pickerCollNode = CollisionNode('mouseRay')
        self.pickerNodePath = camera.attachNewNode(self.pickerCollNode)
        #self.pickerCollNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerCollNode.addSolid(self.pickerRay)
        base.cTrav.addCollider(self.pickerNodePath, self.collisionHandler)

    def onClick(self):
        #print('click')
        if base.mouseWatcherNode.hasMouse():
            mousePos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mousePos.getX(), mousePos.getY())

            if self.collisionHandler.getNumEntries() > 0:
                self.collisionHandler.sortEntries()
                for i in range(self.collisionHandler.getNumEntries()):
                    entry = self.collisionHandler.getEntry(i).getIntoNodePath()
                    entryName = entry.getName()
                    #print('entry found: ' + entryName)
                    if entryName[:5] == 'enemy' and not entry.isEmpty():
                        enemy = enemyDictionary[entryName]
                        self._playerRef.setCurrentTarget(enemy)

            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()

            base.camLens.extrude(mousePos, nearPoint, farPoint)
            if self.plane.intersectsLine(pos3d, 
                        base.render.getRelativePoint(camera, nearPoint),
                        base.render.getRelativePoint(camera, farPoint)):
                #print('Mouse ray intersects ground at ', pos3d)
                self._playerRef.setPlayerDestination(pos3d)

