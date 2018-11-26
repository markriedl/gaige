import random
import copy
import sys
import numbers
from Observation import *
from Reward import *
from Action import *


class Environment:

	# Survivors have unique IDs.
	smallestSurvivorID = 6 # Cannot be smaller than 5
	largestSurvivorID = 9 # Cannot be larger than 9


	# The grid world
	# 1 = walls
	# 2 = radiation
	# 4 = goal (non-terminal)
	# 5 = goal (terminal)
	# 6-9 = people to rescue
	map = [[1, 1, 1, 1, 1, 1, 1],
		   [1, 0, 2, 6, 1, 7, 1],
		   [1, 0, 2, 0, 2, 0, 1],
		   [1, 0, 0, 4, 2, 0, 1],
		   [1, 1, 1, 1, 1, 1, 1]]
	# Note: the extremities of the map should be '1's.
	# Width and height should match the actual dimensions of the grid above
	width = 7
	height = 5
	
	# Which direction should the enemy walk?
	# 0 = up
	# 1 = down
	# 2 = left
	# 3 = right
	influenceMap = [[3, 1, 1, 1, 1, 1, 2],
					[3, 1, 2, 2, 2,	1, 2],
					[3, 1, 0, 0, 2, 2, 2],
					[3, 3, 3, 0, 2, 2, 2],
					[3, 0, 0, 0, 0, 0, 2]]
  
	# The current state
	currentState = []

	# The previous state
	previousState = []
	
	# Hard-coded initial state (used unless randomStart = True)
	# 0: bot x
	# 1: bot y
	# 2: enemy alive?
	# 3: enemy x
	# 4: enemy y
	# 5: enemy torture mode?
	# 6-9: person rescue state (if any)
	startState = [1, 1, True, 3, 1, False, False, False]
	
	# Amount of reward at the goal
	reward = 10.0
	
	# Amount of reward for each rescue
	rescue = 20.0
	
	# Amount of penalty
	penalty = -1.0
	
	# Amount of penalty from touching the enemy
	pain = -50.0
	
	# amount of penalty from touching radiation
	radiation = -20.0
	
	# Amount of penalty from dead enemy
	enemyDead = -10.0
	
	# Incremented every step
	counter = 0
	
	# enemy move timer
	moveTimer = 1
	
	# how should the enemy move?
	# 0: doesn't move
	# 1: uses influence map
	# 2: moves randomly
	# 3: chases the bot
	# 4: gets input from external source
	enemyMode = 1
	
	# if enemyMode = 4
	nextEnemyMove = None
	
	# Randomly generate a start state
	randomStart = False
	
	randGenerator=random.Random()
	lastActionValue = -1

	# Print debuggin information
	verbose = False

	# 0 = up
	# 1 = down
	# 2 = left
	# 3 = right
	# 4 = smash
	def validActions(self):
		resultArray = [0, 1, 2, 3, 4]
		return resultArray
	
	# Get the name of the action
	def actionToString(self, act):
		if act == 0:
			return "GoUp"
		elif act == 1:
			return "GoDown"
		elif act == 2:
			return "GoLeft"
		elif act == 3:
			return "GoRight"
		elif act == 4:
			return "Smash"
		return str(act)


	# Called to start the simulation
	def env_start(self):
		# Use hard-coded start state or randomly generated state?
		if self.randomStart:
			self.currentState = self.randomizeStart(self.map)
		else:
			self.currentState = self.startState[:]

		# Make sure counter is reset
		self.counter = 0

		if self.isVerbose():
			print "env_start", self.currentState

		# Reset previous state
		self.previousState = []

		# Get the first observation
		returnObs=Observation()
		returnObs.worldState=self.currentState[:]
		returnObs.availableActions = self.validActions()
		return returnObs

	# This creates a random initial state
	# Agent and enemy will not be placed on a wall
	def randomizeStart(self, map):
		bot = []
		enemy = []
		while True:
			bot = [random.randint(1,self.width-2), random.randint(1,self.height-2)]
			if map[bot[1]][bot[0]] != 1:
				break
		while True:
			enemy = [random.randint(1,self.width-2), random.randint(1,self.height-2)]
			if map[enemy[1]][enemy[0]] != 1:
				break
		state = bot + [True] + enemy + [False]
		for x in map:
			for xy in x:
				if xy >= self.smallestSurvivorID and xy <= self.largestSurvivorID:
					state.append(False)
		return state

	# Update world state based on agent's action
	# Enemy is part of the world and autonomous from the agent
	def env_step(self,thisAction):
		# Store previous state
		self.previousState = self.currentState[:]
		# Execute the action
		self.executeAction(thisAction.actionValue)
				
		# increment counter
		self.counter = self.counter + 1
		
		# Enemy movement
		if self.currentState[2]:
			if self.currentState[0] == self.currentState[3] and self.currentState[1] == self.currentState[4]:
				self.currentState[5] = True
			else:
				self.currentState[5] = False
			if self.counter % self.moveTimer == 0:
				# Which direction to move?
				move = None
				if self.enemyMode == 1:
					move = self.influenceMap[self.currentState[4]][self.currentState[3]]
				elif self.enemyMode == 2:
					move = random.randint(0, 3)
				elif self.enemyMode == 3:
					move = self.chaseDirection((self.currentState[3], self.currentState[4]), (self.currentState[0], self.currentState[1]))
				elif self.enemyMode == 4 and self.nextEnemyMove is not None:
					move = self.nextEnemyMove
				if self.isVerbose():
					print "enemy action:", self.actionToString(move)
				if move is not None:
					# newpos will be the new grid cell the enemy moves into
					newpos = [self.currentState[3], self.currentState[4]]
					if move == 0:
						newpos[1] = newpos[1] - 1
					elif move == 1:
						newpos[1] = newpos[1] + 1
					elif move == 2:
						newpos[0] = newpos[0] - 1
					elif move == 3:
						newpos[0] = newpos[0] + 1
					
					# Make sure it can't move into a wall
					if self.map[newpos[1]][newpos[0]] == 1:
						newpos[0] = self.currentState[3]
						newpos[1] = self.currentState[4]


					# update state
					self.currentState[3] = newpos[0]
					self.currentState[4] = newpos[1]
	
		# Rescuing
		# People can be given numbers 5-9 and their rescue state is in positions 5-9 of the bot's state
		for i in range(min(len(self.startState), self.largestSurvivorID) - self.smallestSurvivorID):
			survivor = i + self.smallestSurvivorID
			if not self.currentState[survivor] and self.map[self.currentState[1]][self.currentState[0]] == survivor:
				self.currentState[survivor] = True

		if self.isVerbose():
			print "state:", self.currentState
			if isinstance(self.verbose, numbers.Number) and self.verbose >= 2:
				self.printEnvironment()

		# Make a new observation
		lastActionValue = thisAction.actionValue
		theObs=Observation()
		theObs.worldState=self.currentState[:]
		theObs.availableActions = self.validActions()
		theObs.isTerminal = self.checkTerminal()

		# Calculate the reward
		rewardValue = self.calculateReward(lastActionValue)
		reward = Reward(rewardValue)

		return theObs, reward

        
	# reset the environment
	def env_reset(self):
		# use random start or hard-coded start state?
		if self.randomStart:
			self.currentState = self.randomizeStart(self.map)
		else:
			self.currentState = self.startState[:]
		
		# reset the counter
		self.counter = 0


	# Is agent in a terminal state?
	def checkTerminal(self):
		if self.map[self.currentState[1]][self.currentState[0]] == 5:
			return True
		else:
			return False

	# Agent executes an action, update the state
	def executeAction(self, theAction):
		newpos = [self.currentState[0], self.currentState[1]]
		if (theAction == 0):#Move Up
			if self.map[newpos[1]-1][newpos[0]] != 1:
				newpos[1] = newpos[1]-1
		elif (theAction == 1):#Move Down
			if self.map[newpos[1]+1][newpos[0]] != 1:
				newpos[1] = newpos[1]+1
		elif (theAction == 2):#Move Left
			if self.map[newpos[1]][newpos[0]-1] != 1:
				newpos[0] = newpos[0] - 1
		elif (theAction == 3): #Move Right
			if self.map[newpos[1]][newpos[0]+1] != 1:
				newpos[0] = newpos[0] + 1
		elif (theAction == 4): #smash
			if self.currentState[0] == self.currentState[3] and self. currentState[1] == self.currentState[4]:
				# Smashing the enemy
				self.currentState[2] = False
		self.currentState[0] = newpos[0]
		self.currentState[1] = newpos[1]
		

	# What reward should the agent get?
	def calculateReward(self, theAction):
		r = 0
		if self.currentState[2] and self.currentState[5]:
			# enemy is alive and co-located with the bot for more than one turn
			r = r + self.pain
		elif not self.currentState[2]:
			# enemy is dead
			r = r + self.enemyDead
		
		# Survivors can be given numbers 6-9 and their rescue state is in positions 6-9 of the bot's state
		for i in range(min(self.largestSurvivorID, len(self.currentState)) - self.smallestSurvivorID):
			survivor = i + self.smallestSurvivorID
			if self.currentState[survivor]:
				r = r + self.rescue

		
		if self.map[self.currentState[1]][self.currentState[0]] == 5:
			r = r + self.reward
		elif self.map[self.currentState[1]][self.currentState[0]] == 4:
			r = r + self.reward
		elif self.map[self.currentState[1]][self.currentState[0]] == 2:
			r = r + self.radiation
		else:
			r = r + self.penalty
		return r

	### print the map
	### key:
	# 1 = walls
	# 2 = radiation
	# 4 = goal (non-terminal)
	# 5 = goal (terminal)
	# 6-9 = people to rescue
	# A = agent
	# E = enemy
	# O = agent and enemy are co-located
	# Q = agent and enemy are co-located and enemy torturing agent
	# X = enemy is dead
	def printEnvironment(self):
		for j in range(self.height):
			p = ""
			for i in range(self.width):
				q = ""
				if self.currentState[0] == i and self.currentState[1] == j and self.currentState[3] == i and self.currentState[4] == j and self.currentState[2]:
					# Both co-located and enemy alive
					if not self.currentState[5]:
						# enemy not in torture mode
						q = "O"
					else:
						# enemy in torture mode
						q = "Q"
				elif self.currentState[0] == i and self.currentState[1] == j:
					# not co-located, bot here
					q = "A"
				elif self.currentState[3] == i and self.currentState[4] == j:
					# not co-located, enemy here
					if self.currentState[2]:
						q = "E"
					else:
						q = "X"
				else:
					q = str(self.map[j][i])
					num = self.map[j][i]
					if num > 5 and len(self.currentState) >= num+1 and self.currentState[num]:
						# There is a human here, but that person has been saved
						q = '0'
				p = p + q + " "
			print p

	def isVerbose(self):
		if isinstance(self.verbose, numbers.Number) and self.verbose == 0:
			return False
		return self.verbose

	def chaseDirection(self, myPos, targetPos):
		if targetPos[0] > myPos[0]:
			return 3 # go right
		elif targetPos[0] < myPos[0]:
			return 2 # go left
		elif targetPos[1] < myPos[1]:
			return 0 # go up
		else:
			return 1 # go down

##########################################

if __name__=="__main__":
	EnvironmentLoader.loadEnvironment(environment())