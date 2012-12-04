from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

import time
import requests
import jsondate as json

import utils


class GUI(object):
    _BASE_URL = 'http://fmr-api-507.herokuapp.com/api'

    #_rButtonValue = [0]
    _overlayVisible = False

    def __init__(self, mainRef):
        print("GUI class instantiated")
        self._stateHandlerRef = mainRef.stateHandler

        self.initializeGUI()
        self.toggleOverlayFrame()

#------------------------------- DATA HANDLING ----------------------------------------#
    def initializeGUI(self):
        question_sets_response = requests.get('{}/question_set'.format(self._BASE_URL))
        self.question_sets = json.loads(question_sets_response.text)

        self.create_user()

    def extract_question_set(self, question_set):
        """Extracts a single questions set by checking if the string in
           question_set is in any of the question_set's names.
            Param:
                question_set: A string from the constants in states.py
            Returns:
                A dictionary with the whole question_set
        """
        for qs in self.question_sets['objects']:
            if question_set.lower() in qs['name'].lower():
                return qs
        return self.question_sets

    def get_last_users_scenario(self):
        """Returns the lastest user's scenario and returns it as an int."""
        all_participants = requests.get('{}/participant'.format(self._BASE_URL))
        # getting the total number of participants allows us to find the latest one
        number_of_participants = json.loads(all_participants.text)['num_results']
        # then we can get that participant's scenario
        p = requests.get('{}/participant/{}'.format(self._BASE_URL, number_of_participants))
        return json.loads(p.text)['scenario']

    def create_user(self):
        """This method must be called after get_last_users_scenario() - Why?"""
        # TODO: Handle when user cannot be created, RuntimeError or similar
        #       Check if possible to let people know that there is
        #       something wrong with their connection.
        participant_data = {'scenario': 1 if self.get_last_users_scenario() == 0 else 0}
        r = requests.post('{}/participant'.format(self._BASE_URL),
                      data=json.dumps(participant_data),
                      headers={'content-type': 'application/json'})
        self.participant_id = json.loads(r.text)['id']
        return participant_data['scenario']

    def get_wants_to_continue(self):
        '''This method returns the user's last 'I want to continue playing' answer
            to be used to evaluate whether to return to Play state (again) or not
        '''
        return True

    def save_answer(self, question_id, answer):
        """POSTs answer to server.
            Params:
                question_id: a string or int of the question
                answer: the user's answer as a string
            Returns:
                True if response is 201 (a new resource created)
                False otherwise
        """
        question_data = {'participant_id': self.participant_id,
                         'question_id': question_id, 'answer': answer}
        r = requests.post('{}/answer'.format(self._BASE_URL),
                      data=json.dumps(question_data),
                      headers={'content-type': 'application/json'})
        return True if r.status_code == 201 else False

#---------------------------------- VISUAL GUI ---------------------------------------#
    def toggleOverlayFrame(self):
        if self._overlayVisible:
            #print "Toggle off"
            self.onQuestionsDone()
            self._overlayVisible = False
        else:
            #print "Toggle on"
            self.initializeOverlayFrame()
            self._overlayVisible = True

            states = self._stateHandlerRef
            if states.state == states.PLAY:
                states.request(states.DURING)

    def initializeOverlayFrame(self):
        self.canvasWidth = 1
        canvasHeight = 1
        self.overlayFrame = DirectFrame(
            frameSize=(-self.canvasWidth, self.canvasWidth, -canvasHeight, canvasHeight),
            pos=(0, 1, 0),
            sortOrder=10)

        doneButton = DirectButton(
           parent=self.overlayFrame,
           pos=(self.canvasWidth-.1, 0, -(canvasHeight-.1)),
           scale=0.05,
           pad=(.2, .2, .2, .2),
           text=('Next'),
           pressEffect=1,
           command=self.onQuestionsDone)

        questionSet = self.extract_question_set(self._stateHandlerRef.state)
        #print 'questionSet:', questionSet

        name = questionSet['name']
        infoText = questionSet['info_text']
        questions = questionSet['questions']

        DirectLabel(
            parent=self.overlayFrame,
            text=name,
            scale=0.09,
            pos=(0, 0, canvasHeight-.1))

        DirectLabel(
            parent=self.overlayFrame,
            text=infoText,
            scale=.06,
            pos=(0, 0, canvasHeight-.25),
            text_wordwrap=30)

        self.answersList = []
        self.firstButtonValue = None
        #self.secondButtonValue = None
        self.notFinishedText = None

        yPos = 0.0
        yInc = .4
        questionsPerPage = 4
        for item in questions:
            print item
            self.addInfoText(item['info_text'], yPos)
            self.addQuestion(item['question'], yPos)

            if item['type'] == 3 or item['type'] == 1: # Text input single line / essay
                self.addTextInputField(yPos)
            elif item['type'] in (2,4): # Likert scales and multiple choices
                q = requests.get('{}/question/{}'.format(self._BASE_URL, item['id']))
                self.addLikertScaleButtons(yPos, json.loads(q.text)['choices'])

            yPos += yInc

            if yPos >= yInc * questionsPerPage:

                break

    #def nextPage(self):


    def addQuestion(self, questionText, yPos):
        yStart = .6
        OnscreenText(
            parent=self.overlayFrame,
            text=questionText,
            scale=.05,
            wordwrap=20,
            pos=(-.8, yStart-yPos),
            align=TextNode.ALeft)

    def addInfoText(self, infoText, yPos):
        #print 'add info text:', infoText
        yStart = 0.5
        OnscreenText( # might want to apply slanted or italics to this one
            parent=self.overlayFrame,
            text=infoText,
            scale=.04,
            wordwrap=25,
            pos=(-.8, yStart-yPos),
            align=TextNode.ALeft)

    def addTextInputField(self, yPos, short=True):
        numLines = 1 if short == True else 3
        yStart = .43
        inputField = DirectEntry(
            parent=self.overlayFrame,
            text='',
            scale=.05,
            command=None,
            pos=(-.8, 0, yStart-yPos),
            initialText='',
            frameColor=(0.4, 0.4, 0.4, 0.75),
            width=27,
            numLines=numLines
            #focus=1
            )
        self.answersList.append(inputField)

    def addLikertScaleButtons(self, yPos, choices):
        buttons = []

        for i,item in enumerate(choices):
            xStart = .8
            spacePerElement = .27
            if len(choices) == 2:
                spacePerElement = .4
                xStart = .75
            
            xPos = (i * spacePerElement) - xStart
            yStart = .5

            OnscreenText(
                parent=self.overlayFrame,
                text=item['choice_text'],
                scale=0.04,
                pos=(xPos, yStart-yPos),
                #frameColor=(0, 0, 0, 0),
                wordwrap=7
                )

            buttonVariable = self.firstButtonValue if self.firstButtonValue == None else self.secondButtonValue
            button = DirectRadioButton(
                parent=self.overlayFrame,
                pos=(xPos+.02, 0, yStart-yPos-.05),
                variable=[buttonVariable],
                value=[item['id']],
                scale=0.04,
                frameColor=(1, 1, 1, 0),
                indicatorValue=0
                )
            buttons.append(button)

        for button in buttons:
            button.setOthers(buttons)

    def showNotFinishedText(self):
        if self.notFinishedText == None:
            self.notFinishedText = OnscreenText(
                parent=self.overlayFrame,
                text='Please answer all questions before progressing',
                pos=(0, -.9),
                fg=(1, 0, 0, 1)
                )

    def onQuestionsDone(self):
        allAnswered = True
        for answer in self.answersList:
            print 'answer found:', answer['text'], 'type:', type(answer)
            if answer['text'] == '':
                print 'answer text not filled out'
                allAnswered = False
        if self.firstButtonValue is None:
            print 'button not filled out'
            allAnswered = False
        # if self.secondButtonValue is None and not self._stateHandlerRef.state == self._stateHandlerRef.AFTER:
        #     allAnswered = False

        if allAnswered == False:
            self.showNotFinishedText()
        else:
            self.overlayFrame.destroy()

            states = self._stateHandlerRef
            if states.state == states.BEFORE:
                states.request(states.PLAY)
            elif states.state == states.DURING and self.get_wants_to_continue():
                states.request(states.PLAY)  # Change
            else:
                print 'End game'

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

