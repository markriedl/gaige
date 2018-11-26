import random
import sys
import copy
import operator
from Observation import *
from Reward import *
from Action import *
from Environment import *
from random import Random





class Agent:
	# Random generator
	randGenerator=Random()

	# Remember last action
	lastAction=Action()

	# Remember last observation (state)
	lastObservation=Observation()
	
	# Q-learning stuff: Step size, epsilon, gamma, learning rate
	epsilon = 0.5
	gamma = 0.9
	learningRate = 0.5

	# Value table
	v_table = None

	# The environment
	gridEnvironment = None
	
	#Initial observation
	initialObs = None
	
	#Current observation
	currentObs = None
	
	# The training or testing episdoe will run for no more than this many time steps
	numSteps = 500
	
	# Total reward
	totalReward = 0.0
	
	# Print debugging statements
	verbose = True
	
	# Number of actions in the environment
	numActions = 5

	# Constructor, takes a reference to an Environment
	def __init__(self, env):

		# Initialize value table
		self.v_table={}
		
		# Set dummy action and observation
		self.lastAction=Action()
		self.lastObservation=Observation()
		
		# Set the environment
		self.gridEnvironment = env
		
		# Get first observation and start the environment
		self.initialObs = self.gridEnvironment.env_start()
		self.initializeVtableStateEntry(self.initialObs.worldState)
	
	# Make an empty row in the v table with the state as key.
	def initializeVtableStateEntry(self, state):
		if self.calculateFlatState(state) not in self.v_table.keys():
			self.v_table[self.calculateFlatState(state)] = self.numActions*[0.0]
        
	# Once learning is done, use this to run the agent
	# observation is the initial observation
	def executePolicy(self, observation):
		# History stores up list of actions executed
		history = []
		# Start the counter
		count = 0
		# reset total reward
		self.totalReward = 0.0
		# Copy the initial observation
		self.workingObservation = self.copyObservation(observation)
		
		# Make sure the value table has the starting observation
		self.initializeVtableStateEntry(self.workingObservation.worldState)

		if self.isVerbose():
			print("START")
		
		# While a terminal state has not been hit and the counter hasn't expired, take the best action for the current state
		while not self.workingObservation.isTerminal and count < self.numSteps:
			newAction = Action()
			# Get the best action for this state
			newAction.actionValue = self.greedy(self.workingObservation)
			history.append((newAction.actionValue, self.workingObservation.worldState))

			if self.isVerbose():
				print "state:", self.workingObservation.worldState
				print "bot action:", self.gridEnvironment.actionToString(newAction.actionValue)

			# execute the step and get a new observation and reward
			currentObs, reward = self.gridEnvironment.env_step(newAction)
			if self.isVerbose():
				print "reward:", reward.rewardValue

			
			self.totalReward = self.totalReward + reward.rewardValue
			self.workingObservation = copy.deepcopy(currentObs)

			# increment counter
			count = count + 1
        
		if self.isVerbose():
			print("END")
		return history
	

	# Q-learning implementation
	# observation is the initial observation
	def qLearn(self, observation):
		# copy the initial observation
		self.workingObservation = self.copyObservation(observation)
		
		# start the counter
		count = 0

		lastAction = -1
		
		# reset total reward
		self.totalReward = 0.0
		
		# while terminal state not reached and counter hasn't expired, use epsilon-greedy search
		while not self.workingObservation.isTerminal and count < self.numSteps:
			
			# Make sure table is populated correctly
			self.initializeVtableStateEntry(self.workingObservation.worldState)

			# Take the epsilon-greedy action
			newAction = Action()
			newAction.actionValue = self.egreedy(self.workingObservation)
			lastAction = newAction.actionValue

			# Get the new state and reward from the environment
			currentObs, reward = self.gridEnvironment.env_step(newAction)
			rewardValue = reward.rewardValue
			
			# Make sure table is populated correctly
			self.initializeVtableStateEntry(currentObs.worldState)

			# update the value table
			lastFlatState = self.calculateFlatState(self.workingObservation.worldState)
			newFlatState = self.calculateFlatState(currentObs.worldState)
			self.updateVtable(newFlatState, lastFlatState, newAction.actionValue, rewardValue, currentObs.isTerminal, currentObs.availableActions)
			
			# increment counter
			count = count + 1
			self.workingObservation = self.copyObservation(currentObs)
		
			# increment total reward
			self.totalReward = self.totalReward + reward.rewardValue


		# Done learning, reset environment
		self.gridEnvironment.env_reset()


	### Update the v_table during Q-learning.
	### newState: the new state reached after performing newAction in lastState.
	### lastState: the prior state
	### action: the action just performed
	### reward: the amount of reward received upon transitioning to newState with newAction
	### terminal: boolean: is the newState a terminal state?
	### availableActions: a list of actions that can be performed in newState.
	###
	### Update Q(s, a) in v_table for lastState and the performed action.
	def updateVtable(self, newState, lastState, action, reward, terminal, availableActions):
		# YOUR CODE GOES BELOW HERE

		# YOUR CODE GOES ABOVE HERE
		return None


	### Return the best action according to the policy, or a random action epsilon percent of the time.
	### observation: the current observation (state)
	###
	### If a random number between [0, 1] is less than epsilon, pick a random action from available actions.
	### Otherwise: pick the action for the current state that has the highest Q value.
	### Return the index of the action picked.
	def egreedy(self, observation):
		# YOUR CODE GOES BELOW HERE

		# YOUR CODE GOES ABOVE HERE
		return 0


	### Return the best action according to the policy
	### observation: the current observation (state)
	###
	### Pick the action for the current state that has the highest Q value.
	### Return the index of the action picked.
	def greedy(self, observation):
		self.initializeVtableStateEntry(observation.worldState)
		# YOUR CODE GOES BELOW HERE

		# YOUR CODE GOES ABOVE HERE
		return 0
	

	# Reset the agent
	def agent_reset(self):
		self.lastAction = Action()
		self.lastObservation = Observation()
		self.initialObs = self.gridEnvironment.env_start()

	# Create a copy of the observation
	def copyObservation(self, obs):
		returnObs =  Observation()
		if obs.worldState != None:
			returnObs.worldState = obs.worldState[:]
            
		if obs.availableActions != None:
			returnObs.availableActions = obs.availableActions[:]
        
		if obs.isTerminal != None:
			returnObs.isTerminal = obs.isTerminal
            
		return returnObs
	
	# Turn the state into a tuple for bookkeeping
	def calculateFlatState(self, theState):
		return tuple(theState)

	def isVerbose(self):
		if isinstance(self.verbose, numbers.Number) and self.verbose == 0:
			return False
		return self.verbose
