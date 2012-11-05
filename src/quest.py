from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

#from panda3d.core import TextNode
class Quest():
	#font = loader.loadFont("cmss12")
	font = TextNode.getDefaultFont()

	#def addQuest(pos, msg):
	
	text_Ins = "Get to the exit"
	textObject = OnscreenText(text=text_Ins,font = font, pos=(-1,-0.95), scale = 0.07, 
								fg =(1,0.3,0.8,1), bg=(0.0,0.0,0.0,1.0))
	
	#text_Obj = "Find the exit"
	#textObject = OnscreenText(text=text_Obj, font = font, pos = (-1,-0.85),scale = 0.07,
	#							fg =(1,0.5,0.5,1), bg=(0.0,0.0,0.0,1.0))

