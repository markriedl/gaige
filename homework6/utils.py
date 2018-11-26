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


########################
### PYGAME STUFF

def load_image(name, colorkey=None):
  image = pygame.image.load(name)
  image = image.convert()
  if colorkey is not None:
    if colorkey is -1:
      colorkey = image.get_at((0,0))
    image.set_colorkey(colorkey, RLEACCEL)
  return image, image.get_rect()


############################
### OTHER STUFF

### Distance between two points
def distance(p1, p2):
	return (((p2[0]-p1[0])**2) + ((p2[1]-p1[1])**2))**0.5
  
# Calc the gradient 'm' of a line between p1 and p2
def calculateGradient(p1, p2):
  
	# Ensure that the line is not vertical
	if (p1[0] != p2[0]):
		m = (p1[1] - p2[1]) / float(p1[0] - p2[0])
		return m
	else:
		return None
 
# Calc the point 'b' where line crosses the Y axis
def calculateYAxisIntersect(p, m):
	return  p[1] - (m * p[0])
 
# Calc the point where two infinitely long lines (p1 to p2 and p3 to p4) intersect.
# Handle parallel lines and vertical lines (the later has infinite 'm').
# Returns a point tuple of points like this ((x,y),...) or None
# In non parallel cases the tuple will contain just one point.
# For parallel lines that lay on top of one another the tuple will contain
# all four points of the two lines
def getIntersectPoint(p1, p2, p3, p4):
	m1 = calculateGradient(p1, p2)
	m2 = calculateGradient(p3, p4)
      
	# See if the the lines are parallel
	if (m1 != m2):
		# Not parallel
      
		# See if either line is vertical
		if (m1 is not None and m2 is not None):
			# Neither line vertical           
			b1 = calculateYAxisIntersect(p1, m1)
			b2 = calculateYAxisIntersect(p3, m2)  
			x = (b2 - b1) / float(m1 - m2)       
			y = (m1 * x) + b1           
		else:
			# Line 1 is vertical so use line 2's values
			if (m1 is None):
				b2 = calculateYAxisIntersect(p3, m2)   
				x = p1[0]
				y = (m2 * x) + b2
			# Line 2 is vertical so use line 1's values               
			elif (m2 is None):
				b1 = calculateYAxisIntersect(p1, m1)
				x = p3[0]
				y = (m1 * x) + b1           
			else:
				assert false
              
		return ((x,y),)
	else:
		# Parallel lines with same 'b' value must be the same line so they intersect
		# everywhere. In this case we return the start and end points of both lines
		# the calculateIntersectPoint method will sort out which of these points
		# lays on both line segments
		b1, b2 = None, None # vertical lines have no b value
		if m1 is not None:
			b1 = calculateYAxisIntersect(p1, m1)
          
		if m2 is not None:   
			b2 = calculateYAxisIntersect(p3, m2)
      
		# If these parallel lines lay on one another   
		if b1 == b2:
			return p1,p2,p3,p4
		else:
			return None  
  
  
 
# For line segments (i.e., not infinitely long lines) the intersect point
# may not lay on both lines.
#   
# If the point where two lines intersect is inside both lines' bounding
# rectangles then the lines intersect. Returns intersect point if the line
# intersects or None if not
def calculateIntersectPoint(p1, p2, p3, p4):
	p = getIntersectPoint(p1, p2, p3, p4)
	if p is not None:
		p = p[0]
		if between(p[0], p1[0], p2[0]) and between(p[1], p1[1], p2[1]) and between(p[0], p3[0], p4[0]) and between(p[1], p3[1], p4[1]):
			return p
	return None

# Checks if the first number is between the other two numbers.
# Also returns true if all numbers are very close together to the point where they are essentially equal
# (i.e., floating point approximation).
def between(p, p1, p2):
	return p + EPSILON >= min(p1, p2) and p - EPSILON <= max(p1, p2)

# Checks if two numbers are very close to the same value (i.e., floating point approximation).
def almostEqualNumbers(n1, n2):
	return abs(n1 - n2) < EPSILON

# Checks if two points are very close to the same value (i.e., floating point approximation).
def almostEqualPoints(p1, p2):
	return almostEqualNumbers(p1[0], p2[0]) and almostEqualNumbers(p1[1], p2[1])


def rayTrace(p1, p2, line):
	return calculateIntersectPoint(line[0], line[1], p1, p2)
	#pygame.draw.line(background, (0, 0, 0), p1, p2)
	
def rayTraceWorld(p1, p2, worldLines):
	for l in worldLines:
		hit = rayTrace(p1, p2, l)
		if hit != None:
			return hit
	return None

# Check whether the line between p1 and p2 intersects with line anywhere except an endpoint.
def rayTraceNoEndpoints(p1, p2, line):
	# They are the same line: bad
	if (p1 == line[0] and p2 == line[1]) or (p2 == line[0] and p1 == line[1]):
		return p1
	# They are not the same line but share an endpoint: good
	if (p1 == line[0] or p2 == line[1]) or (p2 == line[0] or p1 == line[1]):
		return None
	# They do not share any points
	hitpoint = calculateIntersectPoint(line[0], line[1], p1, p2)
	if hitpoint != None:
		return hitpoint
	return None

# Check whether the line between p1 and p2 intersects any line anywhere except an endpoint of any of the lines.
def rayTraceWorldNoEndPoints(p1, p2, worldLines):
	for l in worldLines:
		hit = rayTraceNoEndpoints(p1, p2, l)
		if hit != None:
			return hit
	return None


# Return minimum distance between line segment and point
def minimumDistance(line, point):
	d2 = distance(line[1], line[0])**2.0
	if d2 == 0.0: 
		return distance(point, line[0])
	# Consider the line extending the segment, parameterized as line[0] + t (line[1] - line[0]).
	# We find projection of point p onto the line. 
	# It falls where t = [(point-line[0]) . (line[1]-line[0])] / |line[1]-line[0]|^2
	p1 = (point[0] - line[0][0], point[1] - line[0][1])
	p2 = (line[1][0] - line[0][0], line[1][1] - line[0][1])
	t = dotProduct(p1, p2) / d2  # numpy.dot(p1, p2) / d2
	if t < 0.0: 
		return distance(point, line[0])	# Beyond the line[0] end of the segment
	elif t > 1.0: 
		return distance(point, line[1])	# Beyond the line[1] end of the segment
	p3 = (line[0][0] + (t * (line[1][0] - line[0][0])), line[0][1] + (t * (line[1][1] - line[0][1]))) # projection falls on the segment
	return distance(point, p3)


#Polygon is a set of points
def pointOnPolygon(point, polygon):
	last = None
	threshold = EPSILON
	for p in polygon:
		if last != None and minimumDistance((last, p), point) < threshold:
			return True
		last = p
	return minimumDistance((polygon[0], polygon[len(polygon) - 1]), point) < threshold

def withinRange(p1, p2, range):
	return distance(p1, p2) <= range

def withinRangeOfPoints(point, range, list):
	for pt in list:
		if withinRange(point, pt, range):
			return True
	return False

def drawPolygon(poly, screen, color = (0, 0, 0), width = 1, center = False):
	last = None
	for p in poly:
		if last != None:
			pygame.draw.line(screen, color, last, p, width)
		last = p
	pygame.draw.line(screen, color, poly[0], poly[len(poly)-1], width)
	if center:
		c = ( sum(map(lambda p: p[0], poly))/float(len(poly)), sum(map(lambda p: p[1], poly))/float(len(poly)) )
		pygame.draw.line(screen, color, (c[0]-2, c[1]-2), (c[0]+2, c[1]+2), 1)
		pygame.draw.line(screen, color, (c[0]+2, c[1]-2), (c[0]-2, c[1]+2), 1)

def commonPoints(poly1, poly2):
	#if two triangles share 2 points, they are adjacent
	points = []
	for p1 in poly1:
		for p2 in poly2:
			if p1 == p2:
				points.append(p1)
	return points

def polygonsAdjacent(poly1, poly2):
	points = commonPoints(poly1, poly2)
	if len(points) >= 2:
		isAdjacent = False
		for i, point in enumerate(points[:-1]):
			nextPoint = points[i + 1]
			point1Index = poly1.index(point)
			if poly1[(point1Index + 1) % len(poly1)] == nextPoint or poly1[point1Index - 1] == nextPoint:
				point2Index = poly2.index(point)
				if poly2[(point2Index + 1) % len(poly2)] == nextPoint or poly2[point2Index - 1] == nextPoint:
					isAdjacent = True
					break
		if isAdjacent:
			return points
	return False
		
def isConvex(points):
	p1 = None
	p2 = None
	negpos = 0
	for p3 in points:
		if p1 != None and p2 != None:
			#cross product must always be the same sign
			zcross = crossProduct(p1, p2, p3)
			if negpos == 0:
				if zcross >= 0:
					negpos = 1
				else:
					negpos = -1
			elif negpos >= 0 and zcross < 0:
				return False
			elif negpos < 0 and zcross > 0:
				return False
		p1 = p2
		p2 = p3
	#Do the last check
	zcross = crossProduct(points[len(points)-2], points[len(points)-1], points[0])
	if negpos >= 0 and zcross < 0:
		return False
	elif negpos < 0 and zcross > 0:
		return False
	zcross = crossProduct(points[len(points)-1], points[0], points[1])
	if negpos >= 0 and zcross < 0:
		return False
	elif negpos < 0 and zcross > 0:
		return False
	else:
		return True
	
def crossProduct(p1, p2, p3):
	dx1 = p2[0] - p1[0]
	dy1 = p2[1] - p1[1]
	dx2 = p3[0] - p2[0]
	dy2 = p3[1] - p2[1]
	return (dx1*dy2) - (dy1*dx2)
	
def dotProduct(p1, p2):
	return (p1[0]*p2[0]) + (p1[1]*p2[1])


#Special routine for appending a line to a list of lines, making sure there are no duplicates added. Changes made by side-effect.
def appendLineNoDuplicates(line, lines):
	if (line in lines) == False and (reverseLine(line) in lines) == False:
		lines.append(line)
		return False
	else:
		return True
	
#Reverse the order of points in a line.	
def reverseLine(line):
	return (line[1], line[0])
	
#Determine whether a point is inside an simple polygon. Polygon is a set of lines.
def pointInsidePolygonLines(point, polygon):
	count = 0
	intersectEndPoints = {}
	for l in polygon:
		outsidePoint = (-10, SCREEN[1]/2.0)
		result = rayTrace(point, outsidePoint, l)
		if result != None:
			if almostEqualPoints(result, point):
				return True

			# Handles an edge case where the testing line touches the same endpoint of two lines.
			matchingPoint = None
			if almostEqualPoints(result, l[0]):
				matchingPoint = (l[0], l[1])
			elif almostEqualPoints(result, l[1]):
				matchingPoint = (l[1], l[0])
			if matchingPoint is not None:
				if matchingPoint[0] in intersectEndPoints:
					# Check whether the point is tangent or intersecting the polygon at this matching point
					# by checking the intersection of the line segment formed by the other endpoints of the two polygon line segments.
					if calculateIntersectPoint(point, outsidePoint, intersectEndPoints[matchingPoint[0]], matchingPoint[1]) is not None:
						continue
				else:
					intersectEndPoints[matchingPoint[0]] = matchingPoint[1]
			count = count + 1
	return count%2 == 1

#Determine whether a point is inside an simple polygon. Polygon is a set of points.
def pointInsidePolygonPoints(point, polygon):
	lines = []
	last = None
	for p in polygon:
		if last != None:
			lines.append((last, p))
		last = p
	lines.append((polygon[len(polygon)-1], polygon[0]))
	return pointInsidePolygonLines(point, lines)

# Angle between two lines originating at (0, 0). Length of lines must be greater than 0.
def angle(pt1, pt2):
	x1, y1 = pt1
	x2, y2 = pt2
	inner_product = x1*x2 + y1*y2
	len1 = math.hypot(x1, y1)
	len2 = math.hypot(x2, y2)
	return math.acos(inner_product/(len1*len2))

def vectorMagnitude(v):
	return reduce(lambda x, y: (x**2)+(y**2), v)**0.5
	
# Find the point in nodes closest to p that is unobstructed
# NOTE: there is a problem in that this function doesn't compute whether there is enough clearance for an agent to get to the nearest unobstructed point
def findClosestUnobstructed(p, nodes, worldLines):
	best = None
	dist = INFINITY
	for n in nodes:
		if rayTraceWorld(p, n, worldLines) == None:
			d = distance(p, n)
			if best == None or d < dist:
				best = n
				dist = d
	return best
	
def drawCross(surface, point, color = (0, 0, 0), size = 2, width = 1):
	pygame.draw.line(surface, color, (point[0]-size, point[1]-size), (point[0]+size, point[1]+size), width)
	pygame.draw.line(surface, color, (point[0]+size, point[1]-size), (point[0]-size, point[1]+size), width)
