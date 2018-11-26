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




nav = GreedyGridNavigator()

#This contains some edge cases that a basic solution might not account for
world = GameWorld(SEED, (1200,1200), (1200,1200))
agent = Agent(AGENT, (1024,SCREEN[1]/2), 0, SPEED, world)
polygons = []

polygons = [[(884.0/2, 745.0/2), (698.0/2, 852.5/2), (698.0/2, 637.5/2)],
[(1203.0/2, 1825.0/2), (1065.0/2, 1905/2), (1065.0/2, 1745.5/2)],
[(1093.0/2, 1581.0/2), (1041/2, 1652/2), (957/2, 1625/2), (957/2, 1537/2), (1041/2, 1510/2)],
[(1722.0/2, 310.0/2), (1610/2, 464/2), (1429/2, 405/2), (1429/2, 215/2), (1610/2, 156/2)],
[(450.2, 50), (450.8, 50), (450.8, 150), (450.2, 150)],
[(540.0, 350.0), (540.0, 370.0), (560.0, 370.0), (560.0, 350.0)],
[(580.0, 350.0), (580.0, 370.0), (600.0, 370.0), (600.0, 350.0)]]

world.initializeTerrain(polygons, (255, 0, 0), 2)
world.setPlayerAgent(agent)
agent.setNavigator(nav)
nav.setWorld(world)
world.initializeRandomResources(NUMRESOURCES)
world.debugging = True
world.run()