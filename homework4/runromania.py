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

import sys, math, numpy, random, time, copy
from astarnavigator import astar

class AStarRunner:

	def __init__(self, pathnodes, network):
		self.nodesExpanded = 0
		self.pathnodes = pathnodes
		self.network = network

	def run(self):
		old_pairs = []
		for p1 in self.pathnodes:
			for p2 in self.pathnodes:
				if p1 != p2 and (p2, p1) not in old_pairs:
					path, closed = astar(p1, p2, self.network)
					print "start: ", loc2Name(p1, locations), " end: ", loc2Name(p2, locations)
					print "path: ", map(lambda x: loc2Name(x, locations), path)
					print "closed: ", map(lambda x: loc2Name(x, locations), closed)
					print "number of nodes expanded", len(closed), "\n"
					self.nodesExpanded += len(closed)
					old_pairs.append((p1, p2))
		print "number of total nodes expanded", self.nodesExpanded

def dic2Nodes(locations):
	return [locations[e] for e in locations]

def dic2Network(locations, maps):
	network = []
	for l in locations:
		if maps.has_key(l):
			for r in maps[l]:
				network.append((locations[l], locations[r]))
	return network

def loc2Name(loc, locations):
	for name, l in locations.iteritems():
		if l == loc:
			return name
	return None

'''
The Romania test map is taken from the book Artificial Intelligence: An Modern Approach.
You should find a method to measure the distance between two cities.

'''
romania = dict(
    A=set(["Z", "S", "T"]),
    B=set(["U", "P", "G", "F"]),
    C=set(["D", "R", "P"]),
    D=set(["M"]),
    E=set(["H"]),
    F=set(["S"]),
    H=set(["U"]),
    I=set(["V", "N"]),
    L=set(["T", "M"]),
    O=set(["Z", "S"]),
    P=set(["R"]),
    R=set(["S"]),
    U=set(["V"]))

locations = dict(
    A=( 91, 492),    B=(400, 327),    C=(253, 288),   D=(165, 299),
    E=(562, 293),    F=(305, 449),    G=(375, 270),   H=(534, 350),
    I=(473, 506),    L=(165, 379),    M=(168, 339),   N=(406, 537),
    O=(131, 571),    P=(320, 368),    R=(233, 410),   S=(207, 457),
    T=( 94, 410),    U=(456, 350),    V=(509, 444),   Z=(108, 531))

if __name__ == "__main__":
	a = AStarRunner(dic2Nodes(locations), dic2Network(locations, romania))
	a.run()