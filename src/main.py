# coding=utf8
import os

from collections import defaultdict
from Utils import Logger
from DataImporter import Record
from Utils import cosine, cosineOnlyParticipation

logfile = '../data/log.txt'
datafile = '../data/biddata.full.csv'
ROLLINGWINDOW = 200
STEPSIZE = 50
RANKINGOPTION = 'RANKING'

CLUSTER_SIMILAR_CUTOFF = 0.99
POLICY_CHOICE_OPTION = 0

BINARY_DISTANCE_FILE = '../data/distance/binary_policy_' + str(POLICY_CHOICE_OPTION) + '.csv'
HIGH_PRICE_DISTANCE_FILE = '../data/distance/price_high_policy_' + str(POLICY_CHOICE_OPTION) + '.csv'
LOW_PRICE_DISTANCE_FILE = '../data/distance/price_low_policy_' + str(POLICY_CHOICE_OPTION) + '.csv'

log = Logger(logfile)

# allprice [stkcd][inscode] = [(biddercode,price_normal,shares)]
allbids = defaultdict(lambda: defaultdict(lambda: list()))

alllines = open(datafile).readlines()[1:]
log.write('loading files, we have ' + str(len(alllines)) + ' lines in total')

allrecords = []

orderedStkid = []
allinst = []

for l in alllines:
    segs = l.strip().split(',')
    if len(segs) == 7:
        # Record stkcd,dealseq,inscode,biddercode,price_normal,shares,policy_flag
        #          0      1      2        3         4            5      6
        # Full data segs
        #  shares,inscode,bidcode,policy_flag,price_normal,dealseq,stkcd2
        # Record: __init__(stkcd,dealseq,inscode,biddercode,price_normal,shares,policy_flag):
        #                    6    5        1      2           4           0     3
        # data2
        allrecords.append(Record(segs[6], segs[5], segs[1], segs[2], segs[4], segs[0], segs[3]))
        # data1
        # allrecords.append(Record(segs[0],segs[1],segs[2],segs[3],segs[4],segs[5],segs[6]))
        if segs[6] in orderedStkid:
            pass
        else:
            orderedStkid.append(segs[6])
        if segs[1] in allinst:
            pass
        else:
            allinst.append(segs[1])

log.write('we have ' + str(len(orderedStkid)) + ' stocks in total')
log.write('we have ' + str(len(allinst)) + ' insts in total')

for r in allrecords:
    allbids[r.stkcd][r.inscode].append((r.biddercode, r.price_normal, r.shares))


def similarity():
    ###########################################
    #       calculate similarity              #
    ###########################################

    # Binary Code (Binary Participation)
    log.write('computing binary distances')
    bwriter = open(BINARY_DISTANCE_FILE, 'w')
    bwriter.write('INST1,INST2,cosine,involved items\n')

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
    for i in range(0, len(allinst) - 1, 1):
        log.write('Binary distances calculate: processing ' + str(i) + ' / ' + str(len(allinst)))

        for j in range(i + 1, len(allinst), 1):
            dist,involved = cosine(BinaryVectors[allinst[i]], BinaryVectors[allinst[j]])
            bwriter.write(
                allinst[i] + ',' + allinst[j] + ',' + str(dist)+','+str(involved))
            bwriter.write('\n')
    bwriter.close()

    log.write('Binary distances rolling')

    for startIndex in range(0, len(orderedStkid), STEPSIZE):
        log.write('Binary rolling start index ' + str(startIndex))
        if startIndex + ROLLINGWINDOW > len(orderedStkid):
            break
        else:
            bwriter = open(BINARY_DISTANCE_FILE + '.rolling.' + str(startIndex) + '.csv', 'w')
            bwriter.write('INST1,INST2,cosine\n')
            for i in range(0, len(allinst) - 1, 1):
                for j in range(i + 1, len(allinst), 1):
                    bwriter.write(allinst[i] + ',' + allinst[j] + ',')
                    dist,involved = cosine(BinaryVectors[allinst[i]][startIndex:startIndex + STEPSIZE],BinaryVectors[allinst[j]][startIndex:startIndex + STEPSIZE])
                    bwriter.write(str(dist)+','+str(involved))
                    bwriter.write('\n')
            bwriter.close()

    # Price Option
    log.write('Computing price distances')
    hpwriter = open(HIGH_PRICE_DISTANCE_FILE, 'w')
    hpwriter.write('INST1,INST2,cosine\n')

    lpwriter = open(LOW_PRICE_DISTANCE_FILE, 'w')
    lpwriter.write('INST1,INST2,cosine\n')

    HighPriceVectors = dict()
    LowPriceVectors = dict()

    for _ins in allinst:
        _high = []
        _low = []
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

    for i in range(0, len(allinst) - 1, 1):
        for j in range(i + 1, len(allinst), 1):
            dist,involved = cosineOnlyParticipation(HighPriceVectors[allinst[i]], HighPriceVectors[allinst[j]])
            hpwriter.write(allinst[i] + ',' + allinst[j] + ',' + str(dist)+','+str(involved))
            hpwriter.write('\n')

            dist,involved = cosineOnlyParticipation(LowPriceVectors[allinst[i]], LowPriceVectors[allinst[j]])
            lpwriter.write(allinst[i] + ',' + allinst[j] + ',' + str(dist)+','+str(involved))
            lpwriter.write('\n')
    hpwriter.close()
    lpwriter.close()

    for startIndex in range(0, len(orderedStkid), STEPSIZE):
        log.write('Price rolling start index ' + str(startIndex))

        if startIndex + ROLLINGWINDOW > len(orderedStkid):
            break
        else:
            hpwriter = open(HIGH_PRICE_DISTANCE_FILE + '.rolling.' + str(startIndex) + '.csv', 'w')
            hpwriter.write('INST1,INST2,cosine\n')
            for i in range(0, len(allinst) - 1, 1):
                for j in range(i + 1, len(allinst), 1):
                    hpwriter.write(allinst[i] + ',' + allinst[j] + ',')
                    dist,involved = cosineOnlyParticipation(HighPriceVectors[allinst[i]][startIndex:startIndex + STEPSIZE],HighPriceVectors[allinst[j]][startIndex:startIndex + STEPSIZE])
                    hpwriter.write(str(dist)+','+str(involved))
                    hpwriter.write('\n')
            hpwriter.close()

            lpwriter = open(LOW_PRICE_DISTANCE_FILE + '.rolling.' + str(startIndex) + '.csv', 'w')
            lpwriter.write('INST1,INST2,cosine\n')
            for i in range(0, len(allinst) - 1, 1):
                for j in range(i + 1, len(allinst), 1):
                    lpwriter.write(allinst[i] + ',' + allinst[j] + ',')
                    dist,involved = cosineOnlyParticipation(LowPriceVectors[allinst[i]][startIndex:startIndex + STEPSIZE],LowPriceVectors[allinst[j]][startIndex:startIndex + STEPSIZE])
                    lpwriter.write(str(dist)+','+str(involved))
                    lpwriter.write('\n')
            lpwriter.close()


#####################################
#      Cliques                      # 
#####################################

def cliques():
    from networkx.algorithms.clique import find_cliques
    import networkx as nx
    G = nx.Graph()

    for f in os.listdir('../data/distance'):
        log.write('Computing cliques for Distance File:' + f)
        fout = open('../data/cliques/' + f + '.cliques.txt', 'w')

        for l in open('../data/distance/' + f).readlines()[1:]:
            segs = l.strip().split(',')
            if len(segs) == 4:
                weight = float(segs[2])
                if weight > CLUSTER_SIMILAR_CUTOFF:
                    G.add_edge(segs[0], segs[1])
        fout.write('Distance File: ' + f + '\n')
        fout.write('CLUSTER_SIMILAR_CUTOFF:' + str(CLUSTER_SIMILAR_CUTOFF) + '\n\n')
        cqs = find_cliques(G)

        _idx = 0
        for item in cqs:
            _idx += 1
            fout.write('--------------- CLIQUE ' + str(_idx) + ' with ' + str(len(item)) + ' members-----------\n')
            fout.write(','.join([str(ins) for ins in item]))
            fout.write('\n--------------------------------------------------\n')

        fout.close()


similarity()
# cliques()
