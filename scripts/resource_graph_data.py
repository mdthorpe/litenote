#!/usr/bin/env python

import pymongo
import sys
import time
import json

import cgi
import cgitb; cgitb.enable()

from pymongo import objectid, json_util
from urlparse import urlparse, urlsplit
from pymongo.objectid import ObjectId


def main():
    form = cgi.FieldStorage()
    event_id = form.getvalue("event_id", "4e27542f6972651fa0000000")

    connection = pymongo.Connection('localhost')
    db = connection['litenote']
    for base_url in  db.poller_base_url.find({"_id": objectid.ObjectId(event_id)}):
        id = base_url['_id']

        resources = list()
        tooltips = list()
        
        for resource in db.poller_resource.find({"base_url_poll_id": id}):

            parsed_url = urlparse(resource['full_url'])
            wall_clock_start = resource['wall_clock'] - base_url['parse_adjustment'] - base_url['poll_start_time']
            wall_clock_end = wall_clock_start + resource['request_time']

            tooltips.append(''.join(['<a href=\"', resource['full_url'],'\">',resource['full_url'],'</a>']))

            resources.append([
                              "%0.3f" % (wall_clock_start),# "request_start": 
                              "%0.3f" % (wall_clock_end),  # "request_end": 
                              '',
                              parsed_url.path.split('/')[-1],# "file":
                              parsed_url.netloc, # "host": 
                              parsed_url.path, # "path": 
                              resource['resource_type'], # "type": 
                              "%0.3f" % (resource['request_time']),# "request_time": 
                             ])

        base_url['_id'] = str(base_url['_id'])
        print "Content-type: application/x-javascript\r\n"

        print json.dumps({ "request": base_url, "resources": resources, "tooltips": tooltips})

if __name__ == "__main__":
    main()
