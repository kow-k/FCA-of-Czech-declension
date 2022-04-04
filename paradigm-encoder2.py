#! /usr/bin/env python2.7
# -*- encoding: utf-8 -*-
#

# This Pythons script encodes declensional paradigms on the basis of
# pairwise identity network rather than phonological features.
# Assumptions
#  i) fields are separated by either "," or ";" .
# ii) groups of fields are separated by ";" .
# History
# created on 2015/08/DD
# modified on 2015/08/DD
# modified on 2015/12/28
#   now accepts headers like "n1", "f3"
# modified on 2016/01/12
#   implemented reversed value assignment
# modified on 2016/01/19, 21
#   (started) implementing form-based encoding

import sys, string, codecs, re
from getopt import getopt
from getlines import *

### variables and constants

fenc         = sys.getdefaultencoding()
tenc         = fenc
debug        = False
verbose      = False
bundled      = False
indexed      = False
gendered     = True
alternative  = False
alternative2 = False
reversed     = False
cardinality  = 14
header_sep   = u":"
glue         = u","
splitter0    = u","
splitter     = re.compile(ur"[,;]")

cBase = \
	[ u"a", u"á", u"i", u"í", u"y", u"ý",
		u"u", u"ú", u"ů", u"e", u"é", u"ě", u"o", u"ó", \
		u"b", u"c", u"č", u"d", u"ď", u"f", u"g", u"h", u"j", u"k", \
		u"l", u"m", u"n", u"ň", u"p", u"q", u"r", u"ř", \
		u"s", u"š", u"t", u"ť", u"v", u"w", u"x", u"z", u"ž" ]

### functions

def process(lines, tenc):

	K = [ ]; key_iteration = 0
	for i, line in enumerate(lines):
		i += 1
		if debug:
			try:
				print "line: %s" % line.encode(tenc)
			except:
				pass
		## skip comment lines
		if   line[0] == "%":
			continue
		## branch for attribute specification
		elif line[0] == "#":
			B = [ x.strip() for x in re.split(splitter, line[1:]) ]
			if debug:
				print B
			if alternative:
				A = build_attr_alt(B)
			else:
				A = build_attr(B)
			## generates attribute header
			if gendered:
				A.extend([ u"masc", u"fem", u"neut" ])
			if debug: print A
			# Printing out needs splitting print(glue.join(A)) into two steps.
			s = glue.join(A)
			print s.encode(tenc)
			# The following doesn't work, and I can't figure out why.
			#for item in A:
			#	try:
			#		print item.encode(tenc) + glue
			#	except UnicodeDecodeError:
			#		print item + glue

		## process
		else:
			header, line = line.split(header_sep)
			G = gender_encoder(header) # captures m, f, or n
			M = [ x.strip() for x in re.split(splitter, line) ]
			# M is list [sNom, sGen, ..., pNom, ...]
			# main process
			if alternative:
				result = paradigm_encoder_alt(M) # assumes .csv format
			else:
				result = paradigm_encoder(M) # assumes .csv format
			# post-process
			if debug:
				print result
			# generates and indexes a key
			key = "%s.%s" % (M[0].encode(tenc), header.encode(tenc))
			if key in K:
				key_iteration += 1
				key = "%s-%d" % (key, key_iteration)
			else:
				key_iteration = 0
				K.append(key)
			if gendered:
				result.extend(G) # assumes csv format
			## output
			if alternative2:
				try:
					encoding = glue.join(result)
				except TypeError, UnicodeEncodeError:
					encoding = glue.join(result[:-3]) + \
						glue + glue.join([str(x) for x in result[-3:]])
			else:
				encoding = glue.join([str(x) for x in result ])
			if verbose:
				if indexed:
					#print glue.join((i, key, encoding))
					print key, glue, encoding.encode(tenc)
				else:
					#print glue.join((key.encode(tenc), encoding))
					print key, glue, encoding.encode(tenc)
			else:
				if indexed:
					#print glue.join((i, key, encoding))
					print i, glue, key, glue, encoding.encode(tenc)
				else:
					#print glue.join((key, encoding))
					print key, glue, encoding.encode(tenc)

def gender_encoder(header):
	# returns gender encoding specification, assuming the distinction
	# among m(asculine), f(eminine) and n(euter)
	s = header[0]
	if   s == "m":
		return [1, 0, 0]
	elif s == "f":
		return [0, 1, 0]
	elif s == "n":
		return [0, 0, 1]
	else:
		return [0, 0, 0]

def paradigm_encoder(M):
	##
	if debug:
		print u"input M: %s" % M
	# checks cardinality
	if not cardinality == len(M):
		print u"invalid input: %s" % M
	# process
	i = 0; E = [ ]
	for i, item1 in enumerate(M):
		#M2 = [ x for x in M if M.index(x) > i ] # turned out to be wrong
		M2 = M[i+1:]
		if debug:
			print u"M2 at %d: %s" % (i, M2)
		for item2 in M2:
			if item1 == item2:
				if reversed:
					E.append(0)
				else:
					E.append(1)
			else:
				if reversed:
					E.append(1)
				else:
					E.append(0)
	return E

def paradigm_encoder_alt(M):
	# returns a list of [ sNom-a, sNom-á, ... ]
	E = [ ]
	for i, item in enumerate(M):
		for c in cBase:
			if item[-len(c):] == c: E.append(1)
			else: E.append(0)
	return E

#def paradigm_encoder_alt2(M):
#	sNom = [ ], sGen = [ ], sDat = [ ], sAcc = [ ], sVoc = [ ], sLoc = [ ], sIns = [ ], \
#	pNom = [ ], pGen = [ ], pDat = [ ], pAcc = [ ], pVoc = [ ], pLoc = [ ], pIns = [ ]
#
#	for i, item in enumerate(M):
#		if   i ==  0: sNom.extend(item)
#		elif i ==  1: sGen.extend(item)
#		elif i ==  2: sDat.extend(item)
#		elif i ==  3: sAcc.extend(item)
#		elif i ==  4: sVoc.extend(item)
#		elif i ==  5: sLoc.extend(item)
#		elif i ==  6: sIns.extend(item)
#		elif i ==  7: pNom.extend(item)
#		elif i ==  8: pGen.extend(item)
#		elif i ==  9: pDat.extend(item)
#		elif i == 10: pAcc.extend(item)
#		elif i == 11: pVoc.extend(item)
#		elif i == 12: sLoc.extend(item)
#		elif i == 13: pIns.extend(item)

def tencoder(X):

	return X.encode(tenc)

def build_attr(M):
	## generates the upper-right half of the cross Cartesian product over M
	if not len(M) == cardinality:
		print "invalid cardinality: %s" % M
	A = [ ]
	for i, item1 in enumerate(M):
		#M2 = [ x for x in M if M.index(x) > i ] # turned out to be wrong
		M2 = M[i+1:]
		if debug:
			print "M2 at %d: %s" % (i, M2)
		for item2 in M2:
			A.append("%s=%s" % (item1.encode(tenc), item2.encode(tenc)))
	return A

def build_attr_alt(M):
	if not len(M) == cardinality:
		print u"invalid cardinality: %s" % M
	A = [ ]
	for i, tag in enumerate(M):
		for j, c in enumerate(cBase):
			A.append(u"%s-%s" % (tag, c))
	return A

### testing

#if __name__ == '__main__':
#
#	S = [1,4,4,1,2,4]
#	T = [1,1,2,3,2,1,3,2,4,4,1,2,4]
#	U = ['a', 'a', 'b', 'a', 'c', 'c', 'b', 'c',]
#
#	print paradigm_encoder(S)
#	print paradigm_encoder(T)
#	print paradigm_encoder(U)


### main

output = codecs.EncodedFile(sys.stdout, fenc, tenc)

opts, files = getopt(sys.argv[1:], "dvbAIGRg:c:i:o:")

for k, v in opts:
	if k == '-v': verbose      = True
	if k == '-d': debug        = True
	if k == '-b': bundled      = True
	if k == '-I': indexed      = True
	if k == '-G': gendered     = False
	if k == '-A': alternative = True
	if k == '-R': reversed     = True
	if k == '-g': glue         = v
	if k == '-c': cardinality  = int(v) # int() is necessary
	if k == '-i':
		if   v == 's': fenc = 'sjis'
		elif v == 'u' or v == 'w': fenc = 'utf8'
		elif v == 'i': fenc = 'iso2022jp'
	if k == '-o':
		if   v == 's': tenc = 'sjis'
		elif v == 'u' or v == 'w': tenc = 'utf8'
		elif v == 'i': tenc = 'iso2022jp'

if len(files) > 0:
	if bundled:
		process(gather_lines(files, fenc='utf8'), tenc)
	else:
		for file in files:
			process(getlines(file, fenc='utf8'), tenc)
else:
	lines = \
		[ l.decode(fenc, "ignore").strip() for l in sys.stdin.readlines() if len(l) > 1 ]
	process(lines, tenc)

sys.exit()

### end of program
