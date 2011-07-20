#!/usr/bin/env python

import pymongo
from pymongo import Connection

try:
	connection = Connection('localhost')
except Exception, e:
	print "Failed:", repr(e)

db = connection.litenote

# URL Collection
url_collection = db.urls
url_collection.drop()
print url_collection

# Poller Samples Collection
poller_base_url_collection = db.poller_base_url
poller_base_url_collection.drop()
print poller_base_url_collection

poller_resource_collection = db.poller_resource
poller_resource_collection.drop()
print poller_resource_collection

