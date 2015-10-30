# coding=utf8



class Record:
    def __init__(self, stkcd, dealseq, inscode, biddercode, price_normal, shares, policy_flag):
        self.stkcd = str(stkcd)
        self.dealseq = int(dealseq)
        self.inscode = str(inscode)
        self.biddercode = str(biddercode)
        self.price_normal = float(price_normal)
        self.shares = float(shares)
        self.policy_flag = int(policy_flag)
