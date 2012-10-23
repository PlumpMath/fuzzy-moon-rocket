import utils

class Unit(object):
	# Declare class variables
	strength = 0
	constitution = 0
	dexterity = 0
	
	#damage = 0
	currentHealthPoints = 0
	maxHealthPoints = 0
	#armorClass = 0
	movementSpeed = 0

	level = 0
	experience = 0
	prevEXP = 0

	def __init__(self):
		print("Unit class instantiated")
		self.initAttributes()
		self.initlevel()

	def initAttributes(self):
		self.strength = 0
		self.constitution = 0
		self.dexterity = 0

		self.movementSpeed = 0.5 # Not affected by attributes

		self.updateMaxHealthPoints() # initialize the hit points
		self.currentHealthPoints = self.maxHealthPoints

	def initlevel(self):
		self.level = 1
		self.experience = 0
		self.prevEXP = 0

	def increaseStrength(self):
		self.strength += 1

	def getStrengthModifier(self):
		return (self.strength - 10) / 2

	def getConstitutionModifier(self):
		return (self.constitution - 10) / 2

	def getDexterityModifier(self):
		return (self.dexterity - 10) / 2

	def giveEXP(self, value):
		self.experience += value
		if self.experience > self.prevEXP + (self.level * 1000):
			self.increaseLevel()

	def increaseLevel(self):
		self.prevEXP += (self.level * 1000) # increment prevExp
		self.level += 1 # increment level
		self.updateHealthPoints() # Make sure the player's health is updated

		if self.level % 4 == 0: # Every 4th level increase attribute
			self.increaseStrength()
			
	def updateMaxHealthPoints(self):
		self.fighterBaseHealthPoints = 15
		self.fighterHealthPointsPerLevel = 8
		self.maxHealthPoints = self.fighterBaseHealthPoints + (self.level * (self.fighterHealthPointsPerLevel + self.getConstitutionModifier()))

	def getInitiativeRoll(self):
		return (self.level / 2) + self.getDexterityModifier() + getD20()

	def getAttackBonus(self):
		return (self.level / 2) + self.getStrengthModifier() + getD20()

	def getDamageBonus(self):
		return self.getStrengthModifier() + getD8()

	def getArmorClass(self):
		self.baseArmorClass = 10
		return self.baseArmorClass + (self.level / 2) + self.getDexterityModifier()