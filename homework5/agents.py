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
from statemachine import *

############################
### STATEAGENT

class StateAgent(Agent, StateMachine):

	### states: a set of states (class names) that the agent can be in
	### state: the current state (State object). 
	
	### NOTE: use self.getStateType() to check what state the agent is in (you usually don't need an actual reference to the state object. self.getState() == Kill works for a conditional check.

	def __init__(self, image, position, orientation, speed, world, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = Bullet, states = []):
		Agent.__init__(self, image, position, orientation, speed, world, hitpoints, firerate, bulletclass)
		StateMachine.__init__(self, states)

		
	def update(self, delta):
		Agent.update(self, delta)
		StateMachine.update(self, delta)
	
	
	def getStateType(self):
		return type(self.state)
		
	def stop(self):
		Agent.stop(self)
		self.changeState(None)


#####################
### VisionAgent

class VisionAgent(StateAgent):

	### viewangle: the amount of angle, centered on the agent's orientation, that the agent can see out of
	### visible: things that are visible (movers)

	def __init__(self, image, position, orientation, speed, viewangle, world, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = Bullet, states = []):
		StateAgent.__init__(self, image, position, orientation, speed, world, hitpoints, firerate, bulletclass, states)
		self.viewangle = viewangle
		self.visible = []


	def update(self, delta):
		StateAgent.update(self, delta)
		# Ask the world for what is visible (Movers) within the cone of vision
		visible = self.world.getVisible(self.getLocation(), self.orientation, self.viewangle)
		self.visible = visible


	def getVisible(self):
		return self.visible

	def getVisibleType(self, type):
		v = []
		for x in self.visible:
			if isinstance(x, type):
				v.append(x)
		return v
		
			
			
