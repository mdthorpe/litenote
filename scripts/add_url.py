#!/usr/bin/env python

import pymongo
import time
import sys

from pymongo import Connection

url = sys.argv[1]

connection = pymongo.Connection('localhost')
db = connection['litenote']

print db.urls.insert({"url": url})

