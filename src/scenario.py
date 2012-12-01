from gui import GUI
import utils

class ScenarioHandler():

    BASELINE_SCENARIO = 0
    DDA_SCENARIO = 1

    currentScenario = -1

    def __init__(self, mainRef):
        print 'ScenarioHandler instantiated'

        self._guiRef = mainRef.gui

        self.initializeScenario()

    def initializeScenario(self):
        self.currentScenario = self._guiRef.create_user()

        if self.currentScenario == self.BASELINE_SCENARIO:
            print 'This game is baseline'
        else:
            print 'This game has DDA'

    def getHasDDA(self):
        if self.currentScenario == self.DDA_SCENARIO:
            return True
        else:
            return False