from direct.gui.DirectGui import DirectButton, DirectWaitBar
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame
from direct.task import Task
import sys

import player

class HUD:

    def __init__(self, playerRef):
        print("HUD class instantiated")

        self._playerRef = playerRef

        self.gameText = OnscreenText(
                    text="Fuzzy Moon Rocket",
                    pos=(1, 0.9), 
                    bg=(0.25, 0.25, 0.25, 1))

        self.initHealthBar()
        self.initEXPBar()
        self.initTargetBar()
        self.createStatsButton()

        taskMgr.add(self.removeTitle, 'RemoveTitleTask')

        taskMgr.add(self.updateBars, 'UpdateBarsTask')
    
    def initTargetBar(self):
        self.targetBar = DirectWaitBar(
                                    text="Target health",
                                    value=1,
                                    pos=(0.1, 0, 0.9),
                                    scale = 0.5)
        self.targetBar.hide()

    def updateTargetBar(self):
        currentTarget = self._playerRef.getCurrentTarget()
        if not currentTarget is None:
            if not currentTarget.getIsDead():
                self.targetBar.show()
                self.targetBar['value'] = currentTarget.getCurrentHealthPointsAsPercentage()
        else:
            # Hide bar
            self.targetBar.hide()

    def removeTitle(self, task):
        if task.time > 3:
            self.gameText.destroy()
            self.createExitButton()
            return task.done

        return task.cont

    def createStatsButton(self):
        self.statsButton = DirectButton(
                                text = ("Stats"),
                                pos=(1.2, 0, -0.9), 
                                scale=.05, 
                                command=self.showStats)

    
    def showStats(self):
            self.myFrame = DirectFrame(
                                frameColor=(1, 1, 1, 1),
                                frameSize=(-0.5, 0.5, -0.5, 0.5),
                                pos=(1.0, -0.5, 0.0)
                                )
            

            self.statsButton = DirectButton(
                                text = ("close"),
                                pos=(1.0, 0.30, -0.45), 
                                scale=.05, 
                                command=self.exitStats)

            def addStats(pos, text):
                    return OnscreenText(text=text,
                                        pos=(1.0, pos),
                                        scale=0.05,
                                        mayChange=1)  
            self.stat1 = addStats(0.35, 'Strength: ' + str(self._playerRef.strength))
            self.stat2 = addStats(0.25, 'Constitution: ' + str(self._playerRef.constitution))
            self.stat3 = addStats(0.15, 'Dexterity: ' + str(self._playerRef.dexterity))


    def exitStats(self):
        self.myFrame.destroy()
        self.statsButton.destroy()
        self.stat1.destroy()
        self.stat2.destroy()
        self.stat3.destroy()

    def createExitButton(self):
        self.exitButton = DirectButton(
                                    text="Exit",
                                    pos=(1.2, 0, 0.9),
                                    scale=0.1,
                                    command=self.exitGame)

    def exitGame(self):
        sys.exit()

    def initHealthBar(self):
        self.healthBar = DirectWaitBar(
                                    text="Health", 
                                    value=100, 
                                    pos=(0, 0, -0.9),
                                    scale=0.75)

    def updateBars(self, task):
        self.healthBar['value'] = self._playerRef.getCurrentHealthPointsAsPercentage()
        self.updateEXPBar()
        self.updateTargetBar()
        # Continue calling task in next frame
        return task.cont

    def initEXPBar(self):
        self.expBar = DirectWaitBar(text='',
                                    value=0,
                                    pos=(0, 0, -0.79),
                                    scale=0.5,
                                    barColor=(0, 1, 0, 0.5))
        
        self.expBarText = OnscreenText(text='',
                                    parent=self.expBar,
                                    pos=(0.2, -0.025),
                                    scale=0.1,
                                    mayChange=1)
        
        self.expBarLvlText = OnscreenText(text='',
                                        parent=self.expBar,
                                        pos=(-0.8, -0.025),
                                        scale=0.1,
                                        mayChange=1)

    def updateEXPBar(self):
        self.expBar['value'] = self._playerRef.getEXPToNextLevelInPercentage()
        
        self._newEXPBarText = (str(self._playerRef.experience) + 
                                ' / ' + 
                                str(self._playerRef.getEXPToNextLevel()) + 
                                ' experience points')

        self.expBarText.setText(self._newEXPBarText)
        self.expBarLvlText.setText('Level ' + str(self._playerRef.level))