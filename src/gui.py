import time
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DirectRadioButton

class GUI(object):
    _CHOICES = {0: 'Disagree strongly', 1: 'Disagree moderately', 2: 'Disagree a little',
               3: 'Neither agree nor disagree', 4: 'Agree a little', 5: 'Agree moderately',
               6: 'Agree strongly'}
    _rButtonValue = [0]
    _overlayFrame = None
    _overlayVisible = False
    _buttons = []
    _buttonLabels = []
    _rButtonFrame = None
    done = False

    def __init__(self):
        print("GUI class instantiated")
        taskMgr.add(self.recordTime, 'RecordTimeTask')

        self.startTime = time.time()
        #print("startTime : " + str(self.startTime))

    def recordTime(self, task):
        self.currentTime = time.time()
        self.elapsedSeconds = self.currentTime - self.startTime
        #print("elapsedSeconds: " + str(self.elapsedSeconds))

        return task.cont

    def toggleOverlayFrame(self):
        if self._overlayVisible:
            self._overlayFrame.destroy()
            self._overlayVisible = False
        else:
            self._overlayFrame = DirectFrame(frameColor=(1, 1, 1, 1),
                                           # (Left,Right,Bottom,Top)
                                           frameSize=(-1.4, 1.4, 1, -1),
                                           pos=(0, 0, 0))
            self._rButtonFrame = DirectFrame(parent=self._overlayFrame, pos=(-0.5, 0, 0.2))
            self.setupButtons()
            self._overlayVisible = True

    def setupButtons(self):
        self._buttons = []
        for i, question in self._CHOICES.iteritems():
            xOffset = ((i * 15) / 100.0)
            xPos = len(question) / 100.0 + 0.02 + xOffset
            yPos = len(question)/100.0+0.07
            self._buttonLabels.append(DirectLabel(parent=self._rButtonFrame,
                                                  text=question, scale=0.07,
                                                  hpr=(0, 0, -45.0),
                                                  pos=(xPos, 0, yPos),
                                                  frameColor=(0, 0, 0, 0)))
            self._buttons.append(DirectRadioButton(parent=self._rButtonFrame,
                                                   pos=(xOffset, 0, 0),
                                                   variable=self._rButtonValue,
                                                   value=[i], scale=0.05,
                                                   frameColor=(1, 1, 1, 0),
                                                   indicatorValue=0))

        for button in self._buttons:
            button.setOthers(self._buttons)
