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
from agents import *
from astarnavigator import *
from clonenav import *


BUILDRATE = 180
TOWERFIRERATE = 15
BASEFIRERATE = 15
BULLETRANGE = 150
SMALLBULLETRANGE = 150
BIGBULLETRANGE = 250
TOWERBULLETRANGE = 250
TOWERBULLETDAMAGE = 10
TOWERBULLETSPEED = (10, 10)
TOWERBULLET = "sprites/bullet2.gif"
BASEBULLETRANGE = 250
BASEBULLETDAMAGE = 10
BASEBULLETSPEED = (10, 10)
BASEBULLET = "sprites/bullet2.gif"
SPAWNNUM = 3
MAXSPAWN = 20

######################
### MOBABullet
###
### MOBABullets are like regular bullets, but expire after a certain distance is traversed.

class MOBABullet(Bullet):
	
	### range: how far the bullet will travel before expiring
	
	def __init__(self, position, orientation, world, image = SMALLBULLET, speed = SMALLBULLETSPEED, damage = SMALLBULLETDAMAGE, range = BULLETRANGE):
		Bullet.__init__(self, position, orientation, world, image, speed, damage)
		self.range = range
	
	def update(self, delta):
		Bullet.update(self, delta)
		if self.distanceTraveled > self.range:
			self.speed = (0, 0)
			self.world.deleteBullet(self)

	def hit(self, thing):
		ret = Bullet.hit(self, thing)
		if ret:
			return True
		elif isinstance(thing, Base) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			thing.damage(self.damage)
			return True
		elif isinstance(thing, Tower) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			thing.damage(self.damage)
			return True
		else:
			return False


######################
### MOBAAgent
###
### Abstract base class for MOBA agents

class MOBAAgent(VisionAgent):

	### maxHitpoints: the maximum hitpoints the agent is allowed to have

	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = MOBABullet):
		VisionAgent.__init__(self, image, position, orientation, speed, viewangle, world, hitpoints, firerate, bulletclass)
		self.maxHitpoints = hitpoints

	def start(self):
		StateAgent.start(self)
		self.world.computeFreeLocations(self)

	def collision(self, thing):
		StateAgent.collision(self, thing)
		# Agent dies if it hits an obstacle
		if isinstance(thing, Obstacle):
			self.die()

	def getMaxHitpoints(self):
		return self.maxHitpoints

	def getPossibleDestinations(self):
		return self.world.getFreeLocations(self)

#######################
### Hero

class Hero(MOBAAgent):

	def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = MOBABullet):
		MOBAAgent.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)


######################
### Minion
###
### Base class for Minions

class Minion(MOBAAgent):
	
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = MOBABullet):
		MOBAAgent.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)




######################
### BigBullet

class BigBullet(MOBABullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, BIGBULLET, BIGBULLETSPEED, BIGBULLETDAMAGE, BIGBULLETRANGE)

###########################
### SmallBullet

class SmallBullet(MOBABullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, SMALLBULLET, SMALLBULLETSPEED, SMALLBULLETDAMAGE, SMALLBULLETRANGE)


###########################
### TowerBullet

class TowerBullet(MOBABullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, TOWERBULLET, TOWERBULLETSPEED, TOWERBULLETDAMAGE, TOWERBULLETRANGE)

###########################
### BaseBullet

class BaseBullet(MOBABullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, BASEBULLET, BASEBULLETSPEED, BASEBULLETDAMAGE, BASEBULLETRANGE)







############################
### Base
###
### Bases are invulnerable if they have any towers


class Base(Mover):
	
	### team: the name of the team owning the base
	### hitpoints: how much damage the base can withstand
	### nav: a Navigator that will be cloned and given to any NPCs spawned.
	### buildTimer: timer for how often a minion can be built
	### buildRate: how often a minion can be built
	### minionType: type of minion to build
	### bulletclass: type of bullet used
	### firerate: how often the tower can fire
	### firetimer: time lapsed since last fire
	### numSpawned: number of agents spawned
	
	def __init__(self, image, position, world, team = None, minionType = Minion, buildrate = BUILDRATE, hitpoints = BASEHITPOINTS, firerate = BASEFIRERATE, bulletclass = BaseBullet):
		Mover.__init__(self, image, position, 0, 0, world)
		self.team = team
		self.hitpoints = hitpoints
		self.buildTimer = buildrate
		self.buildRate = buildrate
		self.nav = None
		self.minionType = minionType
		self.firerate = firerate
		self.firetimer = 0
		self.canfire = True
		self.bulletclass = bulletclass
		self.numSpawned = 0
	
	def setNavigator(self, nav):
		self.nav = nav
	
	def getTeam(self):
		return self.team
	
	def setTeam(self, team):
		self.team = team
	
	### Spawn an agent.
	### type: name of agent class. Must be RTSAgent or subclass thereof
	### angle: specifies where around the base the agent will be spawned
	def spawnNPC(self, type, angle = 0.0):
		agent = None
		n = len(self.world.getNPCsForTeam(self.getTeam()))
		if n < MAXSPAWN:
			vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
			agent = type(self.getLocation(), 0, self.world)
			self.numSpawned = self.numSpawned + 1
			pos = (vector[0]*(self.getRadius()+agent.getRadius())/2.0,vector[1]*(self.getRadius()+agent.getRadius())/2.0)
			#agent.rect = agent.rect.move(pos)
			agent.move(pos)
			if self.nav is not None:
				newnav = cloneAStarNavigator(self.nav)
				agent.setNavigator(newnav)
			agent.setTeam(self.team)
			agent.setOwner(self)
			self.world.addNPC(agent)
			agent.start()
		return agent

	def update(self, delta):
		Mover.update(self, delta)
		self.buildTimer = self.buildTimer + 1
		if self.buildTimer >= self.buildRate:
			for x in range(SPAWNNUM):
				angle = corerandom.randint(0, 360)
				self.spawnNPC(self.minionType, angle)
			self.buildTimer = 0
		if self.canfire == False:
			self.firetimer = self.firetimer + 1
			if self.firetimer >= self.firerate:
				self.canfire = True
				self.firetimer = 0
		if self.canfire and len(self.world.getTowersForTeam(self.getTeam())) == 0:
			targets = []
			minions = []
			heros = []
			for npc in self.world.npcs + [self.world.agent]:
				if npc.getTeam() == None or npc.getTeam() != self.getTeam() and distance(self.getLocation(), npc.getLocation()) < BASEBULLETRANGE:
					hit = rayTraceWorld(self.getLocation(), npc.getLocation(), self.world.getLines())
					if hit == None:
						if isinstance(npc, Minion):
							minions.append(npc)
						elif isinstance(npc, Hero):
							heros.append(npc)
			minions = sorted(minions, key=lambda x: distance(self.getLocation(), x.getLocation()))
			heros = sorted(heros, key=lambda x: distance(self.getLocation(), x.getLocation()))
			targets = minions + heros
			if len(targets) > 0:
				self.turnToFace(targets[0].getLocation())
				self.shoot()



	def damage(self, amount):
		if len(self.world.getTowersForTeam(self.getTeam())) == 0:
			self.hitpoints = self.hitpoints - amount
			if self.hitpoints <= 0:
				self.die()


	def die(self):
		Mover.die(self)
		print "base dies (team " + str(self.team) + ")"
		self.world.deleteBase(self)

	def shoot(self):
		if self.canfire:
			bullet = self.bulletclass(self.rect.center, self.orientation, self.world)
			bullet.setOwner(self)
			self.world.addBullet(bullet)
			self.canfire = False

	def collision(self, thing):
		Mover.collision(self, thing)
		if isinstance(thing, Hero):
			agent = thing
			if agent.getTeam() == self.getTeam():
				# Heal
				agent.hitpoints = agent.maxHitpoints


	def getHitpoints(self):
		return self.hitpoints


#####################
### Tower



class Tower(Mover):
	
	### team: team that the tower is on
	### bulletclass: type of bullet used
	### firerate: how often the tower can fire
	### firetimer: time lapsed since last fire

	def __init__(self, image, position, world, team = None, hitpoints = TOWERHITPOINTS, firerate = TOWERFIRERATE, bulletclass = TowerBullet):
		Mover.__init__(self, image, position, 0, 0, world)
		self.team = team
		self.hitpoints = hitpoints
		self.firerate = firerate
		self.firetimer = 0
		self.canfire = True
		self.bulletclass = bulletclass

	def getTeam(self):
		return self.team
	
	def setTeam(self, team):
		self.team = team


	def damage(self, amount):
		self.hitpoints = self.hitpoints - amount
		if self.hitpoints <= 0:
			self.die()

	def die(self):
		Mover.die(self)
		print "tower dies (team " + str(self.team) + ")"
		self.world.deleteTower(self)

	def update(self, delta):
		Mover.update(self, delta)
		if self.canfire == False:
			self.firetimer = self.firetimer + 1
			if self.firetimer >= self.firerate:
				self.canfire = True
				self.firetimer = 0
		if self.canfire:
			targets = []
			minions = []
			heros = []
			for npc in self.world.npcs + [self.world.agent]:
				if npc.getTeam() == None or npc.getTeam() != self.getTeam() and distance(self.getLocation(), npc.getLocation()) < TOWERBULLETRANGE:
					hit = rayTraceWorld(self.getLocation(), npc.getLocation(), self.world.getLines())
					if hit == None:
						if isinstance(npc, Minion):
							minions.append(npc)
						elif isinstance(npc, Hero):
							heros.append(npc)
			minions = sorted(minions, key=lambda x: distance(self.getLocation(), x.getLocation()))
			heros = sorted(heros, key=lambda x: distance(self.getLocation(), x.getLocation()))
			targets = minions + heros
			if len(targets) > 0:
				self.turnToFace(targets[0].getLocation())
				self.shoot()

	def shoot(self):
		if self.canfire:
			bullet = self.bulletclass(self.rect.center, self.orientation, self.world)
			bullet.setOwner(self)
			self.world.addBullet(bullet)
			self.canfire = False

	def getHitpoints(self):
		return self.hitpoints


##############################################
### MOBAWorld

class MOBAWorld(GatedWorld):
	
	### bases: the bases (one per team)
	### towers: the towers (many per team)
	
	def __init__(self, seed, worlddimensions, screendimensions, numgates, alarm):
		GatedWorld.__init__(self, seed, worlddimensions, screendimensions, numgates, alarm)
		self.bases = []
		self.towers = []
	
	def addBase(self, base):
		self.bases.append(base)
		if self.sprites is not None:
			self.sprites.add(base)
		self.movers.append(base)
	
	def deleteBase(self, base):
		if base in self.bases:
			self.bases.remove(base)
			if self.sprites is not None:
				self.sprites.remove(base)
			self.movers.remove(base)
	
	
	def addTower(self, tower):
		self.towers.append(tower)
		if self.sprites is not None:
			self.sprites.add(tower)
		self.movers.append(tower)
			
	def deleteTower(self, tower):
		if tower in self.towers:
			self.towers.remove(tower)
			if self.sprites is not None:
				self.sprites.remove(tower)
			self.movers.remove(tower)

	def getBases(self):
		return list(self.bases)
	
	def getBaseForTeam(self, team):
		for b in self.bases:
			if b.getTeam() == team:
				return b
		return None
	
	def getEnemyBases(self, myteam):
		bases = []
		for b in self.bases:
			if b.getTeam() != myteam:
				bases.append(b)
		return bases

	def getTowers(self):
		return list(self.towers)

	def getTowersForTeam(self, team):
		towers = []
		for t in self.towers:
			if t.getTeam() == team:
				towers.append(t)
		return towers

	def getEnemyTowers(self, myteam):
		towers = []
		for t in self.towers:
			if t.getTeam() != myteam:
				towers.append(t)
		return towers
	
	def getNPCsForTeam(self, team):
		npcs = []
		for x in self.getNPCs():
			if x.getTeam() == team:
				npcs.append(x)
		return npcs

	def getEnemyNPCs(self, myteam):
		npcs = []
		for x in self.getNPCs():
			if x.getTeam() != myteam:
				npcs.append(x)
		return npcs


