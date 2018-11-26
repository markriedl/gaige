import random
import sys
import copy
import operator
from Observation import *
from Reward import *
from Action import *
from Environment import *
from Agent import *
from random import Random

# Make an agent
gridEnvironment = Environment()
gridAgent = Agent(gridEnvironment)

# How many states to make?
numStates = 10

states = []

# Make some states
for i in range(numStates):
	# Make a state
	state = [random.randint(1,gridEnvironment.width-1), random.randint(1,gridEnvironment.height-1), True, random.randint(1,gridEnvironment.width-1), random.randint(1,gridEnvironment.height-1), False, False, False]
	states.append(state)
	# Create an entry in v_table for state
	entry = []
	for j in range(gridAgent.numActions):
		entry.append((random.random()-0.5)*100.0)
	gridAgent.v_table[gridAgent.calculateFlatState(state)] = entry
print "v table:"
print gridAgent.v_table

# Call greedy() k times
for k in range(numStates):
	observation = Observation()
	observation.worldState = states[k]
	observation.availableActions = gridEnvironment.validActions()
	action = gridAgent.greedy(observation)
	print "Action selected for:", states[k], "is:", action