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

import os, sys, pygame, math, numpy, random, time, copy, compileall, shutil
from pygame.locals import *

from constants import *
from utils import *
from core import *
from agents import *

import imp

def getNav(astar_module):
	nav = astar_module.AStarNavigator()
	return nav

def cloneDynamicAStarNavigator(astar_module, nav):
	newnav = astar_module.AStarNavigator()
	newnav.world = nav.world
	newnav.pathnodes = nav.pathnodes
	newnav.pathnetwork = nav.pathnetwork
	newnav.navmesh = nav.navmesh
	return newnav


buildBaseFolder = "build"
submissionFiles = ("mycreatepathnetwork", "mynavigatorhelpers", "astarnavigator", "btnode", "behaviortree", "mybehaviors", "MyMinion", "MyHero")

def buildClassFile(classFile, buildFolder):
	buildPath = os.path.join(".", buildBaseFolder, buildFolder)

	for fileName in submissionFiles:
		filePath = os.path.join(classFile, fileName + ".py")
		if not os.path.exists(filePath):
			filePath = os.path.join(".", fileName + ".py")
		if not os.path.exists(filePath):
			filePath = None
		compiledPath = os.path.join(classFile, fileName + ".pyc")
		if filePath:
			with open(filePath, "r") as sourceFile:
				sourceText = sourceFile.read()

			for moduleName in submissionFiles:
				sourceText = sourceText.replace(moduleName, moduleName + buildFolder)

			if not os.path.exists(buildPath):
				os.makedirs(buildPath)
			outputPath = os.path.join(buildPath, fileName + buildFolder + ".py")
			with open(outputPath, "w") as sourceFile:
				sourceFile.write(sourceText)
		elif os.path.exists(compiledPath):
			filePath = os.path.join(".", buildBaseFolder, buildFolder, fileName + buildFolder + ".py")
			if os.path.exists(filePath):
				os.remove(filePath)
			shutil.copyfile(compiledPath, os.path.join(".", buildBaseFolder, buildFolder, fileName + buildFolder + ".pyc"))
		elif fileName != "mybehaviors":
			raise ImportError(fileName + " not found for " + classFile)

	compileall.compile_dir(buildPath)

	for fileName in submissionFiles:
		compiledFile = os.path.join(buildPath, fileName + buildFolder + ".pyc")
		module = imp.load_compiled(fileName + buildFolder, compiledFile)
		imp.load_compiled(fileName, compiledFile)

		if fileName == 'astarnavigator':
			astar = module
		elif fileName == 'MyMinion':
			minion = module
		elif fileName == 'MyHero':
			hero = module

	return astar, minion, hero

directory1 = ""
directory2 = ""

if len(sys.argv) < 3:
	print "Usage:\t\tpython runversus.py directory_name_1 directory_name_2"
	print "Results in simulation of directory_name_1's Heroes and Minions versus directory_name_2's Heroes and Minions"
	print "example directory names: \"Baseline1\", \"Baseline2\", \"Baseline3\", (baseline heroes & minions) and \"Mine\" (custom hero & minions)."
	print "default:\tpython runversus.py \"Mine\" \"Mine\"\n"
	directory1 = "Mine"
	directory2 = "Mine"
else:
	directory1 = sys.argv[1]
	directory2 = sys.argv[2]

# use the given directorys' classfiles
classFile1 = "./" + directory1
classFile2 = "./" + directory2

astar1, minion1, hero1 = buildClassFile(classFile1, "1")
astar2, minion2, hero2 = buildClassFile(classFile2, "2")

nav1 = getNav(astar1)
nav2 = getNav(astar2)

from moba3 import *

# get hero classes from hero modules
try:
	heroclass1 = getattr(hero1, "MyHero1")
except AttributeError:
	heroclass1 = getattr(hero1, "MyHero")
try:
	heroclass2 = getattr(hero2, "MyHero2")
except AttributeError:
	heroclass2 = getattr(hero2, "MyHero")
# get minion classes from minion modules
try:
	minionclass1 = getattr(minion1, "MyMinion1")
except AttributeError:
	minionclass1 = getattr(minion1, "MyMinion")
try:
	minionclass2 = getattr(minion2, "MyMinion2")
except AttributeError:
	minionclass2 = getattr(minion2, "MyMinion")


########################
### Minion Subclasses

class MyHumanMinion(minionclass1):

	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		minionclass1.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)

class MyAlienMinion(minionclass2):

	def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		minionclass2.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)


########################
### Hero Subclasses

class MyHumanHero(heroclass1):

	def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		heroclass1.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)

class MyAlienHero(heroclass2):

	def __init__(self, position, orientation, world, image = ELITE, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		heroclass2.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)

########################


############################
### SET UP WORLD

dims = (1200, 1200)

#obstacles = [[(250, 150), (600, 160), (590, 400), (260, 390)],
#			 [(800, 170), (1040, 140), (1050, 160), (1040, 500), (810, 310)]]
obstacles = [[(400, 150), (850, 150), (900, 300), (1050, 350), (1050, 800), (1010, 825), (990, 825), (900, 750), (900, 500), (700, 300), (450, 300), (375, 210), (375, 190)]
			 ]


mirror = map(lambda poly: map(lambda point: (dims[0]-point[0], dims[1]-point[1]), poly), obstacles)

obstacles = obstacles + mirror



world = MOBAWorld(SEED, dims, dims, 1, 60)
agent = GhostAgent(ELITE, (0, 0), 0, SPEED, world)
world.setPlayerAgent(agent)
world.initializeTerrain(obstacles, (0, 0, 0), 4)
agent.setNavigator(Navigator())
agent.team = 0
world.debugging = True

# create AStarNavigator using student's astar module
nav1.setAgent(agent)
nav1.setWorld(world)

b1 = Base(BASE, (75, 75), world, 1, MyHumanMinion, MyHumanHero, BUILDRATE)
b1.setNavigator(nav1)
world.addBase(b1)

t11 = Tower(TOWER, (250, 100), world, 1)
world.addTower(t11)
t12 = Tower(TOWER, (100, 250), world, 1)
world.addTower(t12)


# create AStarNavigator using student's astar module
nav2.setAgent(agent)
nav2.setWorld(world)

b2 = Base(BASE, (1125, 1125), world, 2, MyAlienMinion, MyAlienHero, BUILDRATE)
b2.setNavigator(nav2)
world.addBase(b2)

t21 = Tower(TOWER, (1100, 950), world, 2)
world.addTower(t21)
t22 = Tower(TOWER, (950, 1100), world, 2)
world.addTower(t22)

hero1 = MyHumanHero((125, 125), 0, world)
hero1.setNavigator(cloneDynamicAStarNavigator(astar1, nav1))
hero1.team = 1
world.addNPC(hero1)
hero2 = MyAlienHero((1025, 1025), 0, world)
hero2.setNavigator(cloneDynamicAStarNavigator(astar2, nav2))
hero2.team = 2
world.addNPC(hero2)

world.makePotentialGates()

hero1.start()
hero2.start()

world.run()
