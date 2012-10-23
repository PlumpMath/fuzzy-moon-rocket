from direct.showbase.DirectObject import DirectObject

class MouseHandler(DirectObject):

	mouseX = 0
	mouseY = 0

	def __init__(self):
		self.accept('mouse1', self.move)

	def move(self):
		# Get mouse position
		if base.mouseWatcherNode.hasMouse():
			self.mouseX = base.mouseWatcherNode.getMouseX()
			self.mouseY = base.mouseWatcherNode.getMouseY()

		print ("x: " + str(self.mouseX) + ", y: " + str(self.mouseY))