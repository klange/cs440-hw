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
	return ("OnTable", a) in s

def Clear(a, s):
	return ("Clear", a) in s

def GenerateFacts(state):
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
	if target == 'T':
		if source == 'T':
			return "DoNothing()"
		return "MoveToTable(%s,%s)" % (block, source)
	if source == 'T':
		source = "Table"
	return "Move(%s,%s,%s)" % (block, source, target)

def PossMove(block, source, target, state):
	if target == 'T' and source == 'T':
		return Clear(block, state)
	if target == 'T':
		return Clear(block, state) and On(block, source, state)
	if source == 'T':
		return Clear(block, state) and OnTable(block, state) and Clear(target, state)
	return Clear(block, state) and Clear(target, state) and On(block, source, state)

def Move(block, source, target, state):
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

def PrintStateLogical(state):
	for i in state:
		ar = list(i)
		print "%s(%s)" % (ar[0], ",".join(ar[1:]))

def DoMove(block, source, target, state):
	if PossMove(block,source,target,state):
		print PrintMove(block,source,target)
		return Move(block,source,target,state)
	return state

def Below(block, state):
	for i in state:
		if i[0] == "On" and i[1] == block:
			return i[2]
		if i[0] == "OnTable" and i[1] == block:
			return 'T'
	assert(False)

def LoadFile(fName):
	f_inFile = None
	try:
		f_inFile = open(fName)
	except:
		return False

	s_numBlocks = f_inFile.readline().strip()
	i_numBlocks = int(s_numBlocks)

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

def RecurseToFind(depthCounter, start, goal):
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

	stateInit = GenerateFacts(a_statesInit)
	stateFini = GenerateFacts(a_statesFini)

	for i in range(1, 11):
		# XXX: Generate CNF
		# XXX: Check with Minisat
		# XXX: if cnf == satisfiable:
		result, moves = RecurseToFind(i, stateInit, stateFini)
		if result:
			print len(moves)
			for i in moves:
				print i
			# XXX: Print out CNF
			sys.exit(0)
	print "BIG"
	sys.exit(0)
