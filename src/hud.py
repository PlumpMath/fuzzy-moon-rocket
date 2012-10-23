from direct.gui.DirectGui import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.task import Task
import sys

class HUD:

	def __init__(self):
		print("HUD class instantiated")

		self.gameText = OnscreenText(text = "Fuzzy Moon Rocket",
					pos = (1, 0.9), 
					bg = (0.25, 0.25, 0.25, 1))

		taskMgr.add(self.removeTitle, 'RemoveTitleTask')


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
