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

import inspect
from btnode import *

### To build a behavior tree, you can pass a nested list into buildTree.
### A list is a tree, such that the first element in the list is the root of the tree and all the remaining
###    elements are the children of the root.
### If the first element of a list is the name of a class (subclass of BTNode), then the node is created of that type
### If the first element of a list is a tuple, then the first element in the tuple is the name of the class (subclass of BTNode)
###    and the remaining elements are arguments passed into the node's constructor
###
### Example: [(Sequence, 1), [(Sequence, 2), (BTNode, 3), (BTNode, 4)], [(Selector, 5), (BTNode, 6), (BTNode, 7)]] 
###         1
###         |
###      -------
###      |     |
###      2     5
###      |     |
###     ---   ---
###     | |   | | 
###     3 4   6 7


###########################
### BehaviorTree
###
### Builds and runs behavior trees. The main function is to receive an update() call every tick and to ask the behavior tree to execute itself.

class BehaviorTree():

	### tree: the root of the tree
	### running: is the planner running?

	def __init__(self):
		self.tree = None
		self.running = False
	
	### Build the behavior tree. Spec is the symbolic specification of the tree contents.
	def buildTree(self, spec):
		self.tree = buildTreeAux(spec, self)
	
	### If the behavior tree was pre-built, set the tree.
	def setTree(self, root):
		self.tree = root
	
	### Recursively print out all the ids of all the nodes in the tree in depth-first order.
	def printTree(self):
		if self.tree is not None:
			self.tree.printTree()
	
	### Called every tick. Calls tree.execute(), which will return True for successful completion, False for failed execution, or None if execution should continue next tick. If the tree completes execution (i.e., returns True or False), then the tree is reset to begin again in the next tick.
	def update(self, delta = 0):
		if self.running and self.tree is not None:
			res = self.tree.execute(delta)
			if res is not None:
				self.tree.reset()
			return res
		else:
			return False
				
	def start(self):
		self.running = True
		
	def stop(self):
		self.running = False

##########################
### HELPERS


### Parse the behavior tree symbolic specification
def buildTreeAux(spec, agent):
	# If you see a symbol, make the node without arguments
	if not isinstance(spec, tuple) and inspect.isclass(spec):
		n = spec(agent)
		return n
	# If you see a tuple, make the node with type in the first position, and pass in the rest of the tuple as arguments
	elif isinstance(spec, tuple) and len(spec) > 0 and inspect.isclass(spec[0]):
		first, rest = spec[0], spec[1:]
		n = first(agent, rest)
		return n
	# If you see a list, recursively build the tree. First element is root of subtree and rest are children of the root
	elif isinstance(spec, list) and len(spec) > 0:
		first, rest = spec[0], spec[1:]
		n = buildTreeAux(first, agent)
		for r in rest:
			child = buildTreeAux(r, agent)
			n.addChild(child)
		return n
		
##########################
### TESTING

##################################
### TestBehaviorTree
###
### A BehaviorTree with a testing harness callback function.

class TestBehaviorTree(BehaviorTree):
	
	### history: a list containing the history of ids of behaviors that have executed.
	
	def __init__(self):
		BehaviorTree.__init__(self)
		self.history = []
	
	def start(self):
		BehaviorTree.start(self)
		self.history = []
	
	def testCallback(self, x):
		self.history.append(x)




################
### TestNode
###
### A simple leaf BTNode that returns success immediately if its index is an even integer.
### The index is the second argument to the constructor (agent is the first), and first argument passed to parseArgs.


class TestNode(BTNode):

	### The first argument is the id. It should be an integer. If there are no args, the id is () from the parent class.
	def parseArgs(self, args):
		BTNode.parseArgs(self, args)
		self.id = None
		if len(args) > 0:
			self.id = args[0]

	### Return true if the id is an even integer.
	def execute(self, delta = 0):
		BTNode.execute(self, delta)
		ret = isinstance(self.id, int) and (self.id % 2) == 0
		self.agent.testCallback((self.id, ret))
		return ret

################
### DelayTestNode
###
### A simple leaf BTNode that returns success if its index is an even integer.
### The DelayTestNode will require n ticks to complete (n calls to execute), where the number is given as an argument.
### The index is the second argument to the constructor (agent is the first), and first argument passed to parseArgs.
### The required number of iterations is the third argument to the constructor, and the second argument passed to parseArgs.


class DelayTestNode(TestNode):

	### Set the id and the number of iterations to complete the execution of this node.
	### ID is the first element in args, which is handled by the parent class.
	### Number of iterations is the second element in args.
	def parseArgs(self, args):
		TestNode.parseArgs(self, args)
		self.timer = 1
		if len(args) > 1:
			self.timer = args[1]

	### Return true if the id is an even integer, but only after a number of ticks have passed.
	### Return None if the timer has not expired.
	def execute(self, delta = 0):
		ret = TestNode.execute(self, delta)
		self.timer = self.timer - 1
		if self.timer <= 0:
			return ret
		else:
			return None

