from direct.gui.DirectGui import *
from direct.gui.OnscreenText import *
from panda3d.core import *

class Quest:

	def __init__(self):
		print("Quest class instantiated")
		self.addQuest('Get to the exit')

	def addQuest(text):
		self.textQuest = OnscreenText(text=text, 
									  pos=(-1,-0.95), 
									  scale=0.07, 
									  fg =(1,0.3,0.8,1), 
									  bg=(0.0,0.0,0.0,1.0),
									  mayChange=1)

