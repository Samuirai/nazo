from flask import json
import os
import time
from urlparse import urlparse


import config

def test_output_directory():
    output_path = "%s/" % (config.BASEDIR)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return output_path

def test_host_directory(_host):
    host_path = "%s/%s/" % (config.BASEDIR, _host)
    if test_output_directory():
        if not os.path.exists(host_path):
            os.makedirs(host_path)
    return host_path

def get_hosts():
    start = time.time()
    output_path = test_output_directory()
    hosts = []
    for host in os.listdir(output_path):
        host_path = test_host_directory(host)
        hosts.append({
                'host': host,
                'url_count': sum(1 for line in open(host_path+"urls")) if os.path.isfile(host_path+"urls") else 0,
            })
    elapsed = time.time() - start
    print "%.2f to collect %d hosts" % (elapsed, len(hosts))
    return hosts

def get_urls(_host):
    directory = test_host_directory(_host)
    urls = []
    if os.path.isfile(directory+"urls"):
        start = time.time()
        with open(directory+"urls", "r+") as f:
            urls = f.read().split("\n")
        elapsed = time.time() - start
        print "%.2f to read %d urls" % (elapsed, len(urls))
    return urls

def clear_urls(_host):
    directory = test_host_directory(_host)
    open(directory+"urls", 'w').close()

def add_urls(_host, _new_urls):
    _new_urls = list(set(_new_urls))
    directory = test_host_directory(_host)
    if directory:
        start = time.time()
        with open(directory+"urls", "a+") as f:
            old_urls = get_urls(_host)
            for new_url in _new_urls:
                for old_url in old_urls:
                    if old_url == new_url:
                        break
                else:
                    f.write(new_url+"\n")
        elapsed = time.time() - start
        print "%.2f to test and append %d urls" % (elapsed, len(_new_urls))