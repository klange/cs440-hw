#!/usr/bin/env python
import sys, os

i_numBlocks  = 0
a_statesInit = []
a_statesFini = []
a_blocks     = []

def On(a, b, s):
	""" True if a is on b in s """
	if (b == 'T'):
		return OnTable(a,s)
	return ("On", a, b) in s

def OnTable(a, s):
	"""
	OnTable fact
	"""
	return ("OnTable", a) in s

def Clear(a, s):
	"""
	Clear fact
	"""
	return ("Clear", a) in s

def GenerateFacts(state):
	"""
	Generate facts from a state
	"""
	facts = set()
	for i in state:
		if len(i) > 0:
			facts.add(("OnTable",i[0]))
			last = i[0]
			for j in i[1:]:
				facts.add(("On",j,last))
				last = j
			facts.add(("Clear",last))
	return facts

def PrintMove(block, source, target):
	"""
	Move action -> string
	"""
	if target == 'T':
		if source == 'T':
			return "DoNothing()"
		return "MoveToTable(%s,%s)" % (block, source)
	if source == 'T':
		source = "Table"
	return "Move(%s,%s,%s)" % (block, source, target)

def PossMove(block, source, target, state):
	"""
	Is this move possible?
	"""
	if target == 'T' and source == 'T':
		return Clear(block, state) and OnTable(block, state)
	if target == 'T':
		return Clear(block, state) and On(block, source, state)
	if source == 'T':
		return Clear(block, state) and OnTable(block, state) and Clear(target, state)
	return Clear(block, state) and Clear(target, state) and On(block, source, state)

def Move(block, source, target, state):
	"""
	Perform a Move
	"""
	facts = state.copy()
	if source == 'T':
		facts.remove(("OnTable", block))
	else:
		facts.remove(("On", block, source))
		facts.add(("Clear", source))
	if target == 'T':
		facts.add(("OnTable", block))
	else:
		facts.add(("On", block, target))
		facts.remove(("Clear", target))
	return facts

def ToStringCNF(statement,step):
	"""
	Convert a fluent statement to a string for the given step.
	"""
	ar = list(statement)
	newvars = []
	for i in ar[1:]:
		i = ord(i) - ord('A')
		newvars.append(str(i))
	newvars.append(str(step))
	return "%s(%s)" % (ar[0], ",".join(newvars))

def Below(block, state):
	"""
	Retreives the block below 'block'.
	"""
	for i in state:
		if i[0] == "On" and i[1] == block:
			return i[2]
		if i[0] == "OnTable" and i[1] == block:
			return 'T'
	assert(False)

def LoadFile(fName):
	"""
	Load a file containing start and finish states.
	"""
	f_inFile = None
	try:
		f_inFile = open(fName)
	except:
		return False

	s_numBlocks = f_inFile.readline().strip()
	i_numBlocks = int(s_numBlocks)

	# Load the initial state
	for i in xrange(i_numBlocks):
		s = f_inFile.readline().strip()
		if len(s) < 1:
			continue
		t = []
		for block in s:
			t.append(block)
			if not block in a_blocks:
				a_blocks.append(block)
		a_statesInit.append(t)

	# Load the final state
	for i in xrange(i_numBlocks):
		s = f_inFile.readline().strip()
		if len(s) < 1:
			continue
		t = []
		for block in s:
			t.append(block)
		a_statesFini.append(t)

	f_inFile.close()
	return True

def GenerateCNF(numBlocks, stateInit, stateFini, steps):
	"""
	Generate and check a CNF formula with minisat.
	"""
	clauses = []
	# Generate initial states
	for i in [ToStringCNF(x,0)     for x in stateInit]:
		clauses.append([i])
	# Generate final states
	for i in [ToStringCNF(x,steps) for x in stateFini]:
		clauses.append([i])

	# Generate actions (for transitions of On/OnTable)
	for i in range(numBlocks):
		for j in range(numBlocks+1):
			if (j == i):
				continue
			for l in range(steps):
				newStatements = []
				if j == numBlocks:
					newStatements.append("!OnTable(%d,%d)" % (i,l+1))
				else:
					newStatements.append("!On(%d,%d,%d)" % (i,j,l+1))
				for k in range(numBlocks+1):
					if (k == i or j == k):
						continue
					if j == numBlocks:
						newStatements.append("MoveToTable(%d,%d,%d)" % (i,k,l))
					else:
						newStatements.append("Move(%d,%d,%d,%d)" % (i,k,j,l))
				for k in range(numBlocks+1):
					if (k == i or j == k):
						continue
					moreStatements = newStatements[:]
					if k == numBlocks:
						moreStatements.append("!MoveToTable(%d,%d,%d)" % (i,j,l))
					else:
						moreStatements.append("!Move(%d,%d,%d,%d)" % (i,j,k,l))
					clauses.append(moreStatements)
				moreStatements = newStatements[:]
				if j == numBlocks:
					moreStatements.append("OnTable(%d,%d)" % (i,l))
				else:
					moreStatements.append("On(%d,%d,%d)" % (i,j,l))
				clauses.append(moreStatements)

	# Generate singular-block uniqueness on actions,
	#   requirements for On/Clear, etc.
	for l in range(steps):
		for i in range(numBlocks):
			for j in range(numBlocks+1):
				if i == j: continue
				for k in range(numBlocks+1):
					if j == k or i == k: continue
					for m in range(numBlocks):
						if j == m or k == m or i == m: continue
						if k == numBlocks:
							clauses.append(["!MoveToTable(%d,%d,%d)" % (i,j,l), "!Move(%d,%d,%d,%d)" % (i,j,m,l)])
						else:
							clauses.append(["!Move(%d,%d,%d,%d)" % (i,j,k,l), "!Move(%d,%d,%d,%d)" % (i,j,m,l)])
					if k != numBlocks:
						if j == numBlocks:
							clauses.append(["!Move(%d,%d,%d,%d)" % (i,j,k,l), "OnTable(%d,%d)" % (i,l)])
						else:
							clauses.append(["!Move(%d,%d,%d,%d)" % (i,j,k,l), "On(%d,%d,%d)" % (i,j,l)])
						clauses.append(["!Move(%d,%d,%d,%d)" % (i,j,k,l), "Clear(%d,%d)" % (i,l)])
						clauses.append(["!Move(%d,%d,%d,%d)" % (i,j,k,l), "Clear(%d,%d)" % (k,l)])
					else:
						clauses.append(["!MoveToTable(%d,%d,%d)" % (i,j,l), "Clear(%d,%d)" % (i,l)])
						clauses.append(["!MoveToTable(%d,%d,%d)" % (i,j,l), "On(%d,%d,%d)" % (i,j,l)])
						if j != numBlocks and k != numBlocks:
							clauses.append(["!On(%d,%d,%d)" % (i,j,l), "!On(%d,%d,%d)" % (i,k,l)])
						elif j != numBlocks and k == numBlocks:
							clauses.append(["!On(%d,%d,%d)" % (i,k,l), "!OnTable(%d,%d)" % (i,l)])
				if j != numBlocks:
					clauses.append(["!On(%d,%d,%d)" % (i,j,l), "!Clear(%d,%d)" % (j,l)])

	# Generate single-action-per-tick rules
	for i in range(numBlocks):
		for j in range(numBlocks + 1):
			for k in range(numBlocks + 1):
				for l in range(numBlocks):
					for m in range(numBlocks + 1):
						for n in range(numBlocks + 1):
							for o in range(steps):
								if i == l and j == m and k == n:
									continue
								if k == numBlocks and n == numBlocks:
									clauses.append(["!MoveToTable(%d,%d,%d)" % (i,j,o), "!MoveToTable(%d,%d,%d)" % (l,m,o)])
								elif k == numBlocks:
									clauses.append(["!MoveToTable(%d,%d,%d)" % (i,j,o), "!Move(%d,%d,%d,%d)" % (l,m,n,o)])
								elif n == numBlocks:
									clauses.append(["!Move(%d,%d,%d,%d)" % (i,j,k,o), "!MoveToTable(%d,%d,%d)" % (l,m,o)])
								else:
									clauses.append(["!Move(%d,%d,%d,%d)" % (i,j,k,o), "!Move(%d,%d,%d,%d)" % (l,m,n,o)])

	# Generate singular On() requirements
	for i in range(numBlocks):
		for j in range(numBlocks):
			for k in range(numBlocks + 1):
				if k == j: continue
				for s in range(steps):
					if k == numBlocks:
						clauses.append(["!On(%d,%d,%d)" % (i,j,s), "!OnTable(%d,%d)" % (i,s)])
					else:
						clauses.append(["!On(%d,%d,%d)" % (i,j,s), "!On(%d,%d,%d)" % (i,k,s)])

	# Convert fluents to numeral variables
	variables = {}
	revVars   = {}
	varCount = 0
	for i in clauses:
		for var in i:
			if var[0] == '!':
				var = var[1:]
			if not variables.has_key(var):
				variables[var] = varCount + 1
				varCount += 1
	for k,v in variables.items():
		revVars[str(v)] = k

	# Generate the actual file, and process it.
	import tempfile, os, subprocess
	fd,name = tempfile.mkstemp()
	os.write(fd, "c Pathfinding check.\n")
	os.write(fd, "p cnf %d %d\n" % (varCount, len(clauses)))
	def Reformat(variable):
		output = ""
		if variable[0] == '!':
			output += "-"
			variable = variable[1:]
		output += str(variables[variable])
		return output
	for i in clauses:
		os.write(fd, " ".join([Reformat(var) for var in i]) + " 0\n")
	os.close(fd)

	# Process the output file
	p = subprocess.Popen(["minisat", name, '.results.tmp'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	(sout,serr) = p.communicate()
	if sout.find("UNSATISFIABLE") != -1 or serr.find("UNSATISFIABLE") != -1:
		# We did not find a result
		os.remove(name)
		return (False, None)
	elif sout.find("SATISFIABLE") != -1 or serr.find("SATISFIABLE") != -1:
		# We found a solution!
		if False:
			# (Left for debugging; print the resulting determined values of all fluents)
			print "\033[1;32m"
			f = open('.results.tmp')
			tmp = f.read()
			f.close()
			tmp = tmp.split("\n")[1]
			out = []
			for k in tmp.split(" "):
				if k == "0":
					continue
				if k[0] == '-':
					out.append("!%s" % revVars[k[1:]])
				else:
					out.append("%s" % revVars[k])
			print " ^ ".join(out)
			print "\033[0m"
		return (True, name)
	else:
		# I'm not entirely sure what happend.
		os.remove(name)
		return (False, None)

def CountBlocks(state):
	"""
	Count the number of blocks in a state.
	"""
	blocks = []
	for i in state:
		if i[0] == "On" and not i[1] in blocks:
			blocks.append(i[1])
		if i[0] == "Clear" and not i[1] in blocks:
			blocks.append(i[1])
		if i[0] == "OnTable" and not i[1] in blocks:
			blocks.append(i[1])
	return len(blocks)


def RecurseToFind(depthCounter, start, goal):
	"""
	Recursively find a valid plan at the requested level of steps, if possible.
	"""
	if depthCounter == 0:
		return False, []
	moveableBlocks = []
	for i in start:
		if i[0] == "Clear":
			moveableBlocks.append(i[1])
	for i in moveableBlocks:
		targets = moveableBlocks[:]
		targets.insert(0,'T')
		targets.remove(i)
		for j in targets:
			if PossMove(i, Below(i, start), j, start):
				nState = Move(i, Below(i, start), j, start)
				if nState == goal:
					return True, [PrintMove(i,Below(i,start),j)]
				else:
					result, moves = RecurseToFind(depthCounter - 1, nState, goal)
					if result:
						moves.insert(0, PrintMove(i, Below(i, start), j))
						return True, moves
	return False, []

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "%s: expected argument" % (sys.argv[0])
		sys.exit(1)

	if not LoadFile(sys.argv[1]):
		print "%s: invalid file" % (sys.argv[0])
		sys.exit(1)

	# Generate facts from the initial state
	stateInit = GenerateFacts(a_statesInit)
	# Generate facts from the final state
	stateFini = GenerateFacts(a_statesFini)

	for i in range(1, 11):
		# Generate and test a CNF
		result, cnf = GenerateCNF(CountBlocks(stateInit), stateInit, stateFini, i)
		if not result:
			# If the CNF failed to satisfy, we can't do it in this number of moves.
			continue
		# Otherwise, we're done, do a recursive search to find a plan
		result, moves = RecurseToFind(i, stateInit, stateFini)
		if result:
			# Print the moves required
			print len(moves)
			for i in moves:
				print i
			# And then dump the CNF file
			f = open(cnf)
			print f.read()
			f.close()
			# Clean up
			os.remove(cnf)
			# End exit
			sys.exit(0)
	# We have failed to find a result.
	print "BIG"
	sys.exit(0)
