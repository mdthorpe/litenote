#!/usr/bin/env python

import pymongo
import sys
import time

from pymongo import objectid

def resource_print(resource):
    wall_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(resource['wall_clock']))
    print "  [%s] [%d] [%0.2fs] %s" % (wall_time,resource['http_code'], resource['request_time'], resource['full_url'])
    #print resource


event_id = sys.argv[1]

connection = pymongo.Connection('localhost')
db = connection['litenote']
for base_url in  db.poller_base_url.find({"_id": objectid.ObjectId(event_id)}):
    id = base_url['_id']
    print
    print "Poll Event ---------------------------------------------\n"
    print "URL:\t\t %s" % base_url['base_url']
    print "Title:\t\t %s" % base_url['page_title']
    print "Request Size:\t %0d bytes" % (base_url['request_bytes'])
    st = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(base_url['poll_start_time']))
    et = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(base_url['poll_end_time']))
    print "Start Time:\t %s" % st
    print "End Time:\t %s" % et
    print "Duration:\t %0.3fs" % (base_url['poll_end_time'] - base_url['poll_start_time'])
    print 
    print "Resources ---------------------------------------------\n"
    print "\n CSS:"
    for resource in  db.poller_resource.find({"base_url_poll_id": id, "resource_type": "css"}):
        resource_print(resource)
    print "\n Scripts:"
    for resource in  db.poller_resource.find({"base_url_poll_id": id, "resource_type": "script"}):
        resource_print(resource)
    print "\n Images:"
    for resource in  db.poller_resource.find({"base_url_poll_id": id, "resource_type": "image"}):
        resource_print(resource)

    print
