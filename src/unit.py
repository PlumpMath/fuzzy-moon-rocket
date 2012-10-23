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
	_currentHealthPoints = 0
	_prevEXP = 0
	_isDead = False

	def __init__(self):
		print("Unit class instantiated")
		self.initAttributes()
		self.initlevel()

	def initAttributes(self):
		self.strength = 1 # Start attributes arbitrarily at 1
		self.constitution = 1
		self.dexterity = 1

		# Initialize movement speed value
		self.movementSpeed = 0.5 # Not affected by attributes

		self.updateMaxHealthPoints() # initialize the hit points
		self._currentHealthPoints = self.maxHealthPoints # Start currentHealthPoints at Max HP

	def initlevel(self):
		self.level = 1
		self.experience = 0
		self._prevEXP = 0

	def getStrengthModifier(self):
		return (self.strength - 10) / 2

	def getConstitutionModifier(self):
		return (self.constitution - 10) / 2

	def getDexterityModifier(self):
		return (self.dexterity - 10) / 2

	def giveEXP(self, value):
		self.experience += value
		if self.experience > self._prevEXP + (self.level * 1000):
			self.increaseLevel()

	def increaseStrength(self):
		self.strength += 1	

	def increaseLevel(self):
		self._prevEXP += (self.level * 1000) # increment prevExp
		self.level += 1 # increment level
		self.updateHealthPoints() # Make sure the player's health is updated

		if (self.level - 1) % 4 == 0: # Every 4th level (starting at level 4) increase attribute
			self.increaseStrength()

	def updateMaxHealthPoints(self):
		self.fighterBaseHealthPoints = 15
		self.fighterHealthPointsPerLevel = 8
		self.maxHealthPoints = self.fighterBaseHealthPoints + (self.level * (self.fighterHealthPointsPerLevel + self.getConstitutionModifier()))

	def receiveDamage(self, damageAmount):
		self._currentHealthPoints = self._currentHealthPoints- damageAmount
		if self._currentHealthPoints <= 0:
			print("Unit died!")
			self._isDead = True

	def heal(self, healAmount):
		if self._isDead == False:
			self._currentHealthPoints += healAmount
			if self._currentHealthPoints > self.maxHealthPoints:
				self._currentHealthPoints = self.maxHealthPoints

	def getInitiativeRoll(self):
		return (self.level / 2) + self.getDexterityModifier() + getD20()

	def getAttackBonus(self):
		return (self.level / 2) + self.getStrengthModifier() + getD20()

	def getDamageBonus(self):
		return self.getStrengthModifier() + getD8()

	def getArmorClass(self):
		self.baseArmorClass = 10
		return self.baseArmorClass + (self.level / 2) + self.getDexterityModifier()

	def getCurrentHealthPoints(self):
		return self._currentHealthPoints

	def getCurrentHealthPointsAsPercentage(self):
		return (self._currentHealthPoints / self.maxHealthPoints) * 100