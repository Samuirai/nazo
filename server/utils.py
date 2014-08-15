from flask import json
import os
import time
from urlparse import urlparse


import config

def test_host_directory(_host):
    if _host:
        if not os.path.exists("%s/" % (config.BASEDIR)):
            os.makedirs("%s/" % (config.BASEDIR))
        if not os.path.exists("%s/%s/" % (config.BASEDIR, _host)):
            os.makedirs("%s/%s/" % (config.BASEDIR, _host))
        return "%s/%s/" % (config.BASEDIR, _host)
    else:
        return None


def get_urls(_host):
    directory = test_host_directory(_host)
    urls = []
    with open(directory+"urls", "r+") as f:
        for url in f.read().split("\n"):
            if url:
                urls.append(json.loads(url))
    return urls

def url_to_dict(_url):
    o = urlparse(_url)
    return {
            'scheme': o.scheme,
            'host': o.hostname,
            'path': o.path,
            'params': o.params,
            'query': o.query,
            'fragment': o.fragment,
            'username': o.username,
            'password': o.password,
            'added': int(time.time()),
            'locked': False,
        }

def url_to_json(_url):
    return json.dumps(url_to_dict(_url))

def clear_urls(_host):
    directory = test_host_directory(_host)
    open(directory+"urls", 'w').close()

def add_urls(_host, _new_urls):
    directory = test_host_directory(_host)
    if directory:
        with open(directory+"urls", "a+") as f:
            old_json_urls = get_urls(_host)
            for new_url in _new_urls:
                new_json_url = url_to_dict(new_url)
                for old_json_url in old_json_urls:
                    if old_json_url["locked"] == False \
                        and old_json_url["path"] == new_json_url["path"] \
                        and old_json_url["params"] == new_json_url["params"] \
                        and old_json_url["query"] == new_json_url["query"] \
                        and old_json_url["fragment"] == new_json_url["fragment"]:
                        break
                    elif old_json_url["locked"] == True \
                        and old_json_url["path"] == new_json_url["path"]:
                        break
                else:
                    f.write(url_to_json(new_url)+"\n")