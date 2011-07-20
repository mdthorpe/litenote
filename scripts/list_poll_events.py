#!/usr/bin/env python

import pymongo
import time
from pymongo import Connection

connection = pymongo.Connection('localhost')
db = connection['litenote']
for base_url in  db.poller_base_url.find():
    print "[%s] '%s' '%s'" % (time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(base_url['poll_start_time'])), base_url['base_url'], base_url['_id'])
    #for resource in  db.poller_resource.find({"base_url_poll_id": id}):
    #    print "\t[%d] [%0.2fs] %s" % (resource['http_code'], resource['request_time'], resource['full_url'])

