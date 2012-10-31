import direct.directbase.DirectStart
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.ai import *
import sys

from src import utils, player, enemy, gui, hud, map

class World(ShowBase):

    # Global debug setting
    global debug 

    # Array of enemies
    enemyList = []

    def __init__(self):
        print('World class instantiated')
        # Enable or disable debugging
        debug = True

        # Set background color
        base.setBackgroundColor(0.1, 0.1, 0.1, 1)

        # Main game node
        self.mainNode = render.attachNewNode('mainNode')

        # Create the main traverser
        base.cTrav = CollisionTraverser()
        # Fluid move prevents quantum tunnelling. 
        base.cTrav.setRespectPrevTransform(True)

        # Initialize global AI
        self.initAI()

        # Instantiate other classes
        self.mapHandler = map.Map(self.mainNode)

        self.player = player.Player(self)
        self.player.setPlayerStartPosition(self.mapHandler.startPos)

        self.gui = gui.GUI()
        self.hud = hud.HUD(self.player)

        self.accept('escape', self.endGame)

        # For debugging
        if debug:
            self.addEnemy()

            self.accept('1', self.damagePlayer)
            self.accept('2', self.killEnemy)
            self.accept('3', self.outputInfo)
            self.accept('4', self.outputTime)
            self.accept('5', self.addEnemy)
            self.accept('6', self.levelPlayerUp)
            self.accept('7', self.healPlayer)
            self.accept('8', self.showAllCollisions)
            self.accept('9', self.printStats)

            self.showCollisions = False

    # Start of debugging methods implementation
    def damagePlayer(self): # key 1
        self.player.receiveDamage(self.player.maxHealthPoints - utils.getD8())

    def killEnemy(self): # key 2
        self.enemy.onDeath()

    def outputInfo(self): # key 3
        print('player pos: ' + str(self.player.playerNode.getPos()))

    def outputTime(self): # key 4
        print(str(globalClock.getFrameTime()))

    def addEnemy(self): # key 5
        attributes = enemy.koboldMinion

        newEnemy = enemy.Enemy(self, 'funny_sphere', attributes)
        #newEnemy.moveEnemy(10 - utils.getD20(), 
        #                   10 - utils.getD20())
        newEnemy.moveEnemy(self.mapHandler.exitPos.getX(), self.mapHandler.exitPos.getY())

    def levelPlayerUp(self): # key 6
        for i in range(10):
            self.player.increaseLevel()

    def healPlayer(self): # key 7
        self.player.heal(self.player.maxHealthPoints)

    def showAllCollisions(self): # key 8
        if self.showCollisions:
            base.cTrav.hideCollisions()
            self.showCollisions = False
        else:
            base.cTrav.showCollisions(base.render)
            self.showCollisions = True

    def printStats(self): # key 9
        print('Strength: ' + str(self.player.strength))
        print('Constitution: ' + str(self.player.constitution))
        print('Dexterity: ' + str(self.player.dexterity))
        print('Movement speed: ' + str(self.player.movementSpeed))
        print('Combat range: ' + str(self.player.combatRange))
        print('Current health: ' + str(self.player.currentHealthPoints))
        print('Max health: ' + str(self.player.maxHealthPoints))
        if self.player.getCurrentTarget() is not None:
            print('Target pos: ' + str(self.player.getCurrentTarget().enemyNode.getPos()))
  


    # End of debugging implementation

    def initAI(self):
        # Create the AI world
        self.AIworld = AIWorld(self.mainNode)

        # AI World update
        AiUpdateTask = taskMgr.add(self.AiUpdate, 'AIUpdateTask')
        AiUpdateTask.last = 0

    def AiUpdate(self, task):
        # Make sure we're not taking too long
        deltaTime = task.time - task.last
        task.last = task.time

        if deltaTime > .2: 
            return task.cont

        # Update Ai world
        self.AIworld.update()

        return task.cont

    def endGame(self):
        sys.exit()

World()
run()
