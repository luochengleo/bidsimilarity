#coding=utf8
import os

from collections import defaultdict
from Utils import Logger
from DataImporter import Record
from Utils import cosine,cosineOnlyParticipation
logfile = '../data/log.txt'
datafile  = '../data/sample_data.csv'
ROLLINGWINDOW = 20
STEPSIZE = 10
RANKINGOPTION = 'RANKING'

CLUSTER_SIMILAR_CUTOFF = 0.9

BINARY_DISTANCE_FILE = '../data/distance/binary.csv'
HIGH_PRICE_DISTANCE_FILE = '../data/distance/price_high.csv'
LOW_PRICE_DISTANCE_FILE = '../data/distance/price_low.csv'

log = Logger(logfile)

# allprice [stkcd][inscode] = [(biddercode,price_normal,shares)]
allbids = defaultdict(lambda:defaultdict(lambda:list()))

alllines = open(datafile).readlines()[1:]
log.write('loading files, we have '+str(len(alllines))+' lines in total')

allrecords = []

orderedStkid = []
allinst = []

for l in alllines:
	segs = l.strip().split(',')
	if len(segs) == 7:
		allrecords.append(Record(segs[0],segs[1],segs[2],segs[3],segs[4],segs[5],segs[6]))
		if segs[0] in orderedStkid:
			pass
		else:
			orderedStkid.append(segs[0])
		if segs[2] in allinst:
			pass
		else:
			allinst.append(segs[2])

log.write('we have '+str(len(orderedStkid))+' stocks in total')
log.write('we have '+str(len(allinst))+' insts in total')

for r in allrecords:
	allbids[r.stkcd][r.inscode].append((r.biddercode,r.price_normal,r.shares))

###########################################
#       calculate similarity              #
###########################################

# Binary Code (Binary Participation)

bwriter = open(BINARY_DISTANCE_FILE,'w')
bwriter.write('INST1,INST2,cosine\n')

BinaryVectors = dict()

for _ins in allinst:
	temp = []
	for _stkid in orderedStkid:
		if len(allbids[_stkid][_ins]) > 0:
			temp.append(1)
		else:
			temp.append(0)
	BinaryVectors[_ins] = temp

for i in range(0,len(allinst)-1,1):
	for j in range(i+1,len(allinst),1):
		bwriter.write(allinst[i]+','+allinst[j]+','+str(cosine(BinaryVectors[allinst[i]],BinaryVectors[allinst[j]])))
		bwriter.write('\n')
bwriter.close()


for startIndex in range(0,len(orderedStkid),STEPSIZE):
	
	if startIndex + ROLLINGWINDOW > len(orderedStkid):
		break
	else:
		bwriter =  open(BINARY_DISTANCE_FILE+'.rolling.'+str(startIndex)+'.csv','w')
		bwriter.write('INST1,INST2,cosine\n')
		for i in range(0,len(allinst)-1,1):
			for j in range(i+1,len(allinst),1):
				bwriter.write(allinst[i]+','+allinst[j]+',')
				bwriter.write(str(cosine(BinaryVectors[allinst[i]][startIndex:startIndex+STEPSIZE],BinaryVectors[allinst[j]][startIndex:startIndex+STEPSIZE])))
				bwriter.write('\n')
		bwriter.close()

# Price Option

hpwriter = open(HIGH_PRICE_DISTANCE_FILE,'w')
hpwriter.write('INST1,INST2,cosine\n')

lpwriter = open(LOW_PRICE_DISTANCE_FILE,'w')
lpwriter.write('INST1,INST2,cosine\n')


HighPriceVectors = dict()
LowPriceVectors  = dict()

for _ins in allinst:
	_high = []
	_low  = []
	for _stkid in orderedStkid:
		h = -1.0
		l = 999999999.0
		if len(allbids[_stkid][_ins]) > 0:
			for item in allbids[_stkid][_ins]:
				if item[1] > h:
					h = item[1]
				if item[1] < l:
					l = item[1]
			_high.append(h)
			_low.append(l)
		else:
			_high.append(0.0)
			_low.append(0.0)

	HighPriceVectors[_ins] = _high
	LowPriceVectors[_ins] = _low

for i in range(0,len(allinst)-1,1):
	for j in range(i+1,len(allinst),1):
		hpwriter.write(allinst[i]+','+allinst[j]+','+str(cosineOnlyParticipation(HighPriceVectors[allinst[i]],HighPriceVectors[allinst[j]])))
		hpwriter.write('\n')

		lpwriter.write(allinst[i]+','+allinst[j]+','+str(cosineOnlyParticipation(LowPriceVectors[allinst[i]],LowPriceVectors[allinst[j]])))
		lpwriter.write('\n')
hpwriter.close()
lpwriter.close()


for startIndex in range(0,len(orderedStkid),STEPSIZE):
	
	if startIndex + ROLLINGWINDOW > len(orderedStkid):
		break
	else:
		hpwriter =  open(HIGH_PRICE_DISTANCE_FILE+'.rolling.'+str(startIndex)+'.csv','w')
		hpwriter.write('INST1,INST2,cosine\n')
		for i in range(0,len(allinst)-1,1):
			for j in range(i+1,len(allinst),1):
				hpwriter.write(allinst[i]+','+allinst[j]+',')
				hpwriter.write(str(cosineOnlyParticipation(HighPriceVectors[allinst[i]][startIndex:startIndex+STEPSIZE],HighPriceVectors[allinst[j]][startIndex:startIndex+STEPSIZE])))
				hpwriter.write('\n')
		hpwriter.close()

		lpwriter =  open(LOW_PRICE_DISTANCE_FILE+'.rolling.'+str(startIndex)+'.csv','w')
		lpwriter.write('INST1,INST2,cosine\n')
		for i in range(0,len(allinst)-1,1):
			for j in range(i+1,len(allinst),1):
				lpwriter.write(allinst[i]+','+allinst[j]+',')
				lpwriter.write(str(cosineOnlyParticipation(LowPriceVectors[allinst[i]][startIndex:startIndex+STEPSIZE],LowPriceVectors[allinst[j]][startIndex:startIndex+STEPSIZE])))
				lpwriter.write('\n')
		lpwriter.close()




#####################################
#      Cliques                      # 
#####################################


import networkx as nx

G = nx.Graph()
for l in open('../data/distance/binary.csv').readlines()[1:]:
	segs = l.strip().split(',')
	if len(segs) == 3:
		weight = float(segs[2])
		if weight > 0.9:
			G.add_edge(segs[0],segs[1])
for item in  nx.max_clique(G):
	print item
