# -*- coding: utf8 -*-
import datetime
import pymysql.cursors
import logging
import sys
import pytz
import json, hashlib, time

# MySql数据库账号信息,需要提前创建好数据库
Host = '????????.sql.tencentcdb.com'
User = '????????'
Password = '????????'
Port = 0
DB = '????????'

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger()
logger.setLevel(level=logging.INFO)

g_connection = None
def connect_mysql():
    global g_connection
    try:
        g_connection = pymysql.connect(host=Host,
                                     user=User,
                                     password=Password,
                                     port=Port,
                                     db=DB,
                                     charset='utf8',
                                     autocommit = True,
                                     cursorclass=pymysql.cursors.DictCursor)
        return True, []
    except Exception as e:
        g_connection = None
        g_connection_errinfo = e;
        return False, e

print("connect database")
connect_mysql()

def recheck_connect():
    global g_connection
    if not g_connection:
        rflag, errorinfo = connect_mysql()
        if not rflag:
            return False, json.dumps(errorinfo)
    with g_connection.cursor() as cursor:
        try:
            sql = 'show databases'
            cursor.execute(sql)
            res = cursor.fetchall()
        except Exception as e:
            rflag, errorinfo = connect_mysql()
            if not rflag:
                return False, json.dumps(errorinfo)
    cursor.close()
    return True, ''

def get_index():
    global g_connection
    rflag, errorinfo = recheck_connect()
    if not rflag:
        return False, errorinfo

    with g_connection.cursor() as cursor:
        sql = 'use %s'%DB
        cursor.execute(sql)
        # get index
        cursor.execute("select unix_timestamp(stime) as utime from sensordata_test order by id desc limit 1")
        result = cursor.fetchall()
    cursor.close()
    rdata = 0 if 0 == len(result) else str(result[0]['utime'])
    return True, rdata;

def put_data(data):
    # check data
    if 0 == len(data):
        return False, "No data to insert"
    # cdb
    global g_connection
    sql = "insert into sensordata_test (stime, udata) values ( from_unixtime(%s), %s)";
    # create datalist
    sdata = []
    for i in data: 
        sdata.append([ i['utime'], i['udata']])
    # insert into db
    try:
        with g_connection.cursor() as cursor:
            cursor.executemany(sql,sdata)
            g_connection.commit()
        cursor.close()
        return True, '';
    except Exception as e:
        g_connection.rollback()
        return False, "insert failed : %s"%e
    

def main_handler(event, context):
    # base format
    rdata = { 'isBase64Encoded': False,'statusCode': 200,'headers': {"Content-Type":"text/html"},'body': ''}
    # get post data
    if 'body' not in event:
        rdata['statusCode'] = 409
        rdata['body'] = 'Lost post data';
        return rdata

    pdata = ''
    try:
        pdata = json.loads(json.loads(event['body']))
    except:
        rdata['statusCode'] = 409
        rdata['body'] = 'post not json';
        return rdata
    # check function
    print pdata, type(pdata)
    if 'type' not in pdata:
        rdata['statusCode'] = 409
        rdata['body'] = 'Lost type section:%s'%(json.dumps(pdata));
        return rdata

    if 'getindex' == pdata['type']:
        rflag, rinfo = get_index()
        rdata['statusCode'] = 200 if rflag else 409
        rdata['body'] = rinfo
    elif 'putdata' == pdata['type']:
        rflag, rinfo = put_data( pdata['data'])
        rdata['statusCode'] = 200 if rflag else 409
        rdata['body'] = rinfo
    else:
        rdata['statusCode'] = 409
        rdata['body'] = 'Unknown section : %s'%pdata['type'];

    return rdata