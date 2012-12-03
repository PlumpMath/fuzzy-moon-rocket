from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from direct.task import Task
import sys

import player

class HUD:

    def __init__(self, playerRef):
        print("HUD class instantiated")

        self._playerRef = playerRef
        self._stateHandlerRef = playerRef._mainRef.stateHandler

        # self.gameText = OnscreenText(
        #                         text="Fuzzy Moon Rocket",
        #                         pos=(1, 0.9),
        #                         bg=(0.25, 0.25, 0.25, 1),
        #                         shadow=(.1, .1, .1, 1))

        self.initHealthBar()
        self.initEXPBar()
        self.initTargetBar()
        self.initStatsButton()
        self.initPlayerAbilityBar()
        self.initQuest()

        self.showAreaTransDialog = False

        taskMgr.doMethodLater(1, self.updateBars, 'UpdateBarsTask')

    def initTargetBar(self):
        self.targetBar = DirectWaitBar(
                                    text='Target health',
                                    value=1,
                                    pos=(0.1, 0, 0.9),
                                    scale=0.5)
        self.targetBar.hide()

    def updateTargetBar(self):
        currentTarget = self._playerRef.getCurrentTarget()
        if not currentTarget is None and not currentTarget.getIsDead() and self._stateHandlerRef.state == self._stateHandlerRef.PLAY:
                self.targetBar.show()
                self.targetBar['value'] = currentTarget.getCurrentHealthPointsAsPercentage()
        else:
                # Hide bar
                self.targetBar.hide()

    def initStatsButton(self):
        self.statsButton = DirectButton(
                                    text ='Stats',
                                    pos=(1, 0, -0.9),
                                    scale=.05,
                                    command=self.toggleStats)

        self._showingStats = False

    def toggleStats(self):
        if not self._showingStats:
            self._showingStats = True

            self.statsFrame = DirectFrame(
                frameColor=(1, 1, 1, 1),
                frameSize=(-0.5, 0.5, -0.5, 0.5),
                pos=(1.0, -0.5, 0.0),
                frameTexture='gui/Stats_Window.png'
                )

            closeButton = DirectButton(
                 text='x',
                 pos=(.4, 0, .4),
                 scale=.05,
                 parent=self.statsFrame,
                 command=self.exitStats)

            def addStats(pos, text):
                    return OnscreenText(text=text,
                                        pos=(-0.4, pos),
                                        fg=(.5, .1, .1, 1),
                                        bg=(.1, .5, .5, .25), # Tweak bg and fg to make text easily readable
                                        shadow=(0, 0, 0, 1),
                                        scale=0.05,
                                        parent=self.statsFrame,
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
        self.statsFrame.destroy()

    def initHealthBar(self):
        self.healthBar = DirectWaitBar(
                                text='Health',
                                value=100,
                                pos=(0, 0, -0.8),
                                scale=0.75)
        self.healthBar.hide()

    def updateBars(self, task):
        self.updateHealthBar()
        self.updateEXPBar()
        self.updateTargetBar()
        self.updateAreaTransDialog()
        self.updateStatsButton()

        # Continue calling task again after initial delay
        return task.again

    def updateStatsButton(self):
        if self._stateHandlerRef.state == self._stateHandlerRef.PLAY:
            if self.statsButton.is_hidden():
                self.statsButton.show()
        else:
            if not self.statsButton.is_hidden():
                self.statsButton.hide()

    def updateHealthBar(self):
        if self._stateHandlerRef.state == self._stateHandlerRef.PLAY:
            if self.healthBar.is_hidden():
                self.healthBar.show()

            self.healthBar['value'] = self._playerRef.getCurrentHealthPointsAsPercentage()
        else:
            if not self.healthBar.is_hidden():
                self.healthBar.hide()

    def updateAreaTransDialog(self):
        player = self._playerRef

        if player.areaTransitioning and not self.showAreaTransDialog:
            self.showAreaTransDialog = True
            self.areaTransDialog = YesNoDialog(dialogName='AreaTransitionDialog',
                                            text='Do you want to transition to the next area?',
                                            fadeScreen=0,
                                            command=self.areaTransAnswer)
        elif not player.areaTransitioning and self.showAreaTransDialog:
            self.showAreaTransDialog = False
            self.areaTransDialog.cleanup()

    def areaTransAnswer(self, arg):
        player = self._playerRef
        mapRef = player._mapHandlerRef

        if self.showAreaTransDialog and player.areaTransitioning:
            if arg:
                #print 'Yes answered'
                mapRef.loadNextArea()
            else:
                #print 'No answered'
                pass

        player.areaTransitioning = False
        self.showAreaTransDialog = False
        self.areaTransDialog.cleanup()

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
        self.expBar.hide()

    def updateEXPBar(self):
        if self._stateHandlerRef.state == self._stateHandlerRef.PLAY:
            if self.expBar.is_hidden():
                self.expBar.show()

            self.expBar['value'] = self._playerRef.getEXPToNextLevelInPercentage()

            self._newEXPBarText = (str(int(self._playerRef.experience)) +
                                ' / ' +
                                str(int(self._playerRef.getEXPToNextLevel())) +
                                ' experience points')

            self.expBarText.setText(self._newEXPBarText)
            self.expBarLvlText.setText('Level ' + str(self._playerRef.level))
        else:
            if not self.expBar.is_hidden():
                self.expBar.hide()

    def initPlayerAbilityBar(self):
        self.abilityBar = DirectFrame(frameColor=(0.7, 0.7, 0.7, 1.0),
                                            pos=(0, 0, -0.95),
                                            pad=(0.4, 0.075))

        scale=.05
        imageUpModifier = .33

        self.offensiveAbilityButton = DirectButton(text=(''),
                                                parent=self.abilityBar,
                                                scale=scale,
                                                pos=(-0.3, 0, -0.01),
                                                image='gui/Bullrush_white.png',
                                                image_pos=(0, 0, imageUpModifier),
                                                command=self._playerRef.fireAbility,
                                                extraArgs=[1])

        self.defensiveAbilityButton = DirectButton(text=(''),
                                                 parent=self.abilityBar,
                                                 scale=scale,
                                                 pos=(-0.1, 0, -0.01),
                                                 image='gui/Unstoppable.png',
                                                 image_pos=(0, 0, imageUpModifier),
                                                 command=self._playerRef.fireAbility,
                                                 extraArgs=[2])

        self.evasiveAbilityButton = DirectButton(text=(''),
                                                 parent=self.abilityBar,
                                                 scale=scale,
                                                 pos=(0.1, 0, -0.01),
                                                 image='gui/Thicket_of_blades.png',
                                                 image_pos=(0, 0, imageUpModifier),
                                                 command=self._playerRef.fireAbility,
                                                 extraArgs=[3])

        self.aoeAbilityButton = DirectButton(text=(''),
                                             parent=self.abilityBar,
                                             scale=scale,
                                             pos=(0.3, 0, -0.01),
                                             image='gui/Shift_the_battlefield.png',
                                             image_pos=(0, 0, imageUpModifier),
                                             command=self._playerRef.fireAbility,
                                             extraArgs=[4])

    def initQuest(self):
        self.questFrame = DirectFrame(frameSize=(-.2, .2, -.25, .25),
                                      pos=(1, 0, .5),
                                      pad=(.2,.2, .2,.2),
                                      frameTexture='gui/Quest_Window.png')
        self.questText = None
        self.addQuest('Explore the farm')

    def addQuest(self, text):
        if self.questText != None:
            self.questText.destroy()

        self.questText = OnscreenText(text='Objective:\n'+text,
                                    pos=(-.15, .15),
                                    fg=(.75, .75, .75, 1),
                                    shadow=(0, 0, 0, .5),
                                    parent=self.questFrame,
                                    scale=.05,
                                    wordwrap=7,
                                    align=TextNode.ALeft)
