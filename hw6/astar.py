#!/usr/bin/env python

import sys, sets

# Open the input file
if len(sys.argv) > 1:
	try:
		sys.stdin = open(sys.argv[1])
	except:
		print >>sys.stderr, "Failed to open file `%s`, aborting." % (sys.argv[1])
		sys.exit(1)
else:
	print >>sys.stderr, "Excepted a filename as an argument, aborting."
	print >>sys.stderr, "Try `%s sample.txt`." % (sys.argv[0])
	sys.exit(1)

def PrintCell(c):
	""" Print a cell (c) in the correct output format. """
	# (y,x) 1-indexed
	print "(%d,%d)" % (c[0] + 1, c[1] + 1)

# Gather size information.
size = int(raw_input())
world = []

# Read the world
for i in xrange(size):
	world.append(raw_input())

# A* scoring maps
g_score = {}
h_score = {}
f_score = {}

def Heuristic(start, goal):
	""" Manhattan distance """
	return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

def FindBest(openset, f_score):
	""" Return the node with the best F score """
	best_val = None
	best_obj = None
	for x in openset:
		if best_obj == None or f_score[x] < best_val:
			# We have found a better match.
			best_obj = x
			best_val = f_score[x]
	return best_obj

def GetNeighbors(node):
	""" Return a list of valid neighboring nodes to `node` """
	out = []
	if node[0] > 0: # Up
		out.append((node[0]-1,node[1]))
	if node[1] > 0: # Left
		out.append((node[0],node[1]-1))
	if node[0] < size - 1: # Down
		out.append((node[0]+1,node[1]))
	if node[1] < size - 1: # Right
		out.append((node[0],node[1]+1))
	return out

def E(node):
	""" Return the elevation of a node """
	return int(world[node[0]][node[1]])

def Cost(a,b):
	""" Return the cost of moving between two nodes, a and b """
	return 1 + abs(E(a) - E(b)) # As given in the homework specifications

def BuildPath(came_from, node):
	""" Build an ordered list of nodes containing the path represented by come_from, ending at node """
	if node in came_from:
		# Recursively build path
		p = BuildPath(came_from, came_from[node])
		p.append(node)
		return p
	else:
		# Hit the end.
		return [node]

def AStar(start, goal):
	""" A* search algorithm """
	closedset = sets.Set()        # Evaluated nodes.
	openset   = sets.Set([start]) # Tentative nodes.
	came_from = {}                # Navigated paths.

	# Cost from best known path
	g_score[start] = 0
	# Heuristic costs
	h_score[start] = Heuristic(start, goal)
	# Estimated total cost through this point
	f_score[start] = g_score[start] + h_score[start]
	while len(openset) > 0:
		# Find the best-valued node from the available set of tentative nodes.
		current = FindBest(openset, f_score)
		# If we have found the goal with the best next node, we are done.
		if current == goal:
			# Reconstruct the path and return it.
			return BuildPath(came_from, goal)
		# Otherwise, we remove this node from the tentative list
		openset.remove(current)
		# And add it to the processed list
		closedset.add(current)
		# And process the neighbors...
		for neighbor in GetNeighbors(current):
			# If we already processed this node, we don't need to do it again.
			if neighbor in closedset:
				continue
			# Get the tentative cost of moving from the current node to this neighbor
			tentative = g_score[current] + Cost(current, neighbor)
			# Two conditions yield a better target:
			isBetter = False
			if not neighbor in openset:
				# If the neighbor is not open
				openset.add(neighbor)
				h_score[neighbor] = Heuristic(neighbor, goal)
				isBetter = True
			elif tentative < g_score[neighbor]:
				# Or if it has a lower g-score than we expect
				isBetter = True
			if isBetter:
				# And if it is, we continue from there.
				came_from[neighbor] = current
				g_score[neighbor]   = tentative
				f_score[neighbor]   = g_score[neighbor] + h_score[neighbor]
	# If we ever reach this point, we somehow failed to find a path,
	# which shouldn't be possible on these simple rectangular grids.
	print >>sys.stderr, "Failed to find a solution!"
	sys.exit(1)

def TotalCost(path):
	""" Return the total cost of a path """
	if len(path) == 1:
		# Hit the end, base case = 0
		return 0
	else:
		# Recursively find costs using the Cost function above
		return Cost(path[0],path[1]) + TotalCost(path[1:])


# Run as requested by the MP to go from the upper left to the lower right.
# Note that internally, we have used 0-indexed values.
results = AStar((0,0), (size-1,size-1))

# Print the output as requested
print TotalCost(results) # total cost
for node in results:
	PrintCell(node) # each node
