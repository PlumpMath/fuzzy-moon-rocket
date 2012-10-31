import time


class GUI(object):
    _LABELS = ["Strongly do not want to continue", "Do not want to continue",
              "Neither", "Want to continue", "Strongly want to continue"]
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
            print "Toggle off"
            self._overlayFrame.destroy()
            self._overlayVisible = False
        else:
            print "Toggle on"
            self._overlayFrame = DirectFrame(frameColor=(1, 1, 1, 1),
                                           # (Left,Right,Bottom,Top)
                                           frameSize=(-1.4, 1.4, 1, -1),
                                           pos=(0, 0, 0))
            self._rButtonFrame = DirectFrame(parent=self._overlayFrame, pos=(-0.5, 0, 0.2))
            self.setupButtons()
            self._overlayVisible = True

    def setupButtons(self):
        self._buttons = []
        for i, label in enumerate(self._LABELS):
            xOffset = ((i * 15) / 100.0)
            xPos = len(label) / 100.0 + 0.02 + xOffset
            yPos = len(label)/100.0+0.07
            self._buttonLabels.append(DirectLabel(parent=self._rButtonFrame,
                                                  text=label, scale=0.07,
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
