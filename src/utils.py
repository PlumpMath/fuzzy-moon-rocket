from direct.showbase.DirectObject import DirectObject
from panda3d.core import *
import random

enemyDictionary = {}

def getIsInRange(pos1, pos2, threshold):
    vector = Vec3(pos2 - pos1)
    if vector.lengthSquared() < (threshold * threshold):
        return True

    return False

def getD2():
    return random.randint(1, 2)

def getD4():
    return random.randint(1, 4)

def getD6():
    return random.randint(1, 6)

def getD8():
    return random.randint(1, 8)

def getD10():
    return random.randint(1, 10)

def getD20():
    return random.randint(1, 20)

class MouseHandler():

    _mouseDown = False

    def __init__(self, playerRef):
        print('MouseHandler class instantiated')
        self._playerRef = playerRef
        self._mapHandlerRef = playerRef._mainRef.mapHandler

        self.setupMouseCollision()

    def setupMouseCollision(self):
        self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))

        DO = DirectObject()
        DO.accept('mouse1', self.onClick)
        DO.accept('mouse1-up', self.onMouseUp)

        self.collisionHandler = CollisionHandlerQueue()

        self.pickerCollNode = CollisionNode('mouseRay')
        self.pickerNodePath = camera.attachNewNode(self.pickerCollNode)
        self.pickerCollNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerCollNode.setIntoCollideMask(BitMask32.allOff())
        self.pickerRay = CollisionRay()
        self.pickerCollNode.addSolid(self.pickerRay)
        base.cTrav.addCollider(self.pickerNodePath, self.collisionHandler)

        taskMgr.add(self.moveTask, 'moveTask')
        taskMgr.doMethodLater(0.5, self.highlightExitGate, 'highlightExitGateTask')

    def moveTask(self, task):
        if base.mouseWatcherNode.hasMouse():
            if self._mouseDown:
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

        return task.cont

    def highlightExitGate(self, task):
        if base.mouseWatcherNode.hasMouse():
            highlightGate = False

            mousePos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mousePos.getX(), mousePos.getY())

            if self.collisionHandler.getNumEntries() > 0:
                self.collisionHandler.sortEntries()
                for i in range(self.collisionHandler.getNumEntries()):
                    entry = self.collisionHandler.getEntry(i).getIntoNodePath()
                    entryName = entry.getName()
 
                    if entryName == 'exitGate' and not entry.isEmpty():
                        highlightGate = True
                        break;

            self._mapHandlerRef.highlightExitGate(highlightGate)

        return task.again

    def onClick(self):
        #print('click')
        if base.mouseWatcherNode.hasMouse():
            self._mouseDown = True

            mousePos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mousePos.getX(), mousePos.getY())

            if self.collisionHandler.getNumEntries() > 0:
                self.collisionHandler.sortEntries()
                for i in range(self.collisionHandler.getNumEntries()):
                    entry = self.collisionHandler.getEntry(i).getIntoNodePath()
                    entryName = entry.getName()
 
                    if entryName[:5] == 'enemy' and not entry.isEmpty():
                        enemy = enemyDictionary[entryName]
                        self._playerRef.setCurrentTarget(enemy)
                        break;

                    elif entryName == 'exitGate' and not entry.isEmpty():
                        self._mapHandlerRef.clickExitGate()
                        break;


    def onMouseUp(self):
        #print('mouseUp')
        self._mouseDown = False

