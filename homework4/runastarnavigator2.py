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
from astarnavigator import *
from nearestgatherer import *

def getLocation(mover):
	return mover.getLocation()
	
	
def cloneAStarNavigator(nav):
	newnav = nav.__class__()
	newnav.world = nav.world
	newnav.pathnodes = nav.pathnodes
	newnav.pathnetwork = nav.pathnetwork
	newnav.navmesh = nav.navmesh
	return newnav

nav = AStarNavigator()

			
world = GatedWorld(SEED, (1000, 1000), (1000, 1000), 2, 60)
agent = Agent(AGENT, (200, 200), 0, SPEED, world)
world.initializeTerrain([[(180, 420), (360, 275), (680, 371), (630, 660), (380, 697)]])
world.setPlayerAgent(agent)
agent.setNavigator(nav)
nav.setWorld(world)
world.initializeResources([(220, 575), (550, 700), (700, 500), (900, 300)], RESOURCE)
world.debugging = True

g = NearestGatherer(NPC, (50, 50), 0.0, SPEED, world)
nav2 = cloneAStarNavigator(nav)
g.setNavigator(nav2)
g.setTargets(map(getLocation, list(world.resources)))
world.addNPC(g)
g.start()

world.makePotentialGates()
world.drawPotentialGates()
world.run()
