
class DDA():

    enemySpeedFactor = 1.0

    def __init__(self, enemyListRef, playerRef):
        print("DDA class instantiated")

        self._playerRef = playerRef
        self._enemyListRef = enemyListRef