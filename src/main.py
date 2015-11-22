# coding=utf8
import os
from collections import defaultdict
from Utils import Logger, publicElements
from DataImporter import Record
from Utils import cosine, cosineOnlyParticipation,mean
import sys

datafile = '../data/biddata.full.csv'
ROLLINGWINDOW = 200
STEPSIZE = 50
# binary cutoff: 0.3, 0.4, 0.5, 0.6
# cosine cutoff: 0.980, 0.9850, 0.990, 0.995
CLUSTER_SIMILAR_CUTOFF = 0.980
POLICY_CHOICE_OPTION = 0
BINARY_DISTANCE_CUTOFF = 0.6

RANKINGOPTION = 'RANKING'
RESULTDIR = '../data/output'

def init_parameters(filename):
    d = {}
    for l in open(filename).readlines():
        segs = l.strip().split('=')
        if len(segs) ==2:
            k,v = segs[0],segs[1]
            d[k.strip()] = v.strip()
        else:
            print len(segs)
    global datafile
    global ROLLINGWINDOW
    global STEPSIZE
    global CLUSTER_SIMILAR_CUTOFF
    global POLICY_CHOICE_OPTION
    global BINARY_DISTANCE_CUTOFF
    global RANKINGOPTION
    global RESULTDIR
    datafile = d['datafile']
    ROLLINGWINDOW = int( d['ROLLINGWINDOW'])
    STEPSIZE = int(d['STEPSIZE'])
    CLUSTER_SIMILAR_CUTOFF = float(d['CLUSTER_SIMILAR_CUTOFF'])
    POLICY_CHOICE_OPTION = int(d['POLICY_CHOICE_OPTION'])
    BINARY_DISTANCE_CUTOFF = float(d['BINARY_DISTANCE_CUTOFF'])
    RANKINGOPTION = d['RANKINGOPTION']
    RESULTDIR = d['RESULTDIR']

##### load parameters ########

init_parameters(sys.argv[1])

########   initial datapath    ############


try:
    os.mkdir(RESULTDIR)
    os.mkdir(RESULTDIR+'/distance')
    os.mkdir(RESULTDIR+'/cliques')
except:
    print 'RESULT DIR EXISTS'

logfile = RESULTDIR+'/log.txt'
log = Logger(logfile)
BINARY_DISTANCE_FILE = RESULTDIR+'/distance/binary_policy_' + str(POLICY_CHOICE_OPTION) + '.csv'
HIGH_PRICE_DISTANCE_FILE = RESULTDIR+'/distance/price_high_policy_' + str(POLICY_CHOICE_OPTION) + '.csv'
LOW_PRICE_DISTANCE_FILE = RESULTDIR+'/distance/price_low_policy_' + str(POLICY_CHOICE_OPTION) + '.csv'

#####   initial datapath ends  ############


#####    initial data structure ##########
allbids = defaultdict(lambda: defaultdict(lambda: list()))
alllines = open(datafile).readlines()[1:]
log.write('loading files, we have ' + str(len(alllines)) + ' lines in total')
allrecords = []
orderedStkid = []
allbidder = []
##########################################

#####    read data structure ##########

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
        r = Record(segs[6], segs[5], segs[1], segs[2], segs[4], segs[0], segs[3])
        if r.policy_flag ==POLICY_CHOICE_OPTION:
            allrecords.append(r)
            if r.stkcd in orderedStkid:
                pass
            else:
                orderedStkid.append(r.stkcd)
            if r.biddercode in allbidder:
                pass
            else:
                allbidder.append(r.biddercode)
log.write('the policy flag is '+str(POLICY_CHOICE_OPTION))
log.write('we have ' + str(len(orderedStkid)) + ' stocks in total')
log.write('we have ' + str(len(allbidder)) + ' insts in total')

for r in allrecords:
    allbids[r.stkcd][r.biddercode].append((r.biddercode, r.price_normal, r.shares))


def similarity():

    # os.system('del ../data/distance/*')
    ###########################################
    #       calculate similarity              #
    ###########################################

    # Binary Code (Binary Participation)
    log.write('computing binary distances')
    bwriter = open(BINARY_DISTANCE_FILE, 'w')
    bwriter.write('BIDDER1,BIDDER2,cosine,involved items\n')

    BinaryVectors = dict()
    log.write('Binary matrix construction')
    for _bidder in allbidder:
        temp = []
        for _stkid in orderedStkid:
            if len(allbids[_stkid][_bidder]) > 0:
                temp.append(1)
            else:
                temp.append(0)
        BinaryVectors[_bidder] = temp

    log.write('Binary distances calculate')
    for i in range(0, len(allbidder) - 1, 1):
        log.write('Binary distances calculate: processing ' + str(i) + ' / ' + str(len(allbidder)))

        for j in range(i + 1, len(allbidder), 1):
            dist,involved = cosine(BinaryVectors[allbidder[i]], BinaryVectors[allbidder[j]])
            bwriter.write(
                allbidder[i] + ',' + allbidder[j] + ',' + str(dist)+','+str(involved))
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
            for i in range(0, len(allbidder) - 1, 1):
                for j in range(i + 1, len(allbidder), 1):
                    bwriter.write(allbidder[i] + ',' + allbidder[j] + ',')
                    dist,involved = cosine(BinaryVectors[allbidder[i]][startIndex:startIndex + STEPSIZE],BinaryVectors[allbidder[j]][startIndex:startIndex + STEPSIZE])
                    bwriter.write(str(dist)+','+str(involved))
                    bwriter.write('\n')
            bwriter.close()

    # Price Option
    log.write('Computing price distances')
    hpwriter = open(HIGH_PRICE_DISTANCE_FILE, 'w')
    hpwriter.write('BIDDER1,BIDDER2,cosine\n')

    lpwriter = open(LOW_PRICE_DISTANCE_FILE, 'w')
    lpwriter.write('BIDDER1,BIDDER2,cosine\n')

    HighPriceVectors = dict()
    LowPriceVectors = dict()

    for _bidder in allbidder:
        _high = []
        _low = []
        for _stkid in orderedStkid:
            h = -1.0
            l = 999999999.0
            if len(allbids[_stkid][_bidder]) > 0:
                for item in allbids[_stkid][_bidder]:
                    if item[1] > h:
                        h = item[1]
                    if item[1] < l:
                        l = item[1]
                _high.append(h)
                _low.append(l)
            else:
                _high.append(0.0)
                _low.append(0.0)

        HighPriceVectors[_bidder] = _high
        LowPriceVectors[_bidder] = _low

    for i in range(0, len(allbidder) - 1, 1):
        for j in range(i + 1, len(allbidder), 1):
            dist,involved = cosineOnlyParticipation(HighPriceVectors[allbidder[i]], HighPriceVectors[allbidder[j]])
            hpwriter.write(allbidder[i] + ',' + allbidder[j] + ',' + str(dist)+','+str(involved))
            hpwriter.write('\n')

            dist,involved = cosineOnlyParticipation(LowPriceVectors[allbidder[i]], LowPriceVectors[allbidder[j]])
            lpwriter.write(allbidder[i] + ',' + allbidder[j] + ',' + str(dist)+','+str(involved))
            lpwriter.write('\n')
    hpwriter.close()
    lpwriter.close()

    for startIndex in range(0, len(orderedStkid), STEPSIZE):
        log.write('Price rolling start index ' + str(startIndex))

        if startIndex + ROLLINGWINDOW > len(orderedStkid):
            break
        else:
            hpwriter = open(HIGH_PRICE_DISTANCE_FILE + '.rolling.' + str(startIndex) + '.csv', 'w')
            hpwriter.write('BIDDER1,BIDDER2,cosine\n')
            for i in range(0, len(allbidder) - 1, 1):
                for j in range(i + 1, len(allbidder), 1):
                    hpwriter.write(allbidder[i] + ',' + allbidder[j] + ',')
                    dist,involved = cosineOnlyParticipation(HighPriceVectors[allbidder[i]][startIndex:startIndex + STEPSIZE],HighPriceVectors[allbidder[j]][startIndex:startIndex + STEPSIZE])
                    hpwriter.write(str(dist)+','+str(involved))
                    hpwriter.write('\n')
            hpwriter.close()

            lpwriter = open(LOW_PRICE_DISTANCE_FILE + '.rolling.' + str(startIndex) + '.csv', 'w')
            lpwriter.write('BIDDER1,BIDDER2,cosine\n')
            for i in range(0, len(allbidder) - 1, 1):
                for j in range(i + 1, len(allbidder), 1):
                    lpwriter.write(allbidder[i] + ',' + allbidder[j] + ',')
                    dist,involved = cosineOnlyParticipation(LowPriceVectors[allbidder[i]][startIndex:startIndex + STEPSIZE],LowPriceVectors[allbidder[j]][startIndex:startIndex + STEPSIZE])
                    lpwriter.write(str(dist)+','+str(involved))
                    lpwriter.write('\n')
            lpwriter.close()


#####################################
#      Cliques                      # 
#####################################

def cliques():
    # os.system('del ../data/cliques/*')
    from networkx.algorithms.clique import find_cliques
    import networkx as nx

    bidder2stocks = defaultdict(lambda:[])
    for r in allrecords:
        bidder2stocks[r.biddercode].append(r.stkcd)


    for f in os.listdir(RESULTDIR+'/distance'):
        G = nx.Graph()
        log.write('Computing cliques for Distance File:' + f)
        fout = open(RESULTDIR+'/cliques/' + f +'.CLUSTERSIM_CUTOFF_'+str(CLUSTER_SIMILAR_CUTOFF)+'.BINARYSIM_CUTOFF_'+str(BINARY_DISTANCE_CUTOFF)+ '.cliques.txt', 'w')

        if 'price' in f:
            accompany_filter  = defaultdict(lambda:-1.0)
            binaryDistanceFile = f.replace('price_high','binary').replace('price_low','binary')
            for l in open(RESULTDIR+'/distance/'+binaryDistanceFile).readlines()[1:]:
                _inst1,_inst2,_distance,_involved = l.strip().split(',')
                accompany_filter[(_inst1,_inst2)] = float(_distance)
                accompany_filter[(_inst2,_inst1)] = float(_distance)

        if 'binary' in f:
            accompany_filter  = defaultdict(lambda:1.0)

        distance = defaultdict(lambda:'NULL')
        for l in open(RESULTDIR+'/distance/' + f).readlines()[1:]:
            segs = l.strip().split(',')
            if len(segs) == 4:
                weight = float(segs[2])
                if (weight > CLUSTER_SIMILAR_CUTOFF) and (accompany_filter[(segs[0],segs[1])] > BINARY_DISTANCE_CUTOFF):
                    G.add_edge(segs[0], segs[1])
                    distance[(segs[0],segs[1])] = weight
                    distance[(segs[1],segs[0])] = weight
        fout.write('Distance File: ' + f + '\n')
        fout.write('CLUSTER_SIMILAR_CUTOFF:' + str(CLUSTER_SIMILAR_CUTOFF) + '\n')
        fout.write('BINARY_DISTANCE_CUTOFF:' + str(BINARY_DISTANCE_CUTOFF) + '\n\n')

        cqs = find_cliques(G)

        _idx = 0
        for item in cqs:
            # _idx += 1
            # fout.write('--------------- CLIQUE ' + str(_idx) + ' with ' + str(len(item)) + ' members-----------\n')
            accompanyList = []
            participationList = []
            priceList = []

            for i in range(0,len(item)-1,1):
                for j in range(i+1,len(item),1):
                    priceList.append(distance[(item[i],item[j])])
                    accompanyList.append(accompany_filter[(item[i],item[j])])
                    participationList.append(publicElements(bidder2stocks[item[i]],bidder2stocks[item[j]]))


            for _lt in [accompanyList,participationList,priceList]:
                for _func in [max,mean,min]:
                    fout.write(str(_func(_lt))+',')
            fout.write(','.join([str(ins) for ins in item])+'\n')
        fout.close()


similarity()
cliques()
