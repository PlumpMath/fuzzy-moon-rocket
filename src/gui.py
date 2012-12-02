import time
import requests
import jsondate as json
from direct.gui.DirectGui import *

import utils


class GUI(object):
    _BASE_URL = 'http://fmr-api-507.herokuapp.com/api'
    _CHOICES = {
        0: 'Disagree strongly', 1: 'Disagree moderately', 2: 'Disagree a little',
        3: 'Neither agree nor disagree', 4: 'Agree a little', 5: 'Agree moderately',
        6: 'Agree strongly'}
    _rButtonValue = [0]
    # _overlayFrame = None
    _overlayVisible = False
    _buttons = []
    _buttonLabels = []
    # _rButtonFrame = None
    done = False

    def __init__(self, mainRef):
        print("GUI class instantiated")
        self._stateHandlerRef = mainRef.stateHandler

        self.initializeGUI()
        self.toggleOverlayFrame()

    def initializeGUI(self):
        self.questions = requests.get('{}/question'.format(self._BASE_URL))
        self.questions_dict = self.extract_questions()
        print self.questions_dict

        # just to test that HTTP requests are working
        # r = requests.get('http://api.github.com/users/octocat/orgs')
        # DirectLabel(text=r.headers['date'], scale=0.09, hpr=(0, 0, 0),
        #             pos=(0, 0, 0.7), frameColor=(0, 0, 0, 0))

    def extract_questions(self):
        return json.loads(self.questions.text)['objects']

    def get_last_scenario(self):
        # all_participants = requests.get('{}/participant'.format(self._BASE_URL))
        # # getting the total number of participants allows us to find the latest one
        # number_of_participants = json.loads(self.all_participants.text)['num_results']
        # # then we can get that participant's scenario
        # p = requests.get('{}/participant/{}'.format(self._BASE_URL, number_of_participants))
        # return json.loads(p.text)['scenario']
        return utils.getDXY(0, 1)

    def create_user(self):
        """This method must be called after get_last_scenario()"""
        # uuid needs to be generated
        scenario = 1 if self.get_last_scenario() == 0 else 0
        # post the user to database

        return scenario

    def get_wants_to_continue(self):
        '''This method returns the user's last 'I want to continue playing' answer
            to be used to evaluate whether to return to Play state (again) or not
        '''
        return True

    def save_answer(self, question_id, answer):
        """question_id is a string or int of the question
           answer is the user's answer as a string
        """
        pass

    def toggleOverlayFrame(self):
        if self._overlayVisible:
            print "Toggle off"
            self.onQuestionsDone()
            self._overlayVisible = False
        else:
            print "Toggle on"
            self.initializeOverlayFrame()
            self._overlayVisible = True

            states = self._stateHandlerRef
            if states.state == states.PLAY:
                states.request(states.DURING)

    def initializeOverlayFrame(self):
        self.canvasWidth = 1.6
        canvasHeight = 1
        self.overlayFrame = DirectScrolledFrame(
            canvasSize=(-self.canvasWidth, self.canvasWidth, -canvasHeight, canvasHeight),
            frameSize=(-self.canvasWidth, self.canvasWidth, -canvasHeight, canvasHeight),
            pos=(0, 1, 0),
            manageScrollBars=True,
            autoHideScrollBars=True,
            sortOrder=1000)

        self.doneButton = DirectButton(parent=self.overlayFrame.getCanvas(),
                                       pos=(self.canvasWidth-.1, 0, -(canvasHeight-.1)),
                                       scale=0.05,
                                       pad=(.2, .2, .2, .2),
                                       text=('Done'),
                                       pressEffect=1,
                                       command=self.onQuestionsDone)

    def addQuestion(self, questionText, yPos):
        questionFrame = DirectFrame(
                        parent=self.overlayFrame.getCanvas(),
                        #frameSize=(-(self.canvasWidth-.2),self.canvasWidth-.2, -.4,.4),
                        frameColor=(.2, .2, .2, .5),
                        pad=(-.1, .1, -.1, .1),
                        pos=(-1, 0, yPos))
        DirectLabel(parent=questionFrame,
                    text=questionText,
                    scale=.5,
                    text_wordwrap=20)

    def addAnswer(self, question_id, yPos):
        answerFrame = DirectFrame(
                    parent=self.overlayFrame.getCanvas(),
                    #frameSize=(-(self.canvasWidth-.2),self.canvasWidth-.2, -.2,.2),
                    frameColor=(.5, .5, .5, .5),
                    pad=(-.1, .1, -.1, .1),
                    pos=(-1, 0, yPos))

    def build_likert_question(self, question_dict, buttonFrame):
        self.buttons = []
        DirectLabel(parent=buttonFrame, text=question_dict['question'],
                    scale=0.05, pos=(-.3, 0, 0), frameColor=(0, 0, 0, 0),
                    text_wordwrap=20)
        for i, label in enumerate(self._CHOICES):
            xPos = ((i * 40) / 100.0) - 0.6
            yPos = 0.2
            # print 'static + offset', xPos, yPos

            self._buttonLabels.append(
                DirectLabel(
                    parent=self.buttonFrame, text=label, scale=0.05,
                    pos=(xPos, 0, yPos), frameColor=(0, 0, 0, 0),
                    text_wordwrap=7))
            self.buttons.append(
                DirectRadioButton(
                    parent=self.buttonFrame, pos=(xPos, 0, 0),
                    variable=self._rButtonValue, value=[i], scale=0.05,
                    frameColor=(1, 1, 1, 0), indicatorValue=0))

        for button in self.buttons:
            button.setOthers(self.buttons)

    def build_text_question(self, question_dict, textFrame):
        numLines = 5 if question_dict[
            'type'] == 3 else 1  # type == 3 is essay Qs

        DirectLabel(parent=textFrame, text=question_dict['question'],
                    scale=0.05, pos=(-.3, 0, 0), frameColor=(0, 0, 0, 0),
                    text_wordwrap=20)

        DirectEntry(parent=textFrame, text="", scale=.07, command=None,
                    pos=(-.3, 0, .3), initialText="", numLines=numLines, focus=1)

    def onQuestionsDone(self):
        self.overlayFrame.destroy()

        states = self._stateHandlerRef
        if states.state == states.BEFORE:
            states.request(states.PLAY)
        elif states.state == states.DURING and self.get_wants_to_continue():
            states.request(states.PLAY)  # Change
        else:
            print 'End game'
