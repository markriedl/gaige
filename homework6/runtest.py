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


from behaviortree import *


tree = [(Sequence, 1), [(Sequence, 2), (TestNode, 20), (TestNode, 22)], [(Selector, 5), [(Sequence, 9), (TestNode, 11), (TestNode, 12)], (TestNode, 31), (DelayTestNode, 35, 3), TestNode]]

bt = TestBehaviorTree()
bt.buildTree(tree)
print "print"
bt.printTree()
print "run"
bt.start()
go_on = True
iterations = 0

while go_on and iterations < 100:
	iterations = iterations + 1
	result = bt.update(0)
	print result
	if result is not None:
		go_on = False

print bt.history