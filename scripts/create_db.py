#!/usr/bin/env python

import pymongo
from pymongo import Connection

try:
	connection = Connection('localhost')
except Exception, e:
	print "Failed:", repr(e)

db = connection['litenote']

# URL Collection
url_collection = db.collection['urls']
print url_collection

# Poller Samples Collection
poller_collection = db.collection['poller']
print poller_collection
