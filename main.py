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

        self.player = player.Player(self.mainNode, self.AIworld)

        self.gui = gui.GUI()
        self.hud = hud.HUD(self.player)

        # For debugging
        if debug:
            self.enemy = enemy.Enemy(self.mainNode, 
                                    self.enemyList, 
                                    self.player,
                                    50,
                                    self.AIworld,
                                    self)
            self.enemy.moveEnemy(0, 15)

            self.accept('1', self.damagePlayer)
            self.accept('2', self.killEnemy)
            self.accept('3', self.outputInfo)
            self.accept('4', self.outputTime)
            self.accept('5', self.addEnemy)
            self.accept('6', self.levelPlayerUp)
            self.accept('7', self.healPlayer)

            #base.cTrav.showCollisions(base.render)

    # Start of debugging methods implementation
    def damagePlayer(self):
        self.player.receiveDamage(self.player.maxHealthPoints - utils.getD8())

    def killEnemy(self):
        self.enemy.onDeath()

    def outputInfo(self):
        print('player pos: ' + str(self.player.playerNode.getPos()))

    def outputTime(self):
        print(str(globalClock.getFrameTime()))

    def addEnemy(self):
        newEnemy = enemy.Enemy(self.mainNode, 
                               self.enemyList,
                               self.player,
                               50,
                               self.AIworld,
                               self)
        newEnemy.moveEnemy(10 - utils.getD20(), 
                           10 - utils.getD20())

    def levelPlayerUp(self):
        for i in range(10):
            self.player.increaseLevel()

    def healPlayer(self):
        self.player.heal(self.player.maxHealthPoints)

    # End of debugging implementation

    def initAI(self):
        # Create the AI world
        self.AIworld = AIWorld(self.mainNode)

        # AI World update
        AiUpdateTask = taskMgr.add(self.AIUpdate, 'AIUpdateTask')
        AiUpdateTask.last = 0

    def AIUpdate(self, task):
        # Make sure we're not taking too long
        deltaTime = task.time - task.last
        task.last = task.time

        if deltaTime > .2: 
            return task.cont

        # Update Ai world
        self.AIworld.update()

        return task.cont

World()
run()
