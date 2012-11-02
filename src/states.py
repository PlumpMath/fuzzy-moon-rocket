from panda3d.core import *
from direct.fsm.FSM import FSM


class StateHandler(FSM):

    BEFORE = 'Before'
    PLAY ='Play'
    PAUSE ='Pause'
    DURING ='During'
    AFTER ='After'

    def __init__(self):
        FSM.__init__(self, 'StateHandler')

        self.defaultTransitions = {
            'Before': ['Play', 'Pause'],
            'Play':['Pause', 'During'],
            'Pause':['Play'],
            'During':['Play', 'Pause','After'],
            'After':[],
        }

        self.request(self.BEFORE)

    def enterBefore(self):
        print('State: enterBefore')

    def exitBefore(self):
        print('State: exitBefore')

    def enterPlay(self):
        print('State: enterPlay')

    def exitPlay(self):
        print('State: exitPlay')

    def enterPause(self):
        print('State: enterPause')

    def exitPause(self):
        print('State: exitPause')

    def enterDuring(self):
        print('State: enterDuring')

    def exitDuring(self):
        print('State: exitDuring')

    def enterAfter(self):
        print('State: enterAfter')

    def exitAfter(self):
        print('State: exitAfter')