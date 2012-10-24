from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
import random

def getD6():
    return random.randint(1, 6)

def getD8():
    return random.randint(1, 8)

def getD20():
    return random.randint(1, 20)

class MouseHandler(ShowBase):

    mouseX = 0
    mouseY = 0

    def __init__(self, playerRef):
        self.accept('mouse1', self.move)
        self._playerRef = playerRef
        self.setupMouseCollision()

    def move(self):
        if base.mouseWatcherNode.hasMouse() == False:
            return

        self.returnPos = Vec3(0, 0, 0)

        self.mPos = base.mouseWatcherNode.getMouse()

        self.mPickRay.setFromLens(base.camNode, 
                                    self.mPos.getX(),
                                    self.mPos.getY())

        self.mPickerTraverser.traverse(base.render)

        if self.mCollisionQue.getNumEntries() > 0:
            self.mCollisionQue.sortEntries()
            entry = self.mCollisionQue.getEntry(0)
            pickedObj = entry.getIntoNodePath()
            self.returnPos = pickedObj.getPos()

            if not pickedObj.isEmpty():
                self.returnPos = entry.getSurfacePoint(base.render)

        self._playerRef.move(self.returnPos.getX(),
                            self.returnPos.getY(),
                            self.returnPos.getZ())

    def setupMouseCollision(self):
        #Since we are using collision detection to do picking, we set it up 
        #any other collision detection system with a traverser and a handler
        self.mPickerTraverser = CollisionTraverser()            #Make a traverser
        self.mCollisionQue    = CollisionHandlerQueue()

        #create a collision solid ray to detect against
        self.mPickRay = CollisionRay()
        self.mPickRay.setOrigin(base.camera.getPos(base.render))
        self.mPickRay.setDirection(base.render.getRelativeVector(camera, Vec3(0,1,0)))

        #create our collison Node to hold the ray
        self.mPickNode = CollisionNode('pickRay')
        self.mPickNode.addSolid(self.mPickRay)

        #Attach that node to the camera since the ray will need to be positioned
        #relative to it, returns a new nodepath     
        #well use the default geometry mask
        #this is inefficent but its for mouse picking only

        self.mPickNP = base.camera.attachNewNode(self.mPickNode)

        #well use what panda calls the "from" node.  This is reall a silly convention
        #but from nodes are nodes that are active, while into nodes are usually passive environments
        #this isnt a hard rule, but following it usually reduces processing

        #Everything to be picked will use bit 1. This way if we were doing other
        #collision we could seperate it, we use bitmasks to determine what we check other objects against
        #if they dont have a bitmask for bit 1 well skip them!
        self.mPickNode.setFromCollideMask(GeomNode.getDefaultCollideMask())

        #Register the ray as something that can cause collisions
        self.mPickerTraverser.addCollider(self.mPickNP, self.mCollisionQue)
        #if you want to show collisions for debugging turn this on
        #self.mPickerTraverser.showCollisions(base.render)