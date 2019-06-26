#!/usr/bin/python

import sqlite3, time
from lib.public import *
from lib import apigw

# get config
sdb = get_dbpath()

# get cdb index
rflag, rdata = apigw.getindex()
if not rflag:
    print rdata
    exit(1)
index = int(rdata) #int(rdata[1:-1])
print "index = {}, {}".format(index,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime( index)))

# get sqlite data
sdbo = sqlite3.connect(sdb)
so = sdbo.cursor()
sdata = so.execute("select utime, udata from sensordata where utime > '%s'"%index)

ndata = []
for i in sdata:
    ndata.append({'utime':i[0], 'udata':i[1]})
if 0 == len(ndata):
    print 'No new data'
    exit(0)
print "new record : %d"%len(ndata)
# commit data
rflag, errinfo = apigw.putdata(ndata)
if not rflag:
    print errinfo
    exit(1)
print 'Success'
exit(0)
