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


### Modifications:
### - Hero can dodge
### - MAXSPAWN = 3
### - Press 'j' to make agent dodge randomly
### - MOBABullets tell MOBAAgents who did the damage
### - MOBAAgent.creditKill, Hero.creditKill

HEROHITPOINTS = 50
BUILDRATE = 60
TOWERFIRERATE = 15
BIGTOWERFIRERATE = 10
BASEFIRERATE = 20
BULLETRANGE = 150
SMALLBULLETRANGE = 150
BIGBULLETRANGE = 250
TOWERBULLETRANGE = 150
BIGTOWERBULLETRANGE = 1000
TOWERBULLETDAMAGE = 10
BIGTOWERBULLETDAMAGE = 10
TOWERBULLETSPEED = (20, 20)
TOWERBULLET = "sprites/bullet2.gif"
BASEBULLETRANGE = 200
BASEBULLETDAMAGE = 10
BASEBULLETSPEED = (20, 20)
BASEBULLET = "sprites/bullet2.gif"
SPAWNNUM = 1
MAXSPAWN = 10
AREAEFFECTDAMAGE = 25
AREAEFFECTRATE = 60
AREAEFFECTRANGE = 2

SPAWNTHRESHOLD = 1100

SQUADBASEHITPOINTS = 5
SQUADTOWERHITPOINTS = 3

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
		if isinstance(thing, GhostAgent):
			return False
		ret = Bullet.hit(self, thing)
		if isinstance(thing, MOBAAgent) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			#Already dished damage to another agent, so just keep track of who did the damage
			thing.lastDamagedBy = self.owner
			ret = True
			# Should the agent get some score? Heros score by shooting Heros
			self.world.damageCaused(self.owner, thing, self.damage)
		elif isinstance(thing, Base) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			thing.damage(self.damage)
			ret = True
		elif isinstance(thing, Tower) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			thing.damage(self.damage)
			ret = True
		return ret

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

class BigTowerBullet(TowerBullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, TOWERBULLET, TOWERBULLETSPEED, BIGTOWERBULLETDAMAGE, BIGTOWERBULLETRANGE)


###########################
### BaseBullet

class BaseBullet(MOBABullet):
	
	def __init__(self, position, orientation, world):
		MOBABullet.__init__(self, position, orientation, world, BASEBULLET, BASEBULLETSPEED, BASEBULLETDAMAGE, BASEBULLETRANGE)




######################
### MOBAAgent
###
### Abstract base class for MOBA agents

class MOBAAgent(VisionAgent):

	### maxHitpoints: the maximum hitpoints the agent is allowed to have
	### lastDamagedBy: the agent that last did damage to me.
	### level: the level obtained by this agent. Level starts at 0.

	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = MOBABullet):
		VisionAgent.__init__(self, image, position, orientation, speed, viewangle, world, hitpoints, firerate, bulletclass)
		self.maxHitpoints = hitpoints
		self.lastDamagedBy = None
		self.level = 0

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

	def die(self):
		VisionAgent.die(self)
		# Give a damage modifier
		if self.lastDamagedBy is not None and isinstance(self.lastDamagedBy, MOBAAgent):
			self.lastDamagedBy.creditKill(self)

	def creditKill(self, killed):
		return None
	
	def getLevel(self):
		return self.level
	
	def shoot(self):
		bullet = VisionAgent.shoot(self)
		# If a bullet is spawned, increase its damage by agent's level
		if bullet is not None:
			bullet.damage = bullet.damage + self.level
		return bullet

#######################
### Hero

class Hero(MOBAAgent):

	### dodgeRate: how often the agent can dodge
	### candodge: the agent can dodge now
	### dodgeTimer: counting up until the agent can dodge again
	### areaEffectDamage: how much damage the area effect attack does
	### canareaeffect: the agent can use area effect attack now
	### areaEffectRate: how often the agent can use area effect attack
	### areaEffectTimer: counting up until the agent can use area effect attack

	def __init__(self, position, orientation, world, image = AGENT, speed = SPEED, viewangle = 360, hitpoints = HEROHITPOINTS, firerate = FIRERATE, bulletclass = BigBullet, dodgerate = DODGERATE, areaeffectrate = AREAEFFECTRATE, areaeffectdamage = AREAEFFECTDAMAGE):
		MOBAAgent.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.dodgeRate = dodgerate
		self.dodgeTimer = 0
		self.candodge = True
		self.canareaeffect = True
		self.areaEffectRate = areaeffectrate
		self.areaEffectDamage = areaeffectdamage
		self.areaEffectTimer = 0

	def update(self, delta = 0):
		MOBAAgent.update(self, delta)
		if self.candodge == False:
			self.dodgeTimer = self.dodgeTimer + 1
			if self.dodgeTimer >= self.dodgeRate:
				self.candodge = True
				self.dodgeTimer = 0
		if self.canareaeffect == False:
			self.areaEffectTimer = self.areaEffectTimer + 1
			if self.areaEffectTimer >= self.areaEffectRate:
				self.canareaeffect = True
				self.areaEffectTimer = 0

	def dodge(self, angle = None):
		if self.candodge:
			if angle == None:
				angle = corerandom.uniform(0, 360)
			vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
			self.move((vector[0]*self.getMaxRadius(), vector[1]*self.getMaxRadius()))
			self.candodge = False

	def areaEffect(self):
		if self.canareaeffect:
			self.canareaeffect = False
			pygame.draw.circle(self.world.background, (255, 0, 0), (int(self.getLocation()[0]), int(self.getLocation()[1])), int(self.getMaxRadius()*AREAEFFECTRANGE), 1)
			for x in self.world.getEnemyNPCs(self.getTeam()) + self.world.getEnemyBases(self.getTeam()) + self.world.getEnemyTowers(self.getTeam()):
				if distance(self.getLocation(), x.getLocation()) < (self.getMaxRadius()*AREAEFFECTRANGE)+(x.getRadius()):
					x.lastDamagedBy = self
					scaledDamage = self.areaEffectDamage + self.level
					x.damage(scaledDamage)
					self.world.damageCaused(self, x, scaledDamage)
			return True
		return False

	def creditKill(self, killed):
		MOBAAgent.creditKill(self, killed)
		self.level = self.level + 1
		self.maxHitpoints = self.maxHitpoints + 1
		return None


	def canDodge(self):
		return self.candodge

	def canAreaEffect(self):
		return self.canareaeffect

######################
### Minion
###
### Base class for Minions

class Minion(MOBAAgent):
	
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = MOBABullet):
		MOBAAgent.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)









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
	### heroType: type of hero to build
	### bulletclass: type of bullet used
	### firerate: how often the tower can fire
	### firetimer: time lapsed since last fire
	
	def __init__(self, image, position, world, team = None, minionType = Minion, heroType = Hero, buildrate = BUILDRATE, hitpoints = BASEHITPOINTS, firerate = BASEFIRERATE, bulletclass = BaseBullet):
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
		self.heroType = heroType
	
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
		if type != None:
			n = len(self.world.getNPCsForTeam(self.getTeam()))
			if n < MAXSPAWN:
				vector = (math.cos(math.radians(angle)), -math.sin(math.radians(angle)))
				agent = type(self.getLocation(), 0, self.world)
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
						elif isinstance(npc, Hero) and not isinstance(npc, GhostAgent):
							heros.append(npc)
			minions = sorted(minions, key=lambda x: distance(self.getLocation(), x.getLocation()))
			heros = sorted(heros, key=lambda x: distance(self.getLocation(), x.getLocation()))
			targets = minions + heros
			if len(targets) > 0:
				self.turnToFace(targets[0].getLocation())
				self.shoot()
		friends = self.world.getNPCsForTeam(self.getTeam())
		# Look for my hero
		hero = None
		for a in friends:
			if isinstance(a, Hero):
				hero = a
				break
		if hero == None:
			pass
			# spawn new hero
			# self.spawnNPC(self.heroType)

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
			return bullet
		else:
			return None

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
	### range: how far the tower can shoot

	def __init__(self, image, position, world, team = None, hitpoints = TOWERHITPOINTS, firerate = TOWERFIRERATE, range = TOWERBULLETRANGE, bulletclass = TowerBullet):
		Mover.__init__(self, image, position, 0, 0, world)
		self.team = team
		self.hitpoints = hitpoints
		self.firerate = firerate
		self.firetimer = 0
		self.canfire = True
		self.bulletclass = bulletclass
		self.range = range

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
				if npc.getTeam() == None or npc.getTeam() != self.getTeam() and distance(self.getLocation(), npc.getLocation()) < self.range:
					hit = rayTraceWorld(self.getLocation(), npc.getLocation(), self.world.getLines())
					if hit == None:
						if isinstance(npc, Minion):
							minions.append(npc)
						elif isinstance(npc, Hero) and not isinstance(npc, GhostAgent):
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
			return bullet
		else:
			return None

	def getHitpoints(self):
		return self.hitpoints


##############################################
### MOBAWorld

class MOBAWorld(GatedWorld):
	
	### bases: the bases (one per team)
	### towers: the towers (many per team)
	### score: dictionary with team symbol as key and team score as value. Score is amount of damage done to the hero.
	
	def __init__(self, seed, worlddimensions, screendimensions, numgates, alarm):
		GatedWorld.__init__(self, seed, worlddimensions, screendimensions, numgates, alarm)
		self.bases = []
		self.towers = []
		self.score = {}
	
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
		for x in self.getNPCs() + [self.getAgent()]:
			if x.getTeam() == team:
				npcs.append(x)
		return npcs

	def getEnemyNPCs(self, myteam):
		npcs = []
		for x in self.getNPCs() + [self.getAgent()]:
			if x.getTeam() != myteam:
				npcs.append(x)
		return npcs


	def doKeyDown(self, key):
		GatedWorld.doKeyDown(self, key)
		if key == 106: #'j'
			if isinstance(self.agent, Hero):
				self.agent.dodge()
		elif key == 97: #'a'
			if isinstance(self.agent, Hero):
				self.agent.areaEffect()

	def damageCaused(self, damager, damagee, amount):
		pass
		'''
		if isinstance(damager, Hero) and isinstance(damagee, Hero):
			self.addToScore(damager.getTeam(), amount)
		'''


	def addToScore(self, team, amount):
		if team is not None:
			if team not in self.score.keys():
				self.score[team] = 0
			self.score[team] = self.score[team] + amount
			print "Score", self.score

	def getScore(self, team):
		if team is not None:
			if team not in self.score.keys():
				self.score[team] = 0
			return self.score[team]
		return 0



