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
from astarnavigator2 import *
from agents import *
from moba4 import *
from agents2 import *
from SquadBaselineMinion import *
from SquadBaselineHero import *

def setUpWorld(playerClass):
	############################
	### SET UP WORLD

	dims = (2560, 1400)

	obstacles = [[(1230, 0), (1330, 0), (1330, 625), (1230, 625)],
				[(1230, 1400), (1330, 1400), (1330, 775), (1230, 775)],
				[(2200, 350), (2200, 500), (2150, 500), (2150, 350)],
				[(2200, 900), (2200, 1050), (2150, 1050), (2150, 900)],
				]
	obstaclesToMirror = [[(1700, 450), (1750, 450), (1750, 575), (1700, 575)],
						[(1700, 950), (1750, 950), (1750, 825), (1700, 825)],
						[(1950, 625), (2000, 625), (2000, 775), (1950, 775)],
						[(1030, 650), (1080, 650), (1080, 750), (1030, 750)],
						]

	pathnodes = [(2300, 700), (2300, 200), (2300, 1200)
				]
	pathnodesToMirror = [(1405, 700), (1405, 600), (1405, 800), (1615, 600), (1615, 800), (1725, 700), (1980, 420), (1980, 980), (2150, 700), (1980, 200), (1980, 1200), (1615, 300), (1615, 1100)]

	network = [((2150, 700), (2300, 700)),
			((2300, 700), (2300, 200)),
			((2300, 700), (2300, 1200)),
			((2300, 200), (1980, 200)),
			((2300, 1200), (1980, 1200)),
			]
	networkToMirror = [((1405, 700), (1405, 600)),
						((1405, 700), (1405, 800)),
						((1405, 600), (1615, 600)),
						((1405, 800), (1615, 800)),
						((1615, 600), (1725, 700)),
						((1615, 800), (1725, 700)),
						((1725, 700), (1980, 420)),
						((1725, 700), (1980, 980)),
						((1980, 420), (2150, 700)),
						((1980, 980), (2150, 700)),
						((1980, 200), (1980, 420)),
						((1980, 1200), (1980, 980)),
						((1980, 200), (1615, 300)),
						((1980, 1200), (1615, 1100)),
						((1615, 300), (1615, 600)),
						((1615, 1100), (1615, 800)),
						((1615, 300), (1405, 600)),
						((1615, 1100), (1405, 800)),
						((1405, 700), (1155, 700)),
						]

	weenies = [(1380, 700), (1380, 300), (1780, 300), (2180, 300)]

	mirror = map(lambda poly: map(lambda point: (dims[0]-point[0], dims[1]-point[1]), poly), obstaclesToMirror)
	obstacles = obstacles + obstaclesToMirror + mirror

	mirror = map(lambda point: (dims[0]-point[0], dims[1]-point[1]), pathnodesToMirror)
	pathnodes = pathnodes + pathnodesToMirror + mirror

	mirror = map(lambda edge: map(lambda point: (dims[0]-point[0], dims[1]-point[1]), edge), networkToMirror)
	network = network + networkToMirror + mirror

	###########################
	### Minion Subclasses

	minionclass = SquadBaselineMinion


	class BaselineHumanMinion(minionclass):
		
		def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
			minionclass.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)

	class BaselineAlienMinion(minionclass):
		
		def __init__(self, position, orientation, world, image = JACKAL, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
			minionclass.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)


	########################
	### Hero Subclasses

	heroclass = SquadBaselineHero

	class MyHumanHero(heroclass):
		
		def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
			heroclass.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)



	class MyAlienHero(heroclass):
		
		def __init__(self, position, orientation, world, image = ELITE, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
			heroclass.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass, dodgerate, areaeffectrate, areaeffectdamage)

	########################

	def makeWeenie(location, team, owner, navigator, world):
		w = BaselineHumanMinion(location, 0, world)
		w.setNavigator(cloneAStarNavigator(navigator))
		w.setTeam(team)
		w.setOwner(owner)
		return w

	########################

	nav = AStarNavigator2()

	screenSize = (700, 700)
	world = MOBAWorld2(SEED, dims, screenSize, 0, 60)
	agent = playerClass((350, 350), 0, world, ELITE)
	world.setPlayerAgent(agent)
	if playerClass == AutomaticHero:
		agent.setNavigator(nav)
	else:
		agent.setNavigator(Navigator())
	world.initializeTerrain(obstacles, (0, 0, 0), 4)
	agent.team = 1
	world.debugging = True


	nav.agent = agent
	nav.setWorld(world)
	nav.pathnodes = pathnodes
	nav.pathnetwork = network
	nav.drawPathNetwork(world.debug)


	b1 = Base(BASE, (60, 700), world, 1, None, None, BUILDRATE)
	b1.setNavigator(nav)
	world.addBase(b1)

	enemyTowerX = 2150 + BULLETRANGE

	b2 = Base(BASE, (enemyTowerX + 50, 700), world, 2, BaselineHumanMinion, MyHumanHero, BUILDRATE, SQUADBASEHITPOINTS)
	b2.setNavigator(nav)
	world.addBase(b2)

	t11 = Tower(TOWER, (150, 700), world, 1)
	world.addTower(t11)

	#t12 = Tower(TOWER, (200, 800), world, 1)
	#world.addTower(t12)

	t21 = Tower(TOWER, (enemyTowerX, 550), world, 2, SQUADTOWERHITPOINTS, BIGTOWERFIRERATE, BIGTOWERBULLETRANGE, BigTowerBullet)
	world.addTower(t21)

	t22 = Tower(TOWER, (enemyTowerX, 850), world, 2, SQUADTOWERHITPOINTS, BIGTOWERFIRERATE, BIGTOWERBULLETRANGE, BigTowerBullet)
	world.addTower(t22)




	c1 = MyCompanionHero((150, 550), 0, world, SHIELDJACKAL)
	c1.setNavigator(cloneAStarNavigator(nav))
	c1.team = 1
	c1.id = 1
	world.addNPC(c1)
	c2 = MyCompanionHero((150, 650), 0, world, SHIELDJACKAL)
	c2.setNavigator(cloneAStarNavigator(nav))
	c2.team = 1
	c2.id = 2
	world.addNPC(c2)
	healer = MyHealer((150, 600), 0, world)
	healer.setNavigator(cloneAStarNavigator(nav))
	healer.team = 1
	world.addNPC(healer)

	world.makePotentialGates()

	healer.start()
	c1.start()
	c2.start()

	for loc in weenies:
		w = makeWeenie(loc, 2, b2, nav, world)
		world.addNPC(w)
		w.start()
	return world

if __name__ == "__main__":
	playerClass = None
	args = sys.argv
	if args and len(args) > 1:
		if args[1] == "PlayerHero":
			playerClass = PlayerHero
		elif args[1] == "AutomaticHero":
			playerClass = AutomaticHero
	if not playerClass:
		sys.exit("Usage: Specify PlayerHero or AutomaticHero.")

	world = setUpWorld(playerClass)
	world.run()