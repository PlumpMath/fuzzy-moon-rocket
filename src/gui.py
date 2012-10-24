import time


class GUI:

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