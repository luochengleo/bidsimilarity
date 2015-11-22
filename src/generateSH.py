__author__ = 'luocheng'

idx = 0
commands = open('batch.bat','w')
for b in [0.3,0.4,0.5,0.6]:
    for p in [0.980,0.985,0.990,0.995]:
        idx +=1
        # commands.write('nohup python main.py ./config'+str(idx)+' > '+str(idx)+'.log &\n')
        commands.write('start python main.py ./config'+str(idx)+'\n')
        fout=open('config'+str(idx),'w')
        fout.write('datafile=../data/biddata.full.csv\n')
        fout.write('ROLLINGWINDOW = 200\n')
        fout.write('STEPSIZE = 50\n')
        fout.write('CLUSTER_SIMILAR_CUTOFF ='+str(p)+'\n')
        fout.write('POLICY_CHOICE_OPTION = 0\n')
        fout.write('BINARY_DISTANCE_CUTOFF ='+str(b)+'\n')
        fout.write('RANKINGOPTION =RANKING\n')
        fout.write('RESULTDIR =../data/output'+str(b)+'_'+str(p))
        fout.close()