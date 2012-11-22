from direct.gui.DirectGui import DirectButton, DirectWaitBar, DirectFrame
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from direct.task import Task
import sys

import player

class HUD:

    def __init__(self, playerRef):
        print("HUD class instantiated")

        self._playerRef = playerRef

        self.gameText = OnscreenText(
                    text="Fuzzy Moon Rocket",
                    pos=(1.5, 0.9), 
                    bg=(0.25, 0.25, 0.25, 1))

        self.initHealthBar()
        self.initEXPBar()
        self.initTargetBar()
        self.initStatsButton()
        self.initPlayerAbilityBar()

        #taskMgr.add(self.updateBars, 'UpdateBarsTask')
        taskMgr.doMethodLater(1, self.updateBars, 'UpdateBarsTask')
    
    def initTargetBar(self):
        self.targetBar = DirectWaitBar(
                                    text='Target health',
                                    value=1,
                                    pos=(0.1, 0, 0.9),
                                    scale = 0.5)
        self.targetBar.hide()

    def updateTargetBar(self):
        currentTarget = self._playerRef.getCurrentTarget()
        if not currentTarget is None and not currentTarget.getIsDead():
            self.targetBar.show()
            self.targetBar['value'] = currentTarget.getCurrentHealthPointsAsPercentage()
        else:
            # Hide bar
            self.targetBar.hide()

    def initStatsButton(self):
        self.statsButton = DirectButton(
                                text = ("Stats"),
                                pos=(1.2, 0, -0.9), 
                                scale=.05, 
                                command=self.toggleStats)

        self._showingStats = False

    def toggleStats(self):
        if not self._showingStats:
            self._showingStats = True

            self.myFrame = DirectFrame(
                                frameColor=(1, 1, 1, 1),
                                frameSize=(-0.5, 0.5, -0.5, 0.5),
                                pos=(1.0, -0.5, 0.0)
                                )

            self.closeButton = DirectButton(
                                 text='x',
                                 pos=(.3, 0, .45),
                                 scale=.05,
                                 parent=self.myFrame,
                                 command=self.exitStats)

            def addStats(pos, text):
                return OnscreenText(text=text,
                                    pos=(-0.4, pos),
                                    scale=0.05,
                                    parent=self.myFrame,
                                    align=TextNode.ALeft)  

            addStats(0.4, 'Strength: ' + str(self._playerRef.strength))
            addStats(0.3, 'Constitution: ' + str(self._playerRef.constitution))
            addStats(0.2, 'Dexterity: ' + str(self._playerRef.dexterity))

            addStats(0.05, 'Attack Bonus: ' + str(self._playerRef.attackBonus))
            addStats(-0.05, 'Damage Bonus: ' + str(self._playerRef.damageBonus))
            addStats(-0.15, 'Armor Class: ' + str(self._playerRef.armorClass))

            addStats(-0.30, 'Current Health Points: ' + str(self._playerRef.currentHealthPoints))
            addStats(-0.40, 'Max Health Points: ' + str(self._playerRef.maxHealthPoints))
        else:
            self._showingStats = False

            self.exitStats()

    def exitStats(self):
        self.myFrame.destroy()
        
    def initHealthBar(self):
        self.healthBar = DirectWaitBar(
                                    text="Health", 
                                    value=100, 
                                    pos=(0, 0, -0.8),
                                    scale=0.75)

    def updateBars(self, task):
        self.healthBar['value'] = self._playerRef.getCurrentHealthPointsAsPercentage()
        self.updateEXPBar()
        self.updateTargetBar()

        # Continue calling task again after initial delay
        return task.again

    def initEXPBar(self):
        self.expBar = DirectWaitBar(text='',
                                    value=0,
                                    pos=(0, 0, -0.69),
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
        
        self._newEXPBarText = (str(int(self._playerRef.experience)) + 
                                ' / ' + 
                                str(int(self._playerRef.getEXPToNextLevel())) + 
                                ' experience points')

        self.expBarText.setText(self._newEXPBarText)
        self.expBarLvlText.setText('Level ' + str(self._playerRef.level))

    def initPlayerAbilityBar(self):
        self.abilityBar = DirectFrame(frameColor=(0.2, 0.2, 0.8, 1.0),
                                      pos=(0, 0, -0.95),
                                      pad=(0.4, 0.075))

        self.offensiveAbilityButton = DirectButton(text=('Off'),
                                                   parent=self.abilityBar,
                                                   scale=0.075,
                                                   pos=(-0.3, 0, -0.01),
                                                   command=self._playerRef.fireAbility,
                                                   extraArgs=[1])

        self.defensiveAbilityButton = DirectButton(text=('Def'),
                                                   parent=self.abilityBar,
                                                   scale=0.075,
                                                   pos=(-0.1, 0, -0.01),
                                                   command=self._playerRef.fireAbility,
                                                   extraArgs=[2])

        self.evasiveAbilityButton = DirectButton(text=('Eva'),
                                                 parent=self.abilityBar,
                                                 scale=0.075,
                                                 pos=(0.1, 0, -0.01),
                                                 command=self._playerRef.fireAbility,
                                                 extraArgs=[3])

        self.aoeAbilityButton = DirectButton(text=('AoE'),
                                             parent=self.abilityBar,
                                             scale=0.075,
                                             pos=(0.3, 0, -0.01),
                                             command=self._playerRef.fireAbility,
                                             extraArgs=[4])