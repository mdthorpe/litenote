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

    for results in result_list:
        for result in results:
            print result


###########################################################################
def get_css_urls(soup):

    css_files = soup.findAll('link', {'rel': 'stylesheet'})

    css_set = set()
    for css in css_files:
        if css.has_key('href'):
            if not re.match(RE_IGNORE_DOMAINS,css['href']): 
                css_set.add(('css',css['href']))

    print "CSS: %d" % len(css_set)

    return css_set


###########################################################################
def get_script_urls(soup):

    scripts = soup.findAll("script")
    scripts_set = set()

    for script in scripts:
        if script.has_key('src'):
            if not re.match(RE_IGNORE_DOMAINS,script['src']):
                scripts_set.add(('script',script['src']))

    print "Scripts: %d" % len(scripts_set)

    return scripts_set


###########################################################################
def get_image_urls(soup):

    images = soup.findAll('img', {'src' : re.compile(r'(jpe?g)|(png)|(gif)$')}) 
    images_set = set()

    for img in images:
        if not re.match(RE_IGNORE_DOMAINS,img['src']):
            images_set.add(('image',img['src']))

    print "Images: %d" % len(images_set)

    return images_set


###########################################################################
def main():

    br = mechanize.Browser()


    try:
        t1 = time.time()
        response = br.open(sys.argv[1])
        data = response.get_data()
        assert br.viewing_html()
        t2 = time.time()
        print "\n** Title: %s [%0.3fs] [%d bytes]" % (br.title() , round(t2-t1,4), sys.getsizeof(data))

    except Exception, e:
        print e
        sys.exit(1)

    soup_data = BeautifulSoup(data)

    urls = set()
    urls.update(get_css_urls(soup_data))
    urls.update(get_script_urls(soup_data))
    urls.update(get_image_urls(soup_data))
    parse_url_set(urls)


##########################################################################
# MAIN 
##########################################################################

if __name__ == "__main__":
    
    RE_IGNORE_DOMAINS = '.*(.twimg.com|fbcdn.net|.facebook.com|.twitter.com|.cloudfront.net).*'
    HTTP_THREADS_PER_DOMAIN = 4
    

    t1 = time.time()
    main()
    t2 = time.time()
    print "Total Wall Time: %0.3fs" % (t2-t1)
