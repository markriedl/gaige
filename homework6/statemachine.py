'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *

############################
### STATE

class State(object):

	### agent: the agent this state machine is controlling

	### args is a list of arguments. The args must be parsed by the constructor
	def __init__(self, agent, args = []):
		self.agent = agent
		self.parseArgs(args)

	def execute(self, delta = 0):
		return None
		
	def enter(self, oldstate):
		return None
		
	def exit(self):
		return None
		
	def parseArgs(self, args):
		return None


############################
### STATEMACHINE

class StateMachine():

	### states: a set of states (class names) that the agent can be in
	### state: the current state (State object).
	
	def __init__(self, states):
		self.states = states
		self.state = None
		
	def update(self, delta):
		if self.state is not None:
			self.state.execute(delta)
		
	
	def changeState(self, newstateclass, *args):
		if self.states is not None and (newstateclass == None or newstateclass in self.states):
			old = self.state
			if old is not None:
				old.exit()
			if newstateclass is not None:
				new = newstateclass(self, args)
				if old is not None:
					new.enter(type(old))
				else:
					new.enter(None)
				self.state = new
			else:
				self.state = None

	def getState(self):
		if self.state == None:
			return None
		else:
			return type(self.state)
