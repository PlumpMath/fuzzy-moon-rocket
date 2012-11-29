import utils

class ScenarioHandler():

    BASELINE_SCENARIO = 0
    DDA_SCENARIO = 1

    currentScenario = -1

    def __init__(self):
        print 'ScenarioHandler instantiated'

        if utils.getD100() < 50:
            self.currentScenario = self.BASELINE_SCENARIO
            print 'This game is baseline'
        else:
            self.currentScenario = self.DDA_SCENARIO
            print 'This game has DDA'

    def getHasDDA(self):
        if self.currentScenario == self.DDA_SCENARIO:
            return True
        else:
            return False