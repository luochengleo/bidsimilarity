#coding=utf8
import math
def cosine(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0.0, 0.0, 0.0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    if sumxx*sumyy == 0.0:
    	return 0.0
    return sumxy/math.sqrt(sumxx*sumyy)


def cosineOnlyParticipation(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0.0, 0.0, 0.0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        if x*y != 0:
	        sumxx += x*x
	        sumyy += y*y
	        sumxy += x*y
    if sumxx*sumyy == 0.0:
    	return 0.0
    return sumxy/math.sqrt(sumxx*sumyy)

class Logger:
	def __init__(self,logfile):
		self.writer = open(logfile,'w')
	def write(self,content):
		self.writer.write(content+'\n')
		print content
	def close(self):
		self.writer.close()

