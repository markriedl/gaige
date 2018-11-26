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



##############################
### NearestGatherer
###
### NearestGatherer sorts the list of targets according to which one is closest to where the agent will be when it needs to go the next target

class NearestGatherer(Gatherer):

	def __init__(self, image, position, orientation, speed, world, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = Bullet):
		Gatherer.__init__(self, image, position, orientation, speed, world, hitpoints, firerate, bulletclass)
		

	def setTargets(self, targets):
		Gatherer.setTargets(self, targets)
		self.targets = sortTargets(self.getLocation(), targets)
		return None

	def addTarget(self, target):
		Gatherer.addTarget(self, target)
		self.targets = sortTargets(self.getLocation(), targets)
		return None

	def update(self, delta):
		Gatherer.update(self, delta)
		next = None
		if self.moveTarget == None and len(self.targets) > 0:
			next = self.targets[0]
		if next is not None:
			self.navigateTo(next)
		return None



def sortTargets(location, targets):
	# Get the closest
	start = None
	dist = INFINITY
	for t in targets:
		d = distance(location, t) 
		if d < dist:
			start = t
			dist = d
	# ASSERT: start has the closest node
	remaining = [] + targets
	sorted = [start]
	remaining.remove(start)
	current = start
	while len(remaining) > 0:
		closest = None
		dist = INFINITY
		for t in remaining:
			d = distance(current, t)
			if d < dist:
				closest = t
				dist = d
		sorted.append(closest)
		remaining.remove(closest)
		current = closest
	return sorted