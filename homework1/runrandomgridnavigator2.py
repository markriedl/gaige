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
			
#This is the square with a lot of obstacles		
world = GameWorld(SEED, (768,768), (768,768))
agent = Agent(AGENT, (384,384), 0, SPEED, world)

polygons = [[(223.0, 137.0), (212.5, 169), (185, 189), (151, 189), (123.5, 169), (113.0, 137.0), (123.5, 104.5), (151, 84.5), (185, 84.5), (212.5, 104.5)], 
[(700, 160), (630.0, 143), (650, 100)], 
[(260.0, 422.0), (205, 555), (72, 610.0), (72, 234.0), (205, 289)], 
[(515.0, 216.0), (488, 289), (421, 328), (344.0, 315), (294, 255), (294, 177), (344, 117), (421, 104), (488, 143)], 
[(773.0, 558.0), (724, 660.5), (613.5, 687), (523, 618), (520, 504), (607, 430.5), (718.5, 451)], 
[(100.0, 14.0), (130, 14.5), (80.5, 50)], 
[(586.0, 57.0), (570.5, 94.5), (533.0, 110.0), (495.5, 94.5), (480.0, 57), (495.5, 19.5), (533.0, 4.0), (570.5, 19.5)]]


world.initializeTerrain(polygons, (255, 0, 0), 2) 
world.setPlayerAgent(agent)
agent.setNavigator(nav)
nav.setWorld(world)
world.initializeRandomResources(NUMRESOURCES)
world.debugging = True
world.run()
