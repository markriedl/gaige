import sys

class Reward:

	rewardValue = 0.0
	pseudoRewardValue = 0.0
	def __init__(self, value=None):
		if value != None:
			self.rewardValue = value
