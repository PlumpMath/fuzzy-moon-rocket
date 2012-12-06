from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

import sys
sys.path.insert(0, '')

import requests
import json
import math

import utils

class GUI(object):
    _BASE_URL = 'http://fmr-api-507.herokuapp.com/api'

    def __init__(self, mainRef):
        print("GUI class instantiated")
        self._mapRef = None
        self._mainRef = mainRef
        self._statesRef = mainRef.stateHandler

        self.initializeGUI()

#------------------------------- DATA HANDLING ----------------------------------------#
    def initializeGUI(self):
        question_sets_response = requests.get('{}/question_set'.format(self._BASE_URL))
        self.question_sets = json.loads(question_sets_response.text)

        self.participant_scenario = self.create_user()
        self.timesAnswered = 1

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
        if number_of_participants <= 0:
            return 0
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

    def save_time(self, timeInSeconds):
        time_data = {'play_time':timeInSeconds}
        p = requests.put('{}/participant/{}'.format(self._BASE_URL, self.participant_id),
                            data=json.dumps(time_data),
                            headers={'content-type': 'application/json'})
        return True if p.status_code == 201 else False

    def save_answer(self, question_id, answer):
        """POSTs answer to server.
            Params:
                question_id: a string or int of the question
                answer: the user's answer as a string
            Returns:
                True if response is 201 (a new resource created)
                False otherwise
        """

        if self._mapRef is None:
            self._mapRef = self._mainRef.mapHandler

        prevArea = self._mapRef.previousArea
        currArea = self._mapRef.getCurrentArea()

        question_data = {'participant_id': self.participant_id,
                         'question_id': question_id, 
                         'answer': answer}

        if self._statesRef.state == self._statesRef.DURING:
            question_data['times_answered'] = self.timesAnswered
            question_data['previous_area'] = prevArea.areaName
            question_data['current_area'] = currArea.areaName

        r = requests.post('{}/answer'.format(self._BASE_URL),
                      data=json.dumps(question_data),
                      headers={'content-type': 'application/json'})
        return True if r.status_code == 201 else False

#---------------------------------- VISUAL GUI ---------------------------------------#
    def initializeOverlayFrame(self):
        base.disableAllAudio()

        self.canvasWidth = 1
        canvasHeight = 1

        questionSet = self.extract_question_set(self._statesRef.state)
        #print 'questionSet:', questionSet

        questions = questionSet['questions']

        self.pagesList = []
        self.buttonsList = []
        self.answersList = []
        self.answersDict = {}
        self.firstButtonValue = [None]
        self.secondButtonValue = [None]
        self.multipleChoicesAdded = False
        self.notFinishedText = None

        questionsPerPage = 4
        self.amountOfPages = int(math.ceil(len(questions)/float(questionsPerPage)))
        for i in range(self.amountOfPages):
            page = self.addPage(self.canvasWidth, canvasHeight)
            self.addPageTitle(page, questionSet['name'], questionSet['info_text'])

        yPos = 0.0
        yIncrementor = .4
        for i,item in enumerate(questions):
            #print item
            page = self.pagesList[int(math.floor((i / float(questionsPerPage))))]
            info = self.addInfoText(page, item['info_text'], yPos)
            self.addQuestion(page, item['question'], yPos)

            if item['type'] == 3: # Single line is short
                self.addTextInputField(page, yPos, info, item['id'], True)
            elif item['type'] == 1: # Essay is NOT short
                self.addTextInputField(page, yPos, info, item['id'], False)
            elif item['type'] in (2,4): # Likert scales and multiple choices
                qid = item['id']
                q = requests.get('{}/question/{}'.format(self._BASE_URL, qid))
                self.addLikertScaleButtons(page, yPos, json.loads(q.text)['choices'], qid)

            yPos += yIncrementor
            if yPos >= yIncrementor * questionsPerPage:
                yPos = 0.0

        self.currentPage = 0
        self.pagesList[self.currentPage].show()

    def addPage(self, width, height):
        page = DirectFrame(
            frameSize=(-width, width, -height, height),
            pos=(0, 1, 0),
            sortOrder=10
            )

        setattr(page, 'multipleChoicesAdded', False)
        page.hide()
        self.pagesList.append(page)

        buttonText = 'Next'
        index = self.pagesList.index(page)
        if index+1 == self.amountOfPages:
            buttonText = 'Done'

        button = DirectButton(
           parent=page,
           pos=(width-.1, 0, -(height-.1)),
           scale=0.05,
           pad=(.2, .2, .2, .2),
           text=buttonText,
           pressEffect=1,
           command=self.onQuestionsDone
           )

        return page

    def addPageTitle(self, page, title, infoText):
        DirectLabel(
            parent=page,
            text=title,
            scale=0.09,
            pos=(0, 0, .9))

        DirectLabel(
            parent=page,
            text=infoText,
            scale=.06,
            pos=(0, 0, .75),
            text_wordwrap=30)

    def addQuestion(self, page, questionText, yPos):
        yStart = .6
        OnscreenText(
            parent=page,
            text=questionText,
            scale=.05,
            wordwrap=35,
            pos=(-.8, yStart-yPos),
            align=TextNode.ALeft)

    def addInfoText(self, page, infoText, yPos):
        #print 'add info text:', infoText
        yStart = 0.55
        OnscreenText( # might want to apply slanted or italics to this one
            parent=page,
            text=infoText,
            scale=.04,
            wordwrap=30,
            pos=(-.8, yStart-yPos),
            align=TextNode.ALeft)

        return infoText

    def addTextInputField(self, page, yPos, infoText, question_id, short=True):
        numLines = 1 if short == True else 3
        if infoText != '':
            yStart = .43
        else:
            yStart=.5

        inputField = DirectEntry(
            parent=page,
            text='',
            scale=.05,
            command=None,
            pos=(-.8, 0, yStart-yPos),
            initialText='',
            frameColor=(0.9, 0.9, 0.9, 1),
            width=27,
            numLines=numLines
            #focus=1
            )
        setattr(inputField, 'question_id', question_id)
        self.answersList.append(inputField)

    def addLikertScaleButtons(self, page, yPos, choices, question_id):
        buttons = []
        page.multipleChoicesAdded = True

        for i,item in enumerate(choices):
            xStart = .8
            yStart = .5

            buttonYModifier = 0.05

            spacePerElement = .27
            if len(choices) == 2:
                spacePerElement = .4
                xStart = .75
            else:
                yStart = .45
                buttonYModifier = .1
            
            xPos = (i * spacePerElement) - xStart

            OnscreenText(
                parent=page,
                text=item['choice_text'],
                scale=0.04,
                pos=(xPos, yStart-yPos),
                wordwrap=7
                )

            buttonVariable = self.firstButtonValue if len(self.buttonsList) == 0 else self.secondButtonValue

            buttonYPos = yStart - yPos - buttonYModifier
            button = DirectRadioButton(
                parent=page,
                pos=(xPos+.02, 0, buttonYPos),
                variable=buttonVariable,
                value=[item['sort_nr']],
                scale=0.04,
                frameColor=(1, 1, 1, 0),
                indicatorValue=0
                )
            buttons.append(button)

        self.buttonsList.append((buttons[0], question_id, buttonVariable))

        for button in buttons:
            button.setOthers(buttons)

    def showNotFinishedText(self, page):
        if self.notFinishedText == None:
            self.notFinishedText = OnscreenText(
                parent=page,
                text='Please answer all questions before progressing',
                pos=(0, -.9),
                fg=(1, 0, 0, 1)
                )

    def onQuestionsDone(self):
        bContinue = False
        allAnswered = True

        currentPageFrame = self.pagesList[self.currentPage]
        for answer in self.answersList:
            if answer.get() == '' and answer.getParent() == currentPageFrame:
                allAnswered = False

        if currentPageFrame.multipleChoicesAdded:
            if self.firstButtonValue is None:
                # print 'firstButtonValue is none'
                allAnswered = False
            if len(self.buttonsList) > 1 and self.secondButtonValue is None:
                # print 'secondButtonValue is none'
                allAnswered = False

        if allAnswered == False:
            self.showNotFinishedText(currentPageFrame)
        else:
            base.enableAllAudio()

            for answer in self.answersList:
                if answer.getParent() == currentPageFrame:
                    self.answersDict[answer.question_id] = answer.get()

            if currentPageFrame.multipleChoicesAdded:
                for button,id,value in self.buttonsList:
                    if value[0] is not None:
                        self.answersDict[id] = value[0]

                if self._statesRef.state == self._statesRef.DURING:
                    lastPage = self.pagesList[-1]
                    if currentPageFrame == lastPage:
                        if self.answersDict[13] == 1:
                            bContinue = True

            for id,answer in self.answersDict.iteritems():
                self.save_answer(id, answer)

            self.answersDict = {}

            if self.currentPage < (self.amountOfPages-1): # Clicked 'Next'
                currentPageFrame.hide()
                self.currentPage += 1
                self.pagesList[self.currentPage].show()
            else: # Click 'Done'
                for page in self.pagesList:
                    page.destroy()

                # Handle state changing
                states = self._statesRef
                if states.state == states.BEFORE:
                    states.request(states.PLAY)
                elif states.state == states.DURING:
                    self.timesAnswered += 1
                    if bContinue:
                        states.request(states.PLAY)
                    else:
                        states.request(states.AFTER)
                        self.initializeOverlayFrame()
                elif states.state == states.AFTER:
                    print 'End game'
                    elapsedSeconds = globalClock.getFrameTime()
                    self.save_time(elapsedSeconds)
                    self._mainRef.endGame()

