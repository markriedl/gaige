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
from gridnavigator import *
			
			
			
			
nav = RandomGridNavigator()
			
#This is the tall one with sparse obstacles	
world = GameWorld(SEED, (768,1024), (768,1024))
agent = Agent(AGENT, (384,SCREEN[1]/2), 0, SPEED, world)

polygons = [[(430.0, 847.0), (399.5, 889), (350.5, 873), (350.5, 821), (399.5, 805)], 
[(242.0, 796.0), (187.0, 851.0), (132.0, 796.0), (187.0, 741.0)], 
[(602.0, 396.0), (547.0, 451.0), (492.0, 396.0), (547.0, 341.0)], 
[(254.0, 605.0), (230.0, 646.5), (182.0, 646.5), (158.0, 605.0), (182, 563.5), (230.0, 563.5)], 
[(391.0, 264.0), (370, 307.5), (323, 319), (285, 289.5), (284, 241), (320.5, 210), (368, 218.5)]]


world.initializeTerrain(polygons, (255, 0, 0), 2) 
world.setPlayerAgent(agent)
agent.setNavigator(nav)
nav.setWorld(world)
world.initializeRandomResources(NUMRESOURCES)
world.debugging = True
world.run()
