import time
import requests
import jsondate as json
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DirectRadioButton, DirectEntry

class GUI(object):
    _BASE_URL = 'http://localhost:5001/api'
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

        self.questions = requests.get('{}/question'.format(self._BASE_URL))
        self.questions_dict = self.extract_questions()

        self.startTime = time.time()
        #print("startTime : " + str(self.startTime))

        # just to test that HTTP requests are working
        r = requests.get('http://api.github.com/users/octocat/orgs')
        DirectLabel(text=r.headers['date'], scale=0.09, hpr=(0, 0, 0),
                    pos=(0, 0, 0.7), frameColor=(0, 0, 0, 0))

    def get_last_scenario(self):
        all_participants = requests.get('{}/participant'.format(self._BASE_URL))
        # getting the total number of participants allows us to find the latest one
        number_of_participants = json.loads(self.all_participants.text)['num_results']
        # then we can get that participants scenario
        p = requests.get('{}/participant/{}'.format(self._BASE_URL, number_of_participants))
        return json.loads(p.text)['scenario']

    def create_user(self):
        """This method must be called after get_last_scenario()"""
        # uuid needs to be generated
        scenario = 1 if self.get_last_scenario() == 0 else 0
        # post the user to database

    def save_answer(self, question_id, answer):
        """question_id is a string or int of the question
           answer is the user's answer as a string
        """
        pass

    def extract_questions(self):
        return json.loads(self.questions.text)['objects']

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
            self._rButtonFrame = DirectFrame(
                parent=self._overlayFrame, pos=(-0.5, 0, 0.2))
            self.build_likert_question()
            self._overlayVisible = True

    def build_likert_question(self):
        self._buttons = []
        for i, label in enumerate(self._LABELS):
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
