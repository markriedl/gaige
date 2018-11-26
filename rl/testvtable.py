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
gridAgent.agent_reset()

# A sequence of actions to take
actions = [1, 3, 3, 0, 1]

# The last state
workingObservation = gridAgent.copyObservation(gridAgent.initialObs)
# Make sure there is an entry for the last state in the v table
gridAgent.initializeVtableStateEntry(workingObservation.worldState)

# Report the initial v table
print "Initial V Table:"
print gridAgent.v_table
print "---"

# Execute the sequence of actions
for a in actions:
	# Make a new action
	newAction = Action()
	newAction.actionValue = a
	# Execute the action
	currentObs, reward = gridEnvironment.env_step(newAction)
	# Make sure there is an entry in the v table for the new state
	gridAgent.initializeVtableStateEntry(currentObs.worldState)
	# Put things in the right form
	lastFlatState = gridAgent.calculateFlatState(workingObservation.worldState)
	newFlatState = gridAgent.calculateFlatState(currentObs.worldState)
	# Update the v table
	gridAgent.updateVtable(newFlatState, lastFlatState, newAction.actionValue, reward.rewardValue, currentObs.isTerminal, currentObs.availableActions)
	# Report
	print "v table after:"
	print "   old state:", workingObservation.worldState
	print "   action:", newAction.actionValue
	print "   new state:", currentObs.worldState
	print gridAgent.v_table
	print "---"
	# Update the last state
	workingObservation = gridAgent.copyObservation(currentObs)
