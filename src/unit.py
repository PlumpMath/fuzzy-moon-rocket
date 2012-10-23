class Unit(object):
	# Declare class variables
	strength = 0
	constitution = 0
	dexterity = 0
	damage = 0
	attackBonus = 0
	maxHealthPoints = 0
	armorClass = 0
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

		self.damage = 0 # affected by strength
		self.attackBonus = 0 # Affected by strength
		self.maxHealthPoints = 0 # affected by constitution
		self.armorClass = 0 # affected by dexterity

		self.movementSpeed = 0.5 # Not affected by attributes

		self._currentHealthPoints = self.maxHealthPoints
		self._damageModifier = 1 # Added to damage to calculate total damage

		self.updateHealthPoints() # initialize the hit points

	def initlevel(self):
		self.level = 1
		self.experience = 0
		self.prevEXP = 0

	def getCurrentdamage(self):
		return self.damage + self._damageModifier

	def increaseStrength(self):
		self.strength += 1

	def getCurrentdamageModifier(self):
		self._damageModifier = 1 + (self.strength - 10) / 2
		return self._damageModifier

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
			
	def updateHealthPoints(self):
		self.maxHealthPoints = (self.level * (10 + ((self.constitution - 10) / 2)))
