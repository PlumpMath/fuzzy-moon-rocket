import time
import requests
import jsondate as json
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DirectRadioButton, DirectEntry

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

        # just to test that HTTP requests are working
        r = requests.get('http://api.github.com/users/octocat/orgs')
        DirectLabel(text=r.headers['date'], scale=0.09, hpr=(0, 0, 0),
                    pos=(0, 0, 0.7), frameColor=(0, 0, 0, 0))

        # Right now this is just a pile of mess :)
        r = requests.get('http://localhost:5001/api/question')
        print r
        # print r.text
        print r.status_code
        print type(r.status_code)
        r_dict = json.loads(r.text)
        json.loads(r.text)['objects']


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
            self._rButtonFrame = DirectFrame(
                parent=self._overlayFrame, pos=(-0.5, 0, 0.2))
            self.build_likert_question()
            self._overlayVisible = True

    def build_likert_question(self):
        self._buttons = []
        for i, label in enumerate(self._LABELS):
            print 'len', xPos, yPos
            xPos = ((i * 40) / 100.0) - 0.6
            yPos = 0.2
            print 'static + offset', xPos, yPos

            self._buttonLabels.append(
                DirectLabel(
                    parent=self._rButtonFrame, text=label, scale=0.05,
                    pos=(xPos, 0, yPos), frameColor=(0, 0, 0, 0),
                    text_wordwrap=7))
            self._buttons.append(
                DirectRadioButton(
                    parent=self._rButtonFrame, pos=(xPos, 0, 0),
                    variable=self._rButtonValue, value=[i], scale=0.05,
                    frameColor=(1, 1, 1, 0), indicatorValue=0))

        for button in self._buttons:
            button.setOthers(self._buttons)

    def build_text_question(self, question_dict):  # , xPos, yPos):
        xPos = 0
        yPos = 0.2
        numLines = 5 if question_dict['type'] == 3 else 1  # type == 3 is essay Qs

        DirectLabel(parent=self._rButtonFrame, text=question_dict['question'],
                    scale=0.05, pos=(xPos, 0, yPos), frameColor=(0, 0, 0, 0),
                    text_wordwrap=20)

        DirectEntry(text="", scale=.07, command=None,
                    initialText="", numLines=numLines, focus=1)
