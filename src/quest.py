from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *

#from panda3d.core import TextNode
class Quest:

	def __init__(self):
		print("Quest class instantiated")
		self.addQuest('Get to the exit')


	def addQuest(self, text):
		self.textObject = OnscreenText(text=text, 
									  pos=(-1,-0.95), 
									  scale = 0.07, 
									  fg =(1,0.3,0.8,1), 
									  bg=(0.0,0.0,0.0,1.0),
									  mayChange=1)
	
	#self.addQuest('Get to the exit')
	#text_Obj = "Find the exit"
	#textObject = OnscreenText(text=text_Obj, font = font, pos = (-1,-0.85),scale = 0.07,
	#							fg =(1,0.5,0.5,1), bg=(0.0,0.0,0.0,1.0))

