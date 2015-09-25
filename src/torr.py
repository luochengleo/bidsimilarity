#coding=utf8
__author__ = 'luocheng'
from bencode import bdecode


class Parser(object):
    def __init__(self, filePath):
        self.path = filePath
        metainfo_file = open(str(self.path), 'rb')
        self.metainfo = bdecode(metainfo_file.read())
        metainfo_file.close()

    def getStruct(self):
        print self.metainfo.keys()  # 如果是单文件就返回：0	#如果是多文件就返回:1

    def checkType(self):
        if 'files' in self.metainfo['info']:
            return 1
        else:
            return 0

    def getCreationDate(self):
        if 'creation date' in self.metainfo:
            return self.metainfo['creation date']
        else:
            return ''

    def getInfo(self):
        return self.metainfo['info'].keys()  # 获得文件名

    def getName(self):
        info = self.metainfo['info']
        if 'name.utf-8' in info:
            filename = info['name.utf-8']
        else:
            filename = info['name']
        for c in filename:
            if c == "'":
                filename = filename.replace(c, "///'")
                return filename

    def getInfoFiles(self): # 多文件的情况下，获得所有文件，返回为:dic
        return self.metainfo['info']['files']

    def getCreatedBy(self):  # 返回创建时间
        if 'created by' in self.metainfo:
            return self.metainfo['created by']
        else:
            return ''
    def getEncoding(self): # 获得编码方式

        if 'encoding' in self.metainfo:
            return self.metainfo['encoding']
        return ""

    def getComments(self):
        info = self.metainfo['info']
        if 'comment.utf-8' in self.metainfo:
            comment = self.metainfo['comment.utf-8']
            return comment
        else:
            return ''


import time



import os
torrents = os.listdir('E:\\tor\\torr1')

for t in torrents:
    parser = Parser('E:\\tor\\torr1\\'+ t)
    print t,'created by:' + parser.getCreationDate()
