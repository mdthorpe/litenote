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

# -------------------------------------------------- 
def check_url(browser, url):
    error_message = ""
    try:
        fullurl = quote(url, safe="%/:=&?~#+!$,;'@()*[]")
        response = browser.open(fullurl)
        error_code = 200
        if browser.response().info().getheader('Content-length'):
            size_of = browser.response().info().getheader('Content-length')
        else:
            size_of = sys.getsizeof(response.read())

    except HTTPError, e:
        error_code = e.code
        size_of = 0

    error_message = "%s\n%s\n%s\n" % (browser.request.get_full_url(), browser.response().info(), str(browser.response()) )

    return {'error_code': error_code, 'bytes': int(size_of), 'error_message': error_message}

# -------------------------------------------------- 
def parse_url_set(url_set):
    for url in url_set:
        if not re.match(re_ignore_domains,url):
            t1 = time.time()
            result = check_url(br, url)
            t2 = time.time()
            print "[%s] [%0.2fs] [%s bytes] %s " % (str(result['error_code']).center(5), 
                                                    t2-t1, str(result['bytes']).rjust(8), url)
            if result['error_code'] != 200:
                print result['error_message']
        else:
            next
            #print "[%s] [%0.2fs] [%s bytes] %s " % (str('---').center(5), 
            #                                        0, str(0).rjust(8), url)

# -------------------------------------------------- 
def main():
    """
    MAIN FUNCTION
    """

re_ignore_domains = '.*(.twimg.com|fbcdn.net|.facebook.com|.twitter.com|.cloudfront.net).*'

br = mechanize.Browser()
data = ""

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

soup = BeautifulSoup(data)

# CSS Files
css_files = soup.findAll('link', {'rel': 'stylesheet'})

css_set = set()
for css in css_files:
    if css.has_key('href'):
        css_set.add(css['href'])

print "\nEmbeded CSS  --- Total: %s" % (len(css_set))
parse_url_set(css_set)

# JS Files
scripts = soup.findAll("script")

scripts_set = set()
for script in scripts:
    if script.has_key('src'):
        scripts_set.add(script['src'])

print "\nEmbeded JS  --- Total: %s" % (len(scripts_set))
parse_url_set(scripts_set)

#### Images
images = soup.findAll('img', {'src' : re.compile(r'(jpe?g)|(png)|(gif)$')}) 

images_set = set()
for img in images:
    images_set.add(img['src'])

print "\nEmbeded Images  --- Total: %s" % (len(images_set))
parse_url_set(images_set)

#-------------------------------
# MAIN 
#-------------------------------

if __name__ == "__main__":
    main()
