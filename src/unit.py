import utils

class Unit(object):
    # Declare class variables
    strength = 0
    constitution = 0
    dexterity = 0

    maxHealthPoints = 0
    
    movementSpeed = 0

    level = 0
    experience = 0

    # Declare private variables
    _prevEXP = 0
    _isDead = False

    def __init__(self):
        #print("Unit class instantiated")
        self.initUnitAttributes()
        self.initLevel()

    def initUnitAttributes(self):
        self.initiativeBonus = 0

        self.attackBonus = 0
        self.damageBonus = 0
        self.damageRange = 0
        self.fixedHealthPoints = 0
        self.armorClass = 0

        # Initialize currentHealthPoints at Max HP
        self.initHealth()

        # Regenerate once per second
        self.regenTask = taskMgr.doMethodLater(2.0, self.passiveRegeneration, 'passiveRegenerationTask')

    def initLevel(self):
        self.level = 1
        self.experience = 0
        self._prevEXP = 0

    def getStrengthModifier(self):
        return (self.strength - 10) / 2

    def getConstitutionModifier(self):
        return (self.constitution - 10) / 2

    def getDexterityModifier(self):
        return (self.dexterity - 10) / 2
 
    def increaseStrength(self):
        self.strength += 1  

    def increaseLevel(self):
        self._prevEXP += (self.level * 1000) # increment prevExp
        self.level += 1 # increment level
        
        # Make sure the player's health is updated
        self.updateMaxHealthPoints() 

        # Every 4th level (starting at level 4) increase attribute
        if (self.level - 1) % 4 == 0: 
            self.increaseStrength()

    def initHealth(self):
        self.updateMaxHealthPoints()
        self.currentHealthPoints = self.maxHealthPoints

    def updateMaxHealthPoints(self):
        if self.fixedHealthPoints == 0:
            self.fighterHealthPointsPerLevel = 8
            self.maxHealthPoints =  (self.level * 
                                    (self.fighterHealthPointsPerLevel + self.getConstitutionModifier()))
        else:
            self.maxHealthPoints = self.fixedHealthPoints

    def receiveDamage(self, damageAmount):
        self.currentHealthPoints -= damageAmount
        if self.currentHealthPoints <= 0:
            #print("Unit died!")
            self._isDead = True

    def heal(self, healAmount):
        if not self.getIsDead():
            tempHp = self.currentHealthPoints - self.maxHealthPoints

            self.currentHealthPoints += healAmount
            if self.currentHealthPoints > self.maxHealthPoints:
                self.currentHealthPoints = self.maxHealthPoints

            if tempHp > 0:
                self.currentHealthPoints += tempHp

    def fullHeal(self):
        self.currentHealthPoints = self.maxHealthPoints

    def receiveTemporaryHealth(self, amount):
        if not self.getIsDead():
            self.currentHealthPoints += amount

    def removeTemporaryHealth(self):
        if self.currentHealthPoints > self.maxHealthPoints:
            self.currentHealthPoints = self.maxHealthPoints

    def getIsDead(self):
        if self._isDead or self.currentHealthPoints <= 0:
            return True
        else:
            return False

    def setIsNotDead(self):
        if self.getIsDead():
            self._isDead = False
            if self.currentHealthPoints < 1:
                self.currentHealthPoints = 1

    def getInitiativeRoll(self):
        return self.initiativeBonus + (self.level / 2) + self.getDexterityModifier() #+ utils.getD20()

    def getAttackBonus(self):
        modifier = self.getStrengthModifier() if self.getStrengthModifier() > self.getDexterityModifier() else self.getDexterityModifier()
        return self.attackBonus + (self.level / 2) + modifier + utils.getD20()

    def getDamageBonus(self):
        randomDamage = 0
        if self.damageRange == 4:
            randomDamage = utils.getD4()
        elif self.damageRange == 6:
            randomDamage = utils.getD6()
        elif self.damageRange == 8:
            randomDamage = utils.getD8()
        elif self.damageRange == 10:
            randomDamage = utils.getD10()

        return self.getStrengthModifier() + randomDamage + self.damageBonus

    def getArmorClass(self):
        return self.armorClass + (self.level / 2) + self.getDexterityModifier()

    def getCurrentHealthPointsAsPercentage(self):
        return ((float(self.currentHealthPoints) / 
                    self.maxHealthPoints) * 100.0)

    def attack(self, other):
        if not self.getIsDead() and not other.getIsDead():
            if self.getAttackBonus() >= other.getArmorClass():
                dmg = self.getDamageBonus()
                #print(self.getName(), ' damaged ', other.getName(), ' for ', dmg, ' damage')
                other.receiveDamage(dmg)

                return 2 # Returns 2 when self damages other

            return 1 # Returns 1 when self attacks other

        return 0 # Returns 0 when either self or other is dead

    def passiveRegeneration(self, task):
        if self.getIsDead():
            # Do not regenerate dead objects
            return task.again

        hp = self.maxHealthPoints / 100.0
        if hp >= 0.1:
            self.heal(hp)
            #print 'regenerated ' + str(hp)

        return task.again

    def removePassiveRegeneration(self):
        #self.regenTask.remove()
        taskMgr.remove(self.regenTask)
