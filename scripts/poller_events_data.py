#!/usr/bin/env python

import pymongo
import sys
import time
import cgi
import cgitb; cgitb.enable()
import json

from pymongo import objectid, json_util
from urlparse import urlparse, urlsplit
from pymongo.objectid import ObjectId



def main():
    MAX_EVENTS = 50

    form = cgi.FieldStorage()
    url = form.getvalue("url", "http://www.battlefield.com/battlefield3")
    start_time = int(form.getvalue("start_time", 1))
    end_time = int(form.getvalue("end_time", 10000000000))

    connection = pymongo.Connection('localhost')
    db = connection['litenote']

    events = list()

    first_one = db.poller_base_url.find_one({"base_url": "http://www.battlefield.com/battlefield3", 
                                        "poll_start_time":{"$gt":start_time}, 
                                        "poll_end_time":{"$lt":end_time}
                                        })

    for event in db.poller_base_url.find({"base_url": "http://www.battlefield.com/battlefield3", 
                                        "poll_start_time":{"$gt":start_time}, 
                                        "poll_end_time":{"$lt":end_time}
                                        })[:MAX_EVENTS]:
        events.append({
                        "poll_start_time": event['poll_start_time'],
                        "poll_end_time": event['poll_end_time'],
                        "css_resources": event['css_resources'],
                        "script_resources": event['script_resources'],
                        "image_resources": event['image_resources'],
                        "request_bytes": event['request_bytes'],
                        "request_time": event['poll_end_time'],
                     })

    result = {"url": url,
              "page_title": first_one['page_title'],
              "events": events}
            

    print "Content-type: application/x-javascript\r\n"
    print json.dumps(result)

if __name__ == "__main__":
    main()
