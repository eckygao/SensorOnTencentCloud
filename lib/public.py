#!/usr/bin/python

import os,json,sqlite3

def get_config( ):
    confile = os.path.split(os.path.realpath(__file__))[0] + '/../data/data.conf'
    with open(confile,'r') as f:
        data = json.load(f)
        return data

def get_dbinitsql():
    sqlfile = get_config()['sqlite']['initfile']
    return open( sqlfile, "r").read()

def get_dbpath():
    sdb = get_config()['sqlite']['dbfile']
    if not os.path.isfile(sdb):
        conn = sqlite3.connect(sdb)
        print "Opened database successfully";
        c = conn.cursor()
        c.execute(get_dbinitsql())
        conn.commit();
        conn.close();
    return sdb

def get_cachepath():
    return get_config()['cache']
