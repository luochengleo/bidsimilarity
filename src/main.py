#coding=utf8
import os

from collections import defaultdict
from Utils import Logger
from DataImporter import Record
from Utils import cosine,cosineOnlyParticipation
logfile = '../data/log.txt'
datafile  = '../data/biddata.full.csv'
ROLLINGWINDOW = 200
STEPSIZE = 50
RANKINGOPTION = 'RANKING'

CLUSTER_SIMILAR_CUTOFF = 0.9
POLICY_CHOICE_OPTION = 0


BINARY_DISTANCE_FILE = '../data/distance/binary_policy_'+str(POLICY_CHOICE_OPTION)+'.csv'
HIGH_PRICE_DISTANCE_FILE = '../data/distance/price_high_policy_'+str(POLICY_CHOICE_OPTION)+'.csv'
LOW_PRICE_DISTANCE_FILE = '../data/distance/price_low_policy_'+str(POLICY_CHOICE_OPTION)+'.csv'



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
		#Record stkcd,dealseq,inscode,biddercode,price_normal,shares,policy_flag
		#          0      1      2        3         4            5      6
		
		allrecords.append(Record(segs[6],segs[5],segs[1],segs[2],segs[4],segs[0],segs[3]))
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
log.write('computing binary distances')
bwriter = open(BINARY_DISTANCE_FILE,'w')
bwriter.write('INST1,INST2,cosine\n')

BinaryVectors = dict()
log.write('Binary matrix construction')
for _ins in allinst:
	temp = []
	for _stkid in orderedStkid:
		if len(allbids[_stkid][_ins]) > 0:
			temp.append(1)
		else:
			temp.append(0)
	BinaryVectors[_ins] = temp
log.write('Binary distances calculate')
for i in range(0,len(allinst)-1,1):
	log.write('Binary distances calculate: processing '+str(i)+' / '+str(len(allinst)))

	for j in range(i+1,len(allinst),1):
		bwriter.write(allinst[i]+','+allinst[j]+','+str(cosine(BinaryVectors[allinst[i]],BinaryVectors[allinst[j]])))
		bwriter.write('\n')
bwriter.close()

log.write('Binary distances rolling')


for startIndex in range(0,len(orderedStkid),STEPSIZE):
	log.write('Binary rolling start index '+str(startIndex))
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
log.write('computing price distances')
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

fout = open('../data/cliques/summary.txt','w')
G = nx.Graph()

for f in os.listdir('../data/distance'):
	for l in open('../data/distance/'+f).readlines()[1:]:
		segs = l.strip().split(',')
		if len(segs) == 3:
			weight = float(segs[2])
			if weight > CLUSTER_SIMILAR_CUTOFF:
				G.add_edge(segs[0],segs[1])
	fout.write('Distance File:' + f+'\n')
	for item in  nx.max_clique(G):
		fout.write(str(item))
	fout.write('\n')
fout.close()

