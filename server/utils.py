from flask import json
import os
import time
from urlparse import urlparse
import shutil

import config

def d(msg=''):
    #print msg
    pass

##############################
# Analyse Functions
##############################

def filter_urls(host, urls, num=None):
    in_urls = []
    out_urls = []
    for url in urls:
        parsed_url = urlparse(url)
        if parsed_url.netloc == host:
            if num==None or len(in_urls)<num:
                in_urls.append(url)
        else:
            if num==None or len(in_urls)<num:
                out_urls.append(url)

    return {'in_urls': in_urls, 'out_urls': out_urls}

def parse_urls(urls):
    path = {}
    for url in urls:
        parsed = urlparse(url)
        splitted_path = parsed.path.split("/")[1:]
        _tmp = path
        i = 0
        for s in splitted_path:
            if s not in _tmp:
                _tmp[s] = {'urls': [url]}
            _tmp = _tmp[s]
    return path

# TODO: SOOOO messy... Hope no future epmloyer will ever find this in the git history
def filter(urls, parser):
    _orig_urls = urls[:]
    similar = []
    same = []
    for url in urls:
        d(url)
        u = url
        url = urlparse(url).path
        d(url)
        index = 0
        parser_step = 0
        #print "ASD", len(parser), parser_step
        while parser_step<len(parser):
            #print "."
            step = parser[parser_step]
            d(str(step)+": "+str(index))
            if step['t']=='id':
                if (parser_step+1)<len(parser):
                    _i = url[index:].find(parser[parser_step+1]['s'])
                    if _i>=0:
                        index += _i
                        d("FOUND: search "+parser[parser_step+1]['s']+" found at: "+str(_i))
                    parser_step += 1
                else:
                    index += len(url)
                    parser_step += 1
                    break
            if step['t']=='fixed':
                d(url[index:index+len(step['s'])]+"=="+step['s'])
                if url[index:index+len(step['s'])] == step['s']:
                    d("FOUND: "+step['s']+" found")
                    index += len(step['s'])
                    parser_step += 1
                else:
                    break
            if url[index:]:
                d("new string: "+url[index:])
                d()
            else:
                break
        d(str(parser_step)+" / "+str(len(parser)))
        if parser_step == len(parser):
            d(" >>>> TAKE: "+url[index:])
            if url[index:]:
                similar.append(u)
            else:
                same.append(u)
                #urls.remove(u)

        d()
        d("################################################")
        d()
    for u in same:
        urls.remove(u)
    print similar
    print len(urls)
    return urls

##############################
# Helper Functions
##############################
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


##############################
# Main Functions
##############################
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

def delete_host(_host):
    directory = test_host_directory(_host)
    shutil.rmtree(directory)

def add_urls(_host, _new_urls):
    _new_urls = list(set(_new_urls))
    directory = test_host_directory(_host)
    if directory:
        start = time.time()
        all_urls = ""
        with open(directory+"urls", "a+") as f:
            old_urls = get_urls(_host)
            for new_url in _new_urls:
                for old_url in old_urls:
                    if old_url == new_url:
                        break
                else:
                    all_urls += new_url+"\n"
            f.write(all_urls)
        elapsed = time.time() - start
        print "%.2f to test and append %d urls" % (elapsed, len(_new_urls))