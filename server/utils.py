from flask import json
import os
import time
from urlparse import urlparse
import shutil

import config

def d(msg=''):
    # print msg
    pass

##############################
# Analyse Functions
##############################

def divide_in_out_urls(host, urls, num=None):
    in_urls = []
    out_urls = []
    urls.sort()
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

# TODO: SOOOO messy... Hope no future employer will ever find this in the git history
def filter_url_paths(url_paths, parser):
    _orig_url_paths = url_paths[:]
    similar = []
    same = []
    for url_path in url_paths:
        d(url_path)
        u = url_path
        url_path = urlparse(url_path).path
        d(url_path)
        index = 0
        parser_step = 0
        while parser_step<len(parser):
            step = parser[parser_step]
            d(str(step)+": "+str(index))
            if step['t']=='file':
                if (parser_step+1)<len(parser):
                    _i = url_path[index:].find(parser[parser_step+1]['s'])
                    if _i>=0:
                        index += _i
                        d("FOUND: search "+parser[parser_step+1]['s']+" found at: "+str(_i))
                    parser_step += 1
                else:
                    index += len(url_path)
                    parser_step += 1
                    break
            if step['t']=='id':
                if (parser_step+1)<len(parser):
                    _i1 = url_path[index:].find(parser[parser_step+1]['s'])
                    _i2 = url_path[index:].find("/")
                    if _i2>=0 and _i2>=_i1:
                        index += _i2
                        d("FOUND: search "+parser[parser_step+1]['s']+" found at: "+str(_i2))
                    elif _i1>=0 and _i1>_i2:
                        index += _i1
                        d("FOUND: search "+parser[parser_step+1]['s']+" found at: "+str(_i1))
                    parser_step += 1
                else:
                    _i = url_path[index:].find("/")
                    if _i>=0:
                        index += _i
                    else:
                        index += len(url_path)
                    parser_step += 1
                    break
            if step['t']=='fixed':
                d(url_path[index:index+len(step['s'])]+"=="+step['s'])
                if url_path[index:index+len(step['s'])] == step['s']:
                    d("FOUND: "+step['s']+" found")
                    index += len(step['s'])
                    parser_step += 1
                else:
                    break
            if url_path[index:]:
                d("new string: "+url_path[index:])
                d()
            else:
                break
        d(str(parser_step)+" / "+str(len(parser)))
        if parser_step == len(parser):
            d(" >>>> TAKE: "+url_path[index:])
            if url_path[index:]:
                similar.append(u)
            else:
                same.append(u)
                #url_paths.remove(u)

        d()
        d("################################################")
        d()
    for u in same:
        url_paths.remove(u)
    return url_paths

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
    return hosts

def get_file_contents(_host, filename="urls"):
    directory = test_host_directory(_host)
    lines = []
    if os.path.isfile(directory+filename):
        start = time.time()
        with open(directory+filename, "r+") as f:
            lines = f.read().split("\n")
        elapsed = time.time() - start
    if len(lines)>1 and not lines[-1]:
        return lines[0:-1]
    else:
        return lines

def clear_urls(_host):
    directory = test_host_directory(_host)
    open(directory+"urls", 'w').close()

def remove_host(_host):
    directory = test_host_directory(_host)
    shutil.rmtree(directory)

def add_urls(_host, _new_urls):
    _new_urls = list(set(_new_urls))
    directory = test_host_directory(_host)
    if directory:
        start = time.time()
        all_urls = ""
        with open(directory+"in_urls", "a+") as f:
            old_urls = get_file_contents(_host, "in_urls")
            for new_url in _new_urls:
                if urlparse(new_url).netloc == _host:
                    for old_url in old_urls:
                        if old_url == new_url:
                            break
                    else:
                        all_urls += new_url+"\n"
            f.write(all_urls)
        all_paths = ""
        with open(directory+"paths", "a+") as f:
            old_paths = get_file_contents(_host, 'paths')
            for new_url in _new_urls:
                if urlparse(new_url).netloc == _host:
                    new_path = urlparse(new_url).path

                    for old_path in old_paths:
                        if old_path == new_path:
                            break
                    else:
                        old_paths.append(new_path)
                        all_paths += new_path+"\n"
            f.write(all_paths)
        elapsed = time.time() - start

def get_url_path_filters(_host):
    directory = test_host_directory(_host)
    url_path_filters = []
    if os.path.isfile(directory+"url_path_filters"):
        with open(directory+"url_path_filters", "r+") as f:
            for f in f.read().split("\n"):
                if f:
                    url_path_filters.append(json.loads(f))
    return url_path_filters

def remove_filter(_host, id):
    url_path_filters = get_url_path_filters(_host)
    del url_path_filters[id]
    directory = test_host_directory(_host)
    with open(directory+"url_path_filters", "w") as f:
        for url_path_filter in url_path_filters:
            f.write(json.dumps(url_path_filter)+"\n")


def add_url_path_filter(_host, url_path_filter):
    print "add", url_path_filter
    directory = test_host_directory(_host)
    url_path_filters = get_url_path_filters(_host)
    if url_path_filter not in url_path_filters:
        with open(directory+"url_path_filters", "a+") as f:
            f.write(json.dumps(url_path_filter)+"\n")
        paths = []
        if os.path.isfile(directory+"paths_filtered"):
            paths = get_file_contents(_host, "paths_filtered")
        else:
            paths = get_file_contents(_host, "paths")
        paths = filter_url_paths(paths, url_path_filter)
        with open(directory+"paths_filtered", "w") as f:
            for path in paths:
                f.write(path+"\n")


