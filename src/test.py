#coding=utf8
__author__ = 'luocheng'


# Var.	Def.
# Stkcd	Stock ticker
# inscode	Unique id for institution
# bidcode	Unqiue id for bidder
# Price_normal	Normalized prices in the bids.
# shares	Demand for shares in the bids.
# instype	Type of institutions.
# dealseq	The sequence for the offer
# Policy_flag	=1 if free pricing subsample


import math
def cosine_similarity(v1,v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0.0, 0.0, 0.0
    for i in range(len(v1)):
        x = v1[i]; y = v2[i]
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y
    return sumxy/math.sqrt(sumxx*sumyy)

v1,v2 = [3, 45, 7, 2], [2, 54, 13, 15]
print(v1, v2, cosine_similarity(v1,v2))
