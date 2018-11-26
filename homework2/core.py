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


###########################

corerandom = random.Random()


  
###########################
### Thing

class Thing(object):

	def update(self, delta):
		return None
		
	def collision(self, thing):
		return None
		
#	def notify(self):
#		return None
  

###########################
### Mover

class Mover(pygame.sprite.Sprite, Thing):

		
	### rect: the rectangle
	### image: the image, rotated to orientation
	### originalImage: the image un-rotated
	### orientation: direction agent is facing in degrees (0 = to the right)
	### speed: how fast the agent moves (horizontal, vertical)
	### maxradius: the worst-case scenario for the bounding circle, accounting for rotation changing the dimensions of the agent's bounding box.
	### radius: the bounding circle (max(width, height))
	### world: the world
	### owner: the thing that created me
	### alive: the agent is alive (boolean)
	
	def __init__(self, image, position, orientation, speed, world):
		pygame.sprite.Sprite.__init__(self) # call sprite initializer
		self.image, self.rect = load_image(image, -1)
		self.originalImage = self.image.copy()
		self.orientation = orientation
		self.world = world
		self.speed = speed
		self.maxradius = pow(pow(self.getRadius() * 2, 2) * 2, 0.5) / 2
		## Translate to initial position
		self.position = (0.0, 0.0)
		self.move(position)
		self.turnToAngle(orientation)
		self.owner = None
		self.alive = True
		
	def getRadius(self):
		return distance(self.rect.topleft, self.rect.bottomright)/2.0

	# Gets the worst-case scenario for the object's radius, accounting for all rotations.
	def getMaxRadius(self):
		return self.maxradius

	def move(self, offset):
		self.position = tuple(map(lambda x, y: x + y, self.position, offset))
		self.rect.center = self.position
	
	### Tells the agent to face a point
	def turnToFace(self, pos):
#		direction = [m - n for m,n in zip(pos,self.position)]
		direction = (pos[0] - self.getLocation()[0], pos[1] - self.getLocation()[1])
		angle = math.degrees(numpy.arctan2(direction[0],direction[1]))-90
		self.turnToAngle(angle)
		
	### Tells the agent which way to face
	def turnToAngle(self, angle):
		if angle < 0:
			#unwind
			angle = 360+angle
		self.orientation = angle
		rot_img = pygame.transform.rotate(self.originalImage, self.orientation)
		img_rect = rot_img.get_rect()
		img_rect.center = self.position
		self.image = rot_img
		self.rect = img_rect
	
	### Update the agent every tick. Primarily does movement
	def update(self, delta):
		Thing.update(self, delta)
		return None
		
	### When something collides with me
	def collision(self, thing):
		Thing.collision(self, thing)
#		print "collision", self, thing
		return None
		
	# Get the object's (x, y) location
	def getLocation(self):
		return self.position
		
	def getOrientation(self):
		return self.orientation
		
	def getOwner(self):
		return self.owner
		
	def setOwner(self, owner):
		self.owner = owner

	def isAlive(self):
		return self.alive

	def die(self):
		self.alive = False
		
############################
### RESOURCE

class Resource(Mover):

	def __init__(self, image, position, orientation, world):
		Mover.__init__(self, image, position, orientation, (0, 0), world)


			
###########################
### SimpleResource

class SimpleResource(Resource):

	def __init__(self, image, position, orientation, world):
		Resource.__init__(self, image, position, orientation, world)

	def collision(self, thing):
		Resource.collision(self, thing)
		if isinstance(thing, Agent):
			print "grabbed"
			self.world.deleteResource(self)


###########################
### BULLET

class Bullet(Mover):
	
	### damage: amount of damage
	### distanceTraveled: the total amount of distance traveled by the agent


	def __init__(self, position, orientation, world, image = SMALLBULLET, speed = SMALLBULLETSPEED, damage = SMALLBULLETDAMAGE):
		Mover.__init__(self, image, position, orientation, speed, world)
		self.damage = damage
		self.distanceTraveled = 0
		
	def getDamage(self):
		return self.damage
		
	### Update the agent every tick. Primarily does movement
	def update(self, delta):
		Mover.update(self, delta)
		unwound = self.orientation
		if unwound < 0:
			unwound = unwound + 360.0
		rad = math.radians(unwound)
		normalizedDirection = (math.cos(rad), -math.sin(rad))
		next = [m*n for m,n in zip(normalizedDirection,self.speed)]
		self.distanceTraveled = self.distanceTraveled + distance((0,0), next)
		self.move(next)
		return None

	def collision(self, thing):
		Mover.collision(self, thing)
		if self.hit(thing):
			self.speed = (0, 0)
			self.world.deleteBullet(self)

	### Hit verifies that it has hit something hitable and what it should do (e.g., cause damage) 
	def hit(self, thing):
		if thing != self.owner and isinstance(thing, Agent) and (thing.getTeam() == None or thing.getTeam() != self.owner.getTeam()):
			thing.damage(self.damage)
			return True
		elif isinstance(thing, Obstacle) or isinstance(thing, Gate) or self.position[0] < 0 or self.position[0] > self.world.dimensions[0] or self.position[1] < 0 or self.position[1] > self.world.dimensions[1]:
			return True
		else:
			return False


				
				


###########################
### AGENT

class Agent(Mover):

	### moveTarget: where to move to. Setting this to non-None value activates movement (update fn)
	### moveOrigin: where moving from.
	### navigator: model that does path planning
	### firerate: how often agent can fire
	### firetimer: how long since last firing
	### canfire: can the agent fire?
	### hitpoints: amount of damage the agent can take
	### team: symbol referring to the team (or None)
	### distanceTraveled: the total amount of distance traveled by the agent

	### Constructor
	def __init__(self, image, position, orientation, speed, world, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = Bullet):
		Mover.__init__(self, image, position, orientation, speed, world) 
		self.moveTarget = None
		self.moveOrigin = None
		self.navigator = None
#		self.bulletspeed = bulletspeed
		self.firerate = firerate
		self.firetimer = 0
		self.canfire = True
		self.bulletclass = bulletclass
		self.hitpoints = hitpoints
		self.team = None
		self.distanceTraveled = 0


	### Update the agent every tick. Primarily does movement
	def update(self, delta):
		Mover.update(self, delta)
		if self.moveTarget is not None:
			drawCross(self.world.background, self.moveTarget, (0, 0, 0), 5)
			direction = [m - n for m,n in zip(self.moveTarget,self.position)]
			# Figure out distance to moveTarget
#			mag = reduce(lambda x, y: (x**2)+(y**2), direction)**0.5 
			mag = distance(self.getLocation(), self.moveTarget)
			if mag < self.getRadius()/2.0: #min(self.rect.width,self.rect.height)/2.0:
				# Close enough
				self.moveTarget = None
				self.moveOrigin = None
				if self.navigator != None:
					self.navigator.doneMoving()
					self.doneMoving()
			else:
				# Move
				normalizedDirection = [x/mag for x in direction]
				next = [m*n for m,n in zip(normalizedDirection,self.speed)]
				self.distanceTraveled = self.distanceTraveled + distance((0,0), next)
				self.move(next)
				self.navigator.update(delta)
				# Check for shortcut
				if self.navigator != None:
					self.navigator.smooth()
		if self.canfire == False:
			self.firetimer = self.firetimer + 1
			if self.firetimer >= self.firerate:
				self.canfire = True
				self.firetimer = 0
		return None
		
	def doneMoving(self):
		return None
		
	### NOTE: problem: Agent can be subclassed and collision() can be overridden such that the agent is not stopped by obstacles/blockers
	def collision(self, thing):
		Mover.collision(self, thing)
		if self.moveTarget is not None:
			if isinstance(thing, Blocker):
				# Ran into something that I can't move through
				self.moveTarget = None
				self.moveOrigin = None
				if self.navigator != None:
					self.navigator.collision(thing)
		return None
		
			
	### MoveToTarget tells the agent where to go and starts movement
	def moveToTarget(self, pos):
		self.moveTarget = pos
		self.moveOrigin = self.position
		self.turnToFace(pos)
	

	### Set the path planning module
	def setNavigator(self, navigator):
		navigator.setAgent(self)
		self.navigator = navigator

	def navigateTo(self, pos):
		if self.navigator != None:
			self.navigator.computePath(self.position, pos)

	### Shoot the gun. Return the bullet that was spawned, or None.
	def shoot(self):
		if self.canfire:
			bullet = self.bulletclass(self.position, self.orientation, self.world)
			bullet.setOwner(self)
			self.world.addBullet(bullet)
			self.canfire = False
			return bullet
		else:
			return None
			
	def setTeam(self, team):
		self.team = team
		
	def getTeam(self):
		return self.team
		
	def damage(self, amount):
		self.hitpoints = self.hitpoints - amount
		### Something should happen when hitpoints are <= 0
		if self.hitpoints <= 0:
			self.die()

	def die(self):
		Mover.die(self)
		self.stop()
		self.world.deleteNPC(self)
		
	def start(self):
		return None
		
	def stop(self):
		self.stopMoving()
		
	def stopMoving(self):
		self.moveTarget = None
		
	def isMoving(self):
		if self.moveTarget is not None:
			return True
		else:
			return False

		
	def getMoveTarget(self):
		return self.moveTarget

	def getHitpoints(self):
		return self.hitpoints

	def canFire(self):
		return self.canfire 

							
#####################
### GhostAgent
### 
### Doesn't collide with anything. This is handled by overriding the collision function, which is generally a bad idea.

class GhostAgent(Agent):

	def collision(self, thing):
		return None
		
		

#####################
### Gatherer
###
### Takes a list of target resources and gathers them one at a time.
### Will simply gather them in the order given.

class Gatherer(Agent):

	### targets: resources to be gathered
	### score: the number of resources gathered

	### Constructor
	def __init__(self, image, position, orientation, speed, world, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = Bullet):
		Agent.__init__(self, image, position, orientation, speed, world, hitpoints, firerate, bulletclass) 
		self.targets = []
		self.score = 0
	
	def setTargets(self, targets):
		self.targets = targets
	
	def addTarget(self, target):
		self.targets.append(target)
		
	def addToScore(self, points):
		self.score = self.score + points
		print "score", self.score


	def setNavigator(self, navigator):
		# Call the parent class, setting the navigator
		Agent.setNavigator(self, navigator)

		
	def doneMoving(self):
		if len(self.targets) > 0:
			current = self.targets[0]
			if distance(self.position, current) < self.getRadius()/2.0:
				# close enough, go to the next target
				self.targets.pop(0)
				if len(self.targets) > 0:
					self.navigateTo(self.targets[0])

	def start(self):
		Agent.start(self)
		if self.navigator != None and len(self.targets) > 0:
			self.navigateTo(self.targets[0])
			
	def collision(self, thing):
		Agent.collision(self, thing)
#		print "gatherer collision"
		if isinstance(thing, Resource):
			self.addToScore(1)



#####################
### Navigator

class Navigator(object):
	
	### Path: the planned path of nodes
	### World: a pointer to the world object
	### Agent: the agent doing the navigation
	### source: where starting from
	### destination: where trying to go
	
	
	def __init__(self):
		self.path = None
		self.world = None
		self.agent = None
		self.source = None
		self.destination = None

	
	def setAgent(self, agent):
		self.agent = agent
	
	def setPath(self, path):
		self.path = path

	def getSource(self):
		return self.source
	
	def getDestination(self):
		return self.destination
	
	def getPath(self):
		return self.path

	### Set the world object
	### self: the navigator object
	### world: the world object
	def setWorld(self, world):
		# Store the world object
		self.world = world
	
	
	### Callback from Agent. Agent has reached its move target and must determine what to do next.
	### If the path has been exhausted, the agent moves directly to the destination. Otherwise, it gets the next waypoint from the path.
	def doneMoving(self):
		# Check that the agent is valid
		if self.agent != None:
			# Check that the path is set
			if self.path != None:
				# If the path length is 0, then the path has been exhausted and it should be safe to move directly to the destination.
				if len(self.path) == 0:
					# Tell the agent to go to the destination
					self.agent.moveToTarget(self.destination)
					self.path = None
					self.source = None
					self.destination = None
				else:
					# Get the next waypoint and go there instead
					next = self.path.pop(0)
					self.agent.moveToTarget(next)
					self.checkpoint()

	### Called when the agent gets to a node in the path
	### self: the navigator object
	def checkpoint(self):
		return None
	
	### Callback from Agent. Agent has collided with something.
	def collision(self, thing):
		print "Collision"
	
	### This function gets called by the agent to figure out if some shortcuts can be taken when traversing the path.
	### This function should update the path and return True if the path was updated
	def smooth(self):
		return False
	
	### Finds the shortest path from the source to the destination. It should minimally set the path.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., its current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		# Check that the agent is valid
		if self.agent != None:
			# Just move straight to destination.
			self.source = source
			self.destination = dest
			self.agent.moveToTarget(dest)

	### Gets called after every agent.update()
	### self: the navigator object
	### delta: time passed since last update
	def update(self, delta):
		return None


#####################
### PathNetworkNavigator
###
### Abstract Navigator class that uses a network of path nodes.

class PathNetworkNavigator(Navigator):

	### pathnodes: the path nodes
	### pathnetwork: the edges between path nodes

	def __init__(self):
		Navigator.__init__(self)
		self.pathnodes = None
		self.pathnetwork = None

	def drawPathNetwork(self, surface):
		if self.pathnetwork is not None:
			for l in self.pathnetwork:
				pygame.draw.line(surface, (0, 0, 255), l[0], l[1], 1)

#####################
### NavMeshNavigator
###
### Abstract Navigator class that assumes the agent is traversing a path network created by a nav mesh.

class NavMeshNavigator(PathNetworkNavigator):
	
	### pathnodes: the path nodes
	### pathnetwork: the edges between path nodes
	### navmesh: the polygons making up the nav mesh
	
	def __init__(self):
		PathNetworkNavigator.__init__(self)
		self.navmesh = None
	
	### Set the world object
	### self: the navigator object
	### world: the world object
	def setWorld(self, world):
		Navigator.setWorld(self, world)
		# Create the path network
		self.createPathNetwork(world)
		# Draw the world
		self.drawNavMesh(self.world.debug)
		self.drawPathNetwork(self.world.debug)
	
	### Create the path node network and pre-compute all shortest paths along the network
	### self: the navigator object
	### world: the world object
	def createPathNetwork(self, world):
		return None

	def drawNavMesh(self, surface):
		if self.navmesh is not None:
			for p in self.navmesh:
				drawPolygon(p, surface, (0, 255, 0), 1, False)



#####################
### Blocker
###
### A thing that prevents Agent movement
### I don't know how to make a class with nothing in it, so I made a dummy constructor

class Blocker:
	pass
		

#####################
### Obstacle


class Obstacle(Thing, Blocker):

	### Note: the points are sorted in order of increasing angle around a central point.

	### points: points of the polygon relative to center
	### pos: center of polygon
	### lines: lines of polygon relative to center
	### surface: the surface
	### rect: the rectangle of the surface
	
	def __init__(self):
		self.points = []
		self.pos = [0, 0]
		self.lines = []
		self.surface = None
		self.rect = None
		
	### Draw me
	def draw(self, parent):
		if self.surface != None:
			parent.blit(self.surface, self.pos)
		return None
		
	### Returns the lines with the obstacle offset
	def getLines(self):
		#lines = map(lambda l: ([m + n for m,n in zip(l[0], self.pos)], [m + n for m,n in zip(l[1], self.pos)]), self.lines)
		#return [tuple(i) for i in lines]
		return self.lines


	### Returns the points with the obstacle offset
	def getPoints(self):
		#points = map(lambda p: [m + n for m,n in zip(p, self.pos)], self.points)
		#return [tuple(i) for i in points]
		return self.points

	### Is a point one of the obstacle points?
	def isInPoints(self, point):
		return point in self.getPoints()
		
	def twoAdjacentPoints(self, p1, p2):
		if self.isInPoints(p1) and self.isInPoints(p2):
			return (abs(self.points.index(p1) - self.points.index(p2)) == 1) or (p1 == self.points[0] and p2 == self.points[len(self.points)-1]) or (p2 == self.points[0] and p1 == self.points[len(self.points)-1])
		else:
			return False
			
	def pointInside(self, point):
		return pointInsidePolygonLines(point, self.lines)

######################
### Decoration

class Decoration(pygame.sprite.Sprite):

	def __init__(self, image, position, orientation = 0):
		pygame.sprite.Sprite.__init__(self) # call sprite initializer
		self.image, self.rect = load_image(image, -1)
		## Translate to initial position
		self.rect = self.rect.move(position)
		rot_img = pygame.transform.rotate(self.image, orientation)
		img_rect = rot_img.get_rect()
		img_rect.center = self.rect.center
		self.image = rot_img
		self.rect = img_rect
		


#####################
### RandomObstacle
###
### NOTE: Doesn't work with my APSP code


class RandomObstacle(Obstacle):

	def __init__(self, num, pos, radius, sigma, min, color = (0, 0, 0), linewidth = 4):
		Obstacle.__init__(self)
		self.pos = pos
		points = []
		sphericals = []
		# Generate a number of points in spherical coordinates
		for x in xrange(num):
			rad = x*(2*numpy.pi/num)
			dist = corerandom.gauss(radius/2, sigma/2) #random.randint(0,radius)
			if dist < min:
				dist = min
			if dist > radius:
				dist = radius
#			print "dist", dist
			sphericals.append((rad, dist))
		# Convert to Cartesian coordinates
		for (rad, dist) in sphericals:
			points.append(((int(math.cos(rad)*dist)+radius), int((math.sin(rad)*dist)+radius)))
		# Create surface
		s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA, 32)
		s = s.convert_alpha()
		# Draw polygon on surface
		pygame.draw.lines(s, color, True, points, linewidth)
		# translate points to absolute space
		transpoints = []
		for p in points:
			transpoints.append((p[0] + self.pos[0], p[1] + self.pos[1]))
		# Make lines
		lines = []
		p_last = None
		for p in transpoints:
			if p_last != None:
				lines.append((p_last, p))
			p_last = p
		lines.append((transpoints[len(transpoints)-1], transpoints[0]))
		# Store some stuff
		self.rect = s.get_rect()
		self.surface = s
		self.lines = lines
		self.points = transpoints
#		print "points", self.points
		
		
#
		
		
############################
### ManualObstacle
		
class ManualObstacle(Obstacle):

	### Note: the points are sorted in order of increasing angle around a central point.

	### points: points of the polygon relative to center
	### pos: center of polygon
	### lines: lines of polygon relative to center
	### surface: the surface
	### rect: the rectangle of the surface
	### sprites: the sprite group for all decorations (redundant with self.decorations, but just easier this way)
	### decorations: the decorations
		
	### Constructor
	# pos = center point of polygon
	# Points must be in clockwise or counterclockwise order, and relative to (0,0)
	# color = line color
	# linewidth = width of the lines
	def __init__(self, points, color = (0, 0, 0), linewidth = 4, sprite = None):
		Obstacle.__init__(self)
		minpt = ( min(map(lambda p: p[0], points)), min(map(lambda p: p[1], points)) )
		maxpt = ( max(map(lambda p: p[0], points)), max(map(lambda p: p[1], points)) )
		# create surface
		s = pygame.Surface((maxpt[0]+linewidth, maxpt[1]+linewidth), pygame.SRCALPHA, 32)
		s = s.convert_alpha()
		pygame.draw.lines(s, color, True, points, linewidth)
		self.surface = s
		self.rect = s.get_rect()
		#transpoints = []
		#for p in points:
		#	transpoints.append((p[0] + self.pos[0], p[1] + self.pos[1]))
		#self.points = transpoints
		self.points = points
		# compute lines
		lines = []
		last = None
		for p in points:
			if last != None:
				lines.append((last, p))
			last = p
		lines.append((points[len(points)-1], points[0]))
		self.lines = lines
		# Decorations
		self.decorations = []
		self.sprites = pygame.sprite.RenderPlain()
		if sprite is not None:
			dec = Decoration(sprite, (0, 0))
			pos = (0, 0)
			for x in xrange((self.rect.width*2)/dec.rect.width):
				for y in xrange((self.rect.height*2)/dec.rect.height):
					pos = (((x/2)*dec.rect.width)+corerandom.uniform(0, dec.rect.width/5.0), ((y/2)*dec.rect.height)+corerandom.uniform(0, dec.rect.height/5.0))
					orient = corerandom.uniform(0, 360.0)
					if pointInsidePolygonPoints((pos[0]+dec.rect.width/2.0, pos[1]+dec.rect.height/2.0), points):
						d = Decoration(sprite, pos, orient)
						self.decorations.append(d)
						self.sprites.add(d)

	### Draw me
	def draw(self, parent):
		Obstacle.draw(self, parent)
		self.sprites.draw(self.surface)

############################
### GameWorld

class GameWorld():

	### screen: the screen
	### background: the background surface
	### agent: the player agent
	### obstacles: obstacles
	### sprites: all sprites (player and NPCs)
	### npcs: the NPC agents
	### dimensions: the size of the world (width, height)
	### points: all the points of obstacles, plus screen corners
	### lines: all the points of obstacles, plus screen edges
	### bullets: all the bullets active
	### resources: all the resources
	### movers: all things that can collide with other things and implement collision()
	### destinations: places that are not inside of obstacles. 
	### clock: elapsed time in game

	def __init__(self, seed, worlddimensions, screendimensions):
		#initialize random seed
		self.time = time.time()
		corerandom.seed(seed or self.time)
		random.seed(self.time)
		#initialize Pygame and set up screen and background surface
		pygame.init()
		self.font = pygame.font.SysFont("monospace", 15)
		screen = pygame.display.set_mode(screendimensions)
		# Background surface that will hold everything
#		background = pygame.Surface(screen.get_size())
		background = pygame.Surface(worlddimensions)
		background = background.convert()
		background.fill((255, 255, 255))
		# Debug surface
		debug = pygame.Surface(worlddimensions)
		debug = debug.convert()
		debug.fill((255, 255, 255))
		background.blit(debug, (0, 0))
		screen.blit(background, (0, 0))
		pygame.display.flip()
		#store stuff
		self.screen = screen
		self.seed = seed or self.time
		self.background = background
		self.debug = debug
		self.obstacles = None
		self.sprites = None
		self.agent = None
		self.npcs = []
		self.dimensions = worlddimensions
		self.points = None 
		self.lines = None 
		self.bullets = []
		self.resources = []
		self.debugging = False
		self.movers = []
		self.clock = 0
		# camera
		self.camera = [0, 0]
		# unobstructed places
		self.destinations = {}
	
	def getPoints(self):
		return self.points
	
	def getLines(self):
		return self.lines
	
	def getLinesWithoutBorders(self):
		corners = [(0, 0), (self.dimensions[0], 0), (self.dimensions[0], self.dimensions[1]), (0, self.dimensions[1])]
		lines = []
		for l in self.getLines():
			if not (l[0] in corners and l[1] in corners):
				lines.append(l)
		return lines

	
	def getObstacles(self):
		return self.obstacles
	
	def getDimensions(self):
		return self.dimensions
		
	def setPlayerAgent(self, agent):
		self.agent = agent
		self.camera = agent.getLocation()
		self.movers.append(agent)
#		print agent.radius

	# Make Random Terrain
	def initializeRandomTerrain(self, num, onum, radius, sigma, min):
		obstacles = []
		points = [(0, 0), (self.dimensions[0], 0), (self.dimensions[0], self.dimensions[1]), (0, self.dimensions[1])]
		lines = [((0, 0), (self.dimensions[0], 0)), ((self.dimensions[0], 0), (self.dimensions[0], self.dimensions[1])), ((self.dimensions[0], self.dimensions[1]), (0, self.dimensions[1])), ((0, self.dimensions[1]), (0,0))]
		for _ in xrange(num):
			pos = [0, 0]
			for _ in xrange(100):
				pos = [corerandom.randint(0,self.dimensions[0]-radius), corerandom.randint(0,self.dimensions[1]-radius)]
				tooclose = False
				for o in obstacles:
					if distance(pos, o.pos) < radius*2:
						tooclose = True
				if tooclose == False:
					break
			o = RandomObstacle(onum, pos, radius, sigma, min)
			obstacles.append(o)
			points = points + o.getPoints()
			lines = lines + o.getLines()
		self.obstacles = obstacles
		self.points = points
		self.lines = lines 
		
	# Make Terrain
	# polys = list of list points (poly1, poly2, ...) = ((p11, p12, ...), (p21, p22, ...), ...)
	def initializeTerrain(self, polys, color = (0, 0, 0), linewidth = 4, sprite = None):
		obstacles = []
		points = [(0, 0), (self.dimensions[0], 0), (self.dimensions[0], self.dimensions[1]), (0, self.dimensions[1])]
		lines = [((0, 0), (self.dimensions[0], 0)), ((self.dimensions[0], 0), (self.dimensions[0], self.dimensions[1])), ((self.dimensions[0], self.dimensions[1]), (0, self.dimensions[1])), ((0, self.dimensions[1]), (0,0))]
		for poly in polys:
			#minpt = (min(map(lambda p: p[0], poly)), min(map(lambda p: p[1], poly)))
			#maxpt = (max(map(lambda p: p[0], poly)), max(map(lambda p: p[1], poly)))
			#center = [ (sum(map(lambda p: p[0], poly))/float(len(poly)))-((maxpt[0]-minpt[0])/2.0), (sum(map(lambda p: p[1], poly))/float(len(poly)))-((maxpt[1]-minpt[1])/2.0) ]
			#newpoly = map(lambda pt: (pt[0] - minpt[0], pt[1] - minpt[1]), poly)
			o = ManualObstacle(poly, color, linewidth, sprite)
			points = points + o.getPoints()
			lines = lines + o.getLines()
			obstacles.append(o)
		self.obstacles = obstacles
		self.points = points
		self.lines = lines


	def initializeResources(self, points, resource = RESOURCE):
		for point in points:
			r = SimpleResource(resource, point, 0, self)
			self.addResource(r)
	

	def initializeRandomResources(self, num, resource = RESOURCE):
		for _ in xrange(num):
			pos = (0, 0)
			while True:
				pos = (corerandom.randint(0, self.dimensions[0]), corerandom.randint(0, self.dimensions[1]))
				inside = False
				for o in self.obstacles:
					if pointInsidePolygonPoints(pos, o.getPoints()):
						inside = True
				if inside == False:
					break
			r = SimpleResource(resource, pos, 0, self)
			self.addResource(r)
#			self.resources.add(r)
#			self.movers.add(r)

	def run(self):
		self.sprites = pygame.sprite.RenderPlain((self.agent))
#		for r in self.resources:
#			self.sprites.add(r)
#		for n in self.npcs:
#			self.sprites.add(n)
		for m in self.movers:
			self.sprites.add(m)
		clock = pygame.time.Clock()
		
		# Draw obstacles. Only need to do this once
		for o in self.obstacles:
			o.draw(self.background)

		while True:
			clock.tick(TICK)
			delta = clock.get_rawtime()
			self.handleEvents()
			self.update(delta)
			self.sprites.update(delta) 
			#print "obstacles"
			#for o in self.obstacles:
			#	print o.pos
			#	o.pos[0] = o.pos[0] + 1.0
			#	o.pos[1] = o.pos[1] + 1.0
			self.drawWorld()
			pygame.display.flip()
			
	def drawWorld(self):
		#self.screen.blit(self.background, (0, 0))
		offsetX = self.camera[0] - self.agent.rect.center[0]
		offsetY = self.camera[1] - self.agent.rect.center[1]
		self.screen.fill((255, 255, 255))
		self.screen.blit(self.background, [offsetX, offsetY])
		if self.debugging:
			self.background.blit(self.debug, (0, 0))
		self.sprites.draw(self.background)
		for o in self.obstacles:
			o.draw(self.background)
		self.drawMousePosition()
		#pygame.display.flip()

	def drawMousePosition(self):
		offsetX, offsetY = self.getWorldMousePosition()
		offsetX = int(round(offsetX))
		offsetY = int(round(offsetY))
		label = self.font.render("Mouse: " + str(offsetX) + "," + str(offsetY), True, (255, 0, 0))
		textPosition = (10, 10)
		self.screen.blit(label, textPosition)
		
	def handleEvents(self): 
		events = pygame.event.get()
		for event in events:
			if event.type == QUIT:
				sys.exit(0) 
			elif event.type == MOUSEBUTTONUP:
				self.doMouseUp()
			elif event.type == KEYDOWN:
				self.doKeyDown(event.key)
				
	def doMouseUp(self):
		offsetX, offsetY = self.getWorldMousePosition()
		self.agent.navigateTo([offsetX, offsetY])

	def getWorldMousePosition(self):
		pos = pygame.mouse.get_pos()
		offsetX = pos[0] + self.agent.position[0] - self.camera[0]
		offsetY = pos[1] + self.agent.position[1] - self.camera[1]
		return offsetX, offsetY
		

	def doKeyDown(self, key):
		if key == 32: #space
			self.agent.shoot()
		elif key == 100: #d
			print "distance traveled", self.agent.distanceTraveled

	def worldCollisionTest(self):
		collisions = []
		for m1 in self.movers:
			if m1 in self.movers:
				# Collision against world boundaries
				if m1.position[0] < 0 or m1.position[0] > self.dimensions[0] or m1.position[1] < 0 or m1.position[1] > self.dimensions[1]:
					collisions.append((m1, self))
				# Collision against obstacles
				for o in self.obstacles:
					c = False
					needCheckVertex = False
					if isinstance(m1, Agent) and m1.moveTarget != None:
						moverRadius = m1.getRadius()
						lines = o.getLines()
						direction = numpy.subtract(m1.moveTarget, m1.position)
						magnitude = numpy.linalg.norm(direction)
						if magnitude > 0:
							direction = direction / magnitude
						nextPosition = tuple(numpy.add(m1.position, direction * (m1.speed[0] + moverRadius)))
						p = rayTraceWorldNoEndPoints(m1.position, nextPosition, lines)
						if p == None:
							needCheckVertex = True
					if needCheckVertex:
						for v in o.getPoints():
							# check v between m1.position and nextPosition
							if between(v[0], m1.position[0], nextPosition[0]) and between(v[1], m1.position[1], nextPosition[1]):
								d = minimumDistance((m1.position, nextPosition), v)
								if d < moverRadius:
									needCheckVertex = False
									break
						if needCheckVertex:
							for l in lines:
								if minimumDistance(l, nextPosition) < moverRadius:
									needCheckVertex = False
									break
					if not needCheckVertex:
						for l in o.getLines():
							for r in ((m1.rect.topleft, m1.rect.topright), (m1.rect.topright, m1.rect.bottomright), (m1.rect.bottomright, m1.rect.bottomleft), (m1.rect.bottomleft, m1.rect.topleft)):
								hit = calculateIntersectPoint(l[0], l[1], r[0], r[1])
								if hit is not None:
									c = True
					if c:
						collisions.append((m1, o))
				# Movers against movers
				for m2 in self.movers:
					if m2 in self.movers:
						if m1 != m2:
							if (m1, m2) not in collisions and (m2, m1) not in collisions:
								if m1.rect.colliderect(m2.rect):
									collisions.append((m1, m2))
		for c in collisions:
			c[0].collision(c[1])
			c[1].collision(c[0])
		
	def update(self, delta):
		self.clock = self.clock + delta
		self.worldCollisionTest()
		return None
		
	def collision(self, thing):
		return None
		
	def getLines(self):
		return self.lines[:]

	def getPoints(self):
		return self.points[:]
		
	def addBullet(self, bullet):
		self.bullets.append(bullet)
		if self.sprites is not None:
			self.sprites.add(bullet)
		self.movers.append(bullet)
		
	def deleteBullet(self, bullet):
		if bullet in self.bullets:
			self.bullets.remove(bullet)
			if self.sprites is not None:
				self.sprites.remove(bullet)
			self.movers.remove(bullet)

	def addResource(self, res):
		self.resources.append(res)
		if self.sprites is not None:
			self.sprites.add(res)
		self.movers.append(res)
	
	def deleteResource(self, res):
		self.resources.remove(res)
		if self.sprites is not None:
			self.sprites.remove(res)
		self.movers.remove(res)
		
	def addNPC(self, npc):
		self.npcs.append(npc)
		if self.sprites is not None:
			self.sprites.add(npc)
		self.movers.append(npc)
		
	def deleteNPC(self, npc):
		if npc in self.npcs:
			self.npcs.remove(npc)
			if self.sprites is not None:
				self.sprites.remove(npc)
			self.movers.remove(npc)

	def getVisible(self, position, orientation, viewangle, type = None):
		visible = []
		for m in self.movers:
			if type == None or isinstance(m, type):
				# m is the type that we are looking for
				other = m.getLocation()
				if other != position:
					# other is not me
					if viewangle < 360:
						# viewangle less than 360
						orient = (math.cos(math.radians(orientation)), -math.sin(math.radians(orientation)))
						vect = (other[0]-position[0], other[1]-position[1])
						x = dotProduct(orient, vect) / (vectorMagnitude(orient) * vectorMagnitude(vect))
						if x >= 1.0:
							angle = 0.0
						else:
							angle = math.degrees(math.acos(x))
						if angle < viewangle/2.0:
							hit = rayTraceWorld(position, other, self.getLines())
							if hit == None:
								visible.append(m)
					else:
						# viewangle is 360
						hit = rayTraceWorld(position, other, self.getLines())
						if hit == None:
							visible.append(m)
		return visible

	def computeFreeLocations(self, agent):
		if type(agent) not in self.destinations:
			destinations = []
			grid = agent.getRadius()*2.0
			for x in xrange(1, int(self.dimensions[0]/grid)):
				for y in xrange(1, int(self.dimensions[1]/grid)):
					point = (x*grid, y*grid)
					if isGood(point, self, grid):
						destinations.append(point)
			self.destinations[type(agent)] = destinations
		
	def getFreeLocations(self, agent):
		if type(agent) in self.destinations:
			return self.destinations[type(agent)]
		else:
			return None
					
	def getNPCs(self):
		return self.npcs

	def getAgent(self):
		return self.agent

	def getBullets(self):
		return self.bullets

############################
### GATE

class Gate(Thing, Blocker):

	def __init__(self, p1, p2, sprite, world):
		self.line = (p1, p2)
		self.sprites = pygame.sprite.RenderPlain()
		self.decorations = []
		#self.active = active
		dec = Decoration(sprite, (0, 0)) # throw away
		size = max(dec.rect.height, dec.rect.width)
		floatLength = distance(p1, p2)
		length = int(floatLength)
		dims = range(len(p1))
		# Create evenly spaced decorations along the gate line.
		offset = tuple(p2[i] - p1[i] for i in dims)
		normOffset = tuple(offset[i] / floatLength for i in dims)
		lineStart = tuple(p1[i] + normOffset[i] * size / 2.0 for i in dims)
		numDecorations = length/size
		for t in xrange(numDecorations):
			pos = tuple((lineStart[i] + float(t) / numDecorations * offset[i]) - size / 2.0 for i in dims)
			d = Decoration(sprite, pos, 0)
			self.decorations.append(d)
			self.sprites.add(d)

	def getLine(self):
		return self.line
	
	def draw(self, parent):
		self.sprites.draw(parent)
			
	def isColliding(self, rect):
		for d in self.decorations:
			if d.rect.colliderect(rect):
				return True
		return False

def getGateLine(gate):
	return gate.getLine()

############################
### GatedWorld
			
class GatedWorld(GameWorld):

	### Gates: lines (p1, p2) where gates can appear
	### timer: running timer
	### alarm: when timer is greater than this number, gate switches
	### gate: the active gate

	def __init__(self, seed, worlddimensions, screendimensions, numgates, alarm):
		GameWorld.__init__(self, seed, worlddimensions, screendimensions)
		self.potentialGates = []
		self.timer = 0
		self.alarm = alarm
		self.gates = []
		self.numGates = numgates
	
	def getNumGates(self):
		return self.numGates
	
	def getGates(self):
		return map(getGateLine, self.gates)
	
	def makePotentialGates(self):
		if self.obstacles != None:
			dangerpoints = [(0, 0), (self.dimensions[0], 0), (self.dimensions[0], self.dimensions[1]), (0, self.dimensions[1])]
			for p1 in self.getPoints():
				for p2 in self.getPoints():
					if p1 != p2: # and p2 != (0, 0) and p2 != (self.dimensions[0], 0) and p2 != (self.dimensions[0], self.dimensions[1]) and p2 != (0, self.dimensions[1]):
						if (p1 not in dangerpoints) or (p2 not in dangerpoints):
							samepoly = False
							for o in self.obstacles:
								if p1 in o.getPoints() and p2 in o.getPoints():
									samepoly = True
							if samepoly == False:
								if not insideObstacle(((p1[0]+p2[0])/2.0, (p1[1]+p2[1])/2.0), self.obstacles):
									
									hit = rayTraceWorldNoEndPoints(p1, p2, self.getLines())
									if hit == None:
										self.potentialGates.append((p1, p2))

	def drawWorld(self):
		GameWorld.drawWorld(self)
		for g in self.gates:
			g.draw(self.background)
			

	def worldCollisionTest(self):
		GameWorld.worldCollisionTest(self)
		for g in self.gates:
			for m in self.movers:
				if g.isColliding(m.rect):
					m.collision(g)
					g.collision(m)
				

	def update(self, delta):
		GameWorld.update(self, delta)
		self.timer = self.timer + 1
		if self.timer > self.alarm:
			self.timer = 0
			if len(self.potentialGates) > 0:
				newgates = []
				for x in xrange(self.numGates):
					r = corerandom.randint(0, len(self.potentialGates)-1)
					line = self.potentialGates[r]
					tooclose = False
					for m in self.movers:
						if minimumDistance(line, m.getLocation()) < m.getRadius()*4.0:
							tooclose = True
							break
					if tooclose == False:
						g = Gate(line[0], line[1], GATE, self)
						newgates.append(g)
					elif len(self.gates) > x:
						newgates.append(self.gates[x])
				self.gates = newgates
		return None


		
	### NOTE: really should get the bounding box and return the lines of the bounding box
	def getLines(self):
		lines = GameWorld.getLines(self)
		for g in self.gates:
			lines.append(g.line)
		return lines

	def doKeyDown(self, key):
		GameWorld.doKeyDown(self, key)
		if key == 103: #'g'
			offsetX, offsetY = self.getWorldMousePosition()
			self.addGateAtNearest((offsetX, offsetY))

	def drawPotentialGates(self):
		for g in self.potentialGates:
			pygame.draw.line(self.debug, (225, 225, 225), g[0], g[1], 1)


	def addGateAtNearest(self, point):
		if len(self.potentialGates) > 0 and self.numGates > 0:
			bestGate = None
			bestDist = 0
			for cur in self.potentialGates:
				d = minimumDistance(cur, point)
				if bestGate is None or d < bestDist:
					bestGate = cur
					bestDist = d
			g = Gate(bestGate[0], bestGate[1], GATE, self)
			self.gates.append(g)
			if len(self.gates) > self.numGates:
				self.gates.pop(0)

#######################################
### HELPERS
	

def insideObstacle(point, obstacles):
	for o in obstacles:
		if pointInsidePolygonPoints(point, o.getPoints()):
			return True
	return False		
				
def isGood(point, world, threshold):
	if point[0] > 0 and point[0] < world.dimensions[0] and point[1] > 0 and point[1] < world.dimensions[1]:
		for o in world.obstacles:
			if pointInsidePolygonPoints(point, o.getPoints()):
				return False
		for l in world.getLines():
			if minimumDistance(l, point) < threshold:
				return False
		return True
	return False

