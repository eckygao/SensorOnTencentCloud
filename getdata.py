#!/usr/bin/python

import time
from lib.public import *

def updatedata( udata):
    # get time
    utime = int(time.time())
    stime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime( utime))

    # get data.dict
    ddata = {"utime":utime,"stime":stime,"udata":round(udata, 3)}

    # format data
    cache = json.dumps(ddata)#"{utime}	{stime}	{udata}".format(**ddata)
    dbsql = "insert into sensordata (utime, udata) values ('{utime}','{udata}')".format(**ddata)

    # get config
    cfile = get_cachepath()
    dbfile = get_dbpath()

    # flush cache
    f = open( cfile, "w")
    f.write(cache)
    f.close()

    # insert db
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute(dbsql)
    conn.commit();
    conn.close();

    return True

import serial
from time import sleep
ser=serial.Serial("/dev/serial0",9600)

while True :
    r_data = ser.read()
    sleep(0.3)
    data_left = ser.inWaiting()
    r_data += ser.read(data_left)
    if 9 != len(r_data):
        print 'error length: %d'%len(r_data)
        continue
    else:
        # get num
        n=0
        n=ord(r_data[4])*256+ord(r_data[5])

        updatedata(n/1000.0)
