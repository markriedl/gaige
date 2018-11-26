import sys
from Observation import *
from Reward import *
from Action import *
from Agent import *
from Environment import *
import numpy


# Training episodes
episodes = 500

# how often to report training results
trainingReportRate = 100

# play the interactive game?
# 0: human does not play
# 1: human plays as the bot
# 2: human plays as the enemy
play = 2

#Max reward received in any iteration
maxr = None

# Set up environment for initial training
gridEnvironment = Environment()
gridEnvironment.randomStart = False
gridEnvironment.enemyMode = 1
gridEnvironment.verbose = 0

# Set up agent
gridAgent = Agent(gridEnvironment)
gridAgent.verbose = False

# This is where learning happens
for i in range(episodes):
	# Train
	gridAgent.agent_reset()
	gridAgent.qLearn(gridAgent.initialObs)
	# Test
	gridAgent.agent_reset()
	gridAgent.executePolicy(gridAgent.initialObs)
	# Report
	totalr = gridAgent.totalReward
	if maxr == None or totalr > maxr:
		maxr = totalr
	
	if i % trainingReportRate == 0:
		print "iteration:", i, "total reward", totalr, "max reward:", maxr


# Reset the environment for policy execution
gridEnvironment.verbose = 1
gridEnvironment.randomStart = False
gridEnvironment.enemyMode = 1
gridAgent.verbose = True

print "Execute Policy"
gridAgent.agent_reset()
gridAgent.executePolicy(gridAgent.initialObs)
print "total reward", gridAgent.totalReward

### HOW TO PLAY
### w: up
### s: down
### a: left
### d: right
### q: smash (if playing as the bot)
### reset: start the game over
### quit: end game

if play == 1:
	# Play as the bot
	print "PLAY!"
	gridAgent.agent_reset()
	gridAgent.verbose = 0
	gridEnvironment.enemyMode = 1 # change this if you want
	gridEnvironment.verbose = 0
	totalr = 0.0
	while(True):
		# print the map
		gridEnvironment.printEnvironment()
		print "total player reward:", totalr
		
		# Player move
		print "Move?"
		move = None
		x = sys.stdin.readline()
		if x.strip() == "reset":
			# reset the game state
			gridAgent.agent_reset()
			totalr = 0.0
			print "PLAY!"
			continue # I feel so bad about this
		elif x.strip() == "quit":
			# quit game
			break
		elif x[0] == '0' or x[0] == 'w':
			#up
			move = 0
		elif x[0] == '1' or x[0] == 's':
			#down
			move = 1
		elif x[0] == '2' or x[0] == 'a':
			#left
			move = 2
		elif x[0] == '3' or x[0] == 'd':
			#right
			move = 3
		elif x[0] == '4' or x[0] == 'q':
			#smash
			move = 4
		act = Action()
		act.actionValue = move
		newobs, reward = gridEnvironment.env_step(act)

		print "reward received:", reward.rewardValue
		
		totalr = totalr + reward.rewardValue

elif play == 2:
	# play as the enemy
	print "PLAY!"
	gridAgent.agent_reset()
	gridAgent.verbose = 0
	gridEnvironment.enemyMode = 4 # don't change this
	gridEnvironment.verbose = 0
	obs = gridAgent.copyObservation(gridAgent.initialObs)
	totalr = 0.0
	while(True):
		# print the map
		gridEnvironment.printEnvironment()
		print "total bot reward:", totalr
		
		# Enemy (player) move
		print "Move?"
		move = None
		x = sys.stdin.readline()
		if x.strip() == "reset":
			# reset the game state
			gridAgent.agent_reset()
			obs = gridAgent.copyObservation(gridAgent.initialObs)
			totalr = 0.0
			print "PLAY!"
			continue # I feel so bad about this
		elif x.strip() == "quit":
			# quit game
			break
		elif x[0] == '0' or x[0] == 'w':
			#up
			move = 0
		elif x[0] == '1' or x[0] == 's':
			#down
			move = 1
		elif x[0] == '2' or x[0] == 'a':
			#left
			move = 2
		elif x[0] == '3' or x[0] == 'd':
			#right
			move = 3
		gridEnvironment.nextEnemyMove = move

		# execute greedy policy
		act = Action()
		act.actionValue = gridAgent.greedy(obs)
		print "bot action:", gridEnvironment.actionToString(act.actionValue)
		print "enemy action:", gridEnvironment.actionToString(move)
		
		# bot and enemy (player) actions happen here
		newobs, reward = gridEnvironment.env_step(act)

		print "reward received:", reward.rewardValue
		
		totalr = totalr + reward.rewardValue
		obs = copy.deepcopy(newobs)


