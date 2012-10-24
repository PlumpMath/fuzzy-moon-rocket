from direct.gui.DirectGui import DirectButton, DirectWaitBar
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
import sys

import player

class HUD:

	#_playerRef

	def __init__(self, playerRef):
		print("HUD class instantiated")

		self._playerRef = playerRef

		self.gameText = OnscreenText(text = "Fuzzy Moon Rocket",
					pos = (1, 0.9), 
					bg = (0.25, 0.25, 0.25, 1))

		self.initHealthBar()

		taskMgr.add(self.removeTitle, 'RemoveTitleTask')

		taskMgr.add(self.updateHealthBar, 'UpdateHealthBarTask')


	def removeTitle(self, task):
		if task.time > 3:
			self.gameText.destroy()
			self.createExitButton()
			return task.done

		return task.cont

	def createExitButton(self):
		self.exitButton = DirectButton(text = "Exit",
									pos = (1.2, 0, 0.9),
									scale = 0.1,
									command=self.exitGame)

	def exitGame(self):
		sys.exit()

	def initHealthBar(self):
		self.healthBar = DirectWaitBar(text = "Health", 
									value = 100, 
									pos = (0, 0, -0.9),
									scale = 0.75)

	def updateHealthBar(self, task):
		self.healthBar['value'] = self._playerRef.getCurrentHealthPointsAsPercentage()

		# Continue calling task in next frame
		return task.cont