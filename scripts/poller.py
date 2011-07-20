#!/usr/bin/env python
##
## Because Keynote Sucks
## 
## Author: Mike Thorpe <mthorpe@ea.com>
## Date: Mon Jul 18 18:00:22 UTC 2011
##

import sys
import re
import mechanize
import time
import pymongo
import itertools

from BeautifulSoup import BeautifulSoup
from sets import Set
from urllib2 import HTTPError
from urllib import quote
from multiprocessing import Process, Pool
from urlparse import urlparse, urlunsplit

###########################################################################
def check_url(resource_url):

    url = resource_url[1]

    browser = mechanize.Browser()
    error_message = ""

    t1 = time.time()
    try:
        fullurl = quote(url, safe="%/:=&?~#+!$,;'@()*[]")
        response = browser.open(fullurl)
        http_code = 200
        if browser.response().info().getheader('Content-length'):
            size_of = browser.response().info().getheader('Content-length')
        else:
            size_of = sys.getsizeof(response.read())

    except HTTPError, e:
        http_code = e.code
        size_of = 0
        error_message = "%s\n%s\n%s\n" % (browser.request.get_full_url(), 
                                      browser.response().info(), 
                                      str(browser.response()) )
    t2 = time.time()

    result = {
            'full_url': resource_url[1],
            'http_code': http_code, 
            'bytes': int(size_of), 
            'request_time': round(t2-t1,3),
            'resource_type': resource_url[0],
            'wall_clock' : time.time(),
            'error_message': error_message}

    return result
    

###########################################################################
def parse_url_set(url_set):

    domain_set = set()
    parsed_urls = list()
    result_list = list()
    response_list = list()

    # Break url list up into groups by unique domain
    for u in url_set:
        p = urlparse(u[1])
        domain_set.add(p.netloc)

    url_groups = list()
    for domain in domain_set:
        domain_url_list = list()
        for url in url_set:
            if urlparse(url[1]).netloc == domain:
                domain_url_list.append(url)
        url_groups.append(domain_url_list)
    
    t1 = time.time()
    for url_group in url_groups:
        pool = Pool(HTTP_THREADS_PER_DOMAIN)
        result_list.append(pool.map(check_url, url_group))

    for r in result_list:
        for x in r:
            response_list.append(x)

    return response_list


###########################################################################
def get_css_urls(soup):

    css_files = soup.findAll('link', {'rel': 'stylesheet'})

    css_set = set()
    for css in css_files:
        if css.has_key('href'):
            if not re.match(RE_IGNORE_DOMAINS,css['href']): 
                css_set.add(('css',css['href']))

    #print "CSS: %d" % len(css_set)

    return css_set


###########################################################################
def get_script_urls(soup):

    scripts = soup.findAll("script")
    scripts_set = set()

    for script in scripts:
        if script.has_key('src'):
            if not re.match(RE_IGNORE_DOMAINS,script['src']):
                scripts_set.add(('script',script['src']))

    #print "Scripts: %d" % len(scripts_set)

    return scripts_set


###########################################################################
def get_image_urls(soup):

    images = soup.findAll('img', {'src' : re.compile(r'(jpe?g)|(png)|(gif)$')}) 
    images_set = set()

    for img in images:
        if not re.match(RE_IGNORE_DOMAINS,img['src']):
            images_set.add(('image',img['src']))

    #print "Images: %d" % len(images_set)

    return images_set


###########################################################################
def main():

    br = mechanize.Browser()
    base_url = sys.argv[1]

    poll_start_time = time.time()

    error_message = ""
    page_title = ""
    base_request_ok = False

    t1 = time.time()
    try:
        response = br.open(base_url)
        data = response.get_data()
        assert br.viewing_html()
        base_request_ok = True

    except Exception, e:
        print e
        error_message = e

    t2 = time.time()
    
    base_url_request_time = round(t2-t1,4)

    if base_request_ok:
        base_url_request_bytes = sys.getsizeof(data)
        page_title = br.title()

        soup_data = BeautifulSoup(data)

        urls = set()
        css_urls = get_css_urls(soup_data)
        script_urls = get_script_urls(soup_data)
        image_urls = get_image_urls(soup_data)

        urls.update(css_urls)
        urls.update(script_urls)
        urls.update(image_urls)

        image_resource_count = len(css_urls)
        script_resource_count = len(script_urls)
        css_resource_count = len(image_urls)

        resource_requests = parse_url_set(urls)
    else:
        base_url_request_bytes = 0
        resource_requests = []
        image_resource_count = 0
        script_resource_count = 0
        css_resource_count = 0

        
    poll_end_time = time.time()

    poll_base_url = { 'base_url': base_url,
                      'poll_start_time': poll_start_time,
                      'poll_end_time': poll_end_time,
                      'request_time': base_url_request_time,
                      'request_bytes': base_url_request_bytes,
                      'error_message' : error_message,
                      'image_resources' : image_resource_count,
                      'script_resources' : script_resource_count,
                      'css_resources' : css_resource_count,
                      'page_title' : page_title }

    try:
        connection = pymongo.Connection('localhost')
        db = connection.litenote
        obj_id = db.poller_base_url.insert(poll_base_url)
        print "Poller Event Id: %s " % obj_id
        for resource_request in resource_requests:
            resource_request['base_url_poll_id'] = obj_id
            db.poller_resource.insert(resource_request)

    except Exception, e:
        print "Failed:", repr(e)


##########################################################################
# MAIN 
##########################################################################

if __name__ == "__main__":
    
    RE_IGNORE_DOMAINS = '.*(.twimg.com|fbcdn.net|.facebook.com|.twitter.com|.cloudfront.net).*'
    HTTP_THREADS_PER_DOMAIN = 4
    

    t1 = time.time()
    main()
    t2 = time.time()
