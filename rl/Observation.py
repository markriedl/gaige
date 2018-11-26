class Observation:
	worldState = []
	availableActions = []
	hierarchy = {}
	isTerminal = None
	def __init__(self, state=None, actions=None, hierarchy=None, isTerminal=None):
		if state != None:
			self.worldState = state

		if actions != None:
			self.availableActions = actions

		if hierarchy != None:
			self.hierarchy = hierarchy

		if isTerminal != None:
			self.isTerminal = isTerminal

