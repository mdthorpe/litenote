#!/usr/bin/env python

import pymongo
import time
from pymongo import Connection

connection = pymongo.Connection('localhost')
db = connection.litenote
for url in db.urls.find():
    print url['url']
