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
from agents import *
from moba2 import *
from MyHero import *
from WanderingMinion import *
from clonenav import *

if len(sys.argv) < 3:
	print "Usage: python " + sys.argv[0] + " classname1 classname2"
	print "classname1 and classname2 must be in files with the same located in this directory."
	exit(1)

module1 = __import__(sys.argv[1])
module2 = __import__(sys.argv[2])
class1 = getattr(module1, sys.argv[1])
class2 = getattr(module2, sys.argv[2])

############################
### How to use this file
###
### Use this file to conduct a competition with other agents.
### Step 1: Give your MyHero class an unique name, e.g., MarkHero. Change the file name to match the class name exactly.
### Step 2: python runherocompetition.py classname1 classname2

############################
### SET UP WORLD

dims = (1200, 1200)

obstacles = [[(250, 150), (600, 200), (550, 350), (260, 390)],
			 [(800, 200), (1040, 140), (1050, 160), (1025, 500), (1000, 500), (810, 310)]]


mirror = map(lambda poly: map(lambda point: (dims[0]-point[0], dims[1]-point[1]), poly), obstacles)

obstacles = obstacles + mirror

obstacles = obstacles + [[(550, 570), (600, 550), (660, 570), (650, 630), (600, 650), (540, 630)]]

###########################
### Minion Subclasses


class WanderingHumanMinion(WanderingMinion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		WanderingMinion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)

class WanderingAlienMinion(WanderingMinion):
	
	def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		WanderingMinion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)


########################
### Hero Subclasses

class MyHumanHero(class1):
	
	def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		class1.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)



class MyAlienHero(class2):
	
	def __init__(self, position, orientation, world, image = ELITE, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		class2.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)



########################

world = MOBAWorld(SEED, dims, dims, 0, 60)
agent = GhostAgent(ELITE, (600, 500), 0, SPEED, world)
#agent = Hero((600, 500), 0, world, ELITE)
world.setPlayerAgent(agent)
world.initializeTerrain(obstacles, (0, 0, 0), 4)
agent.setNavigator(Navigator())
agent.team = 0
world.debugging = True


nav = AStarNavigator()
nav.agent = agent
nav.setWorld(world)

b1 = Base(BASE, (75, 75), world, 1, WanderingHumanMinion, MyHumanHero, BUILDRATE, 1000)
b1.setNavigator(nav)
world.addBase(b1)


b2 = Base(BASE, (1125, 1125), world, 2, WanderingAlienMinion, MyAlienHero, BUILDRATE, 1000)
b2.setNavigator(nav)
world.addBase(b2)


hero1 = MyHumanHero((125, 125), 0, world)
hero1.setNavigator(cloneAStarNavigator(nav))
hero1.team = 1
world.addNPC(hero1)
hero2 = MyAlienHero((1050, 1025), 0, world)
hero2.setNavigator(cloneAStarNavigator(nav))
hero2.team = 2
world.addNPC(hero2)

world.makePotentialGates()

hero1.start()
hero2.start()



world.run()
