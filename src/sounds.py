
class SoundsHandler():

    def __init__(self):
        print 'SoundsHandler instantiated'

        self.loadAllSounds()

        self.startAmbientMusic()
        self.startBackgroundMusic()

    def loadAllSounds(self):
        soundsPath = 'sounds/'
        self.ambientMusic = loader.loadSfx(soundsPath+'Ambient_Music_edited.mp3')
        self.bgMusic = loader.loadSfx(soundsPath+'background_music_mixtrack.mp3')
        
        self.diggerAttack = loader.loadSfx(soundsPath+'Digger_attack.mp3')
        self.diggerDeath = loader.loadSfx(soundsPath+'Digger_death.mp3')
        self.diggerIdle = loader.loadSfx(soundsPath+'Digger_idle.mp3')
        self.probeDeath = loader.loadSfx(soundsPath+'Probe_death.mp3')

        self.playerAttack = loader.loadSfx(soundsPath+'Player_attack_hit.wav')
        self.playerAttackMiss = loader.loadSfx(soundsPath+'Player_attack_miss.mp3')
        self.playerWalk = loader.loadSfx(soundsPath+'Walk_sound.wav')
        self.playerDeath = loader.loadSfx(soundsPath+'WilhelmScream_Player_Death.ogg')
        self.areaExit = loader.loadSfx(soundsPath+'Area_exit_sound.mp3')

    def startAmbientMusic(self):
        self.ambientMusic.setLoop(True)
        self.ambientMusic.play()

    def startBackgroundMusic(self):
        self.bgMusic.setLoop(True)
        self.bgMusic.play()

#-------------------- ENEMY SOUNDS --------------------#
    def playDiggerAttack(self):
        self.diggerAttack.play()

    def playDiggerIdle(self):
        self.diggerIdle.play()

    def playDiggerDeath(self):
        self.diggerDeath.play()

    def playProbeDeath(self):
        self.probeDeath.play()

#------------------------PLAYER SOUNDS-----------------#
    def playPlayerAttackHit(self):
        self.playerAttack.play()

    def playPlayerAttackMiss(self):
        self.playerAttackMiss.play()

    def playPlayerWalk(self):
        self.playerWalk.play()

    def stopPlayerWalk(self):
        self.playerWalk.stop()

    def playPlayerDeath(self):
        self.playerDeath.play()

    def playAreaExit(self):
        self.areaExit.play()