#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json # manipulation of json
import socket # for server connection
import sys
import logging
import sqlite3
import time
import datetime
import random
from time import sleep

dbname = 'hakku.db'

def init_hakkudb():
    c.execute('''CREATE TABLE temps (timestamp DATETIME, temp NUMERIC, miner TEXT);''')

def dbclose(conn):
    conn.commit()
    conn.close()

def log_temperature(now,temp,miner):
    print(now)
    print(temp)
    print(miner)
    params = (now,temp,miner)
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute("INSERT INTO temps VALUES (?,?,?)",params)
    dbclose(conn)

def main():
    random.random()
    for x in range(0,100):
        for y in range(0,1):
            log_temperature(datetime.datetime.now(),random.randrange(60,116),'S9_1')
            log_temperature(datetime.datetime.now(),random.randrange(60,116),'S9_2')
            log_temperature(datetime.datetime.now(),random.randrange(60,116),'S9_3')
        sleep(1)


if __name__ == '__main__':
    main()
