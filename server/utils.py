from flask import json

from urlparse import urlparse
import os
import time
import shutil
import difflib

import config

def d(msg=''):
    # print msg
    pass

######################################################################################################################################################
# Analyse Functions
######################################################################################################################################################

def diff_string(a, b):
    s = difflib.SequenceMatcher(None,a,b)
    last_block = None
    diff = []
    for block in s.get_matching_blocks():
        if last_block:
            diff.append({'s': a[last_block[0]+last_block[2]:block[0]], 'm': False})

        diff.append({'s': a[block[0]:block[0]+block[2]], 'm': True})
        last_block = block
    return diff

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

def parse_url_parameters(urls):
    urls.sort()
    parameters = []
    for url in urls:
        parsed_url = urlparse(url)
        splitted_query = parsed_url.query.split("&")
        query = {}
        for key_value in splitted_query:
            if "=" in key_value:
                (key,value) = key_value.split("=")
            else:
                (key,value) = key_value,""
            if key in query:
                if value not in query[key]:
                    query[key].append(value)
            else:   
                query[key] = [value]
        #print parameters
        for parameter in parameters:
            if parameter['p'] == parsed_url.path:
                for key in parameter['q']:
                    if key in query:
                        parameter['q'][key] += query[key]
                        parameter['q'][key] = list(set(parameter['q'][key]))
                break
        else:
            parameters.append({'p': parsed_url.path, 'q': query, 'e': url})
    return parameters

######################################################################################################################################################
# Helper Functions
######################################################################################################################################################
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


######################################################################################################################################################
# Main Functions
######################################################################################################################################################
def get_hosts():
    start = time.time()
    output_path = test_output_directory()
    hosts = []
    for host in os.listdir(output_path):
        host_path = test_host_directory(host)
        hosts.append({
                'host': host,
                'in_urls_count': sum(1 for line in open(host_path+"in_urls")) if os.path.isfile(host_path+"in_urls") else 0,
                'paths_count': sum(1 for line in open(host_path+"paths")) if os.path.isfile(host_path+"paths") else 0,
                'paths_filtered_count': sum(1 for line in open(host_path+"paths_filtered")) if os.path.isfile(host_path+"paths_filtered") else 0,
                'forms_count': sum(1 for line in open(host_path+"forms")) if os.path.isfile(host_path+"forms") else 0,
                'cookies_count': sum(1 for line in open(host_path+"cookies")) if os.path.isfile(host_path+"cookies") else 0,
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

def get_forms(_host):
    forms = []
    directory = test_host_directory(_host)
    if directory:
        if os.path.isfile(directory+"forms"):
            with open(directory+"forms", "r") as f:
                lines = f.read().split("\n")
                for line in lines:
                    print line
                    if line:
                        forms.append(json.loads(line))
    return forms

def get_cookies(_host):
    all_cookies = []
    directory = test_host_directory(_host)
    if directory:
        if os.path.isfile(directory+"cookies"):
            with open(directory+"cookies", "r") as f:
                last_cookie = {}
                for cookies in f.read().split("\n"):
                    if cookies:
                        _cookies = {}
                        _this_cookie = {}
                        for cookie in cookies.split(";"):
                            eq_pos = cookie.find("=")
                            key, value = cookie[0:eq_pos].strip(), cookie[eq_pos+1:].strip()
                            if key in last_cookie:
                                _cookies[key] = diff_string(value, last_cookie[key])
                            else:
                                _cookies[key] = diff_string(value, value)
                            _this_cookie[key] = value
                        last_cookie = _this_cookie;
                        all_cookies.append(_cookies)
    return all_cookies


def add_cookie(_host, _cookie):
    directory = test_host_directory(_host)
    if directory:
        old_cookies = get_file_contents(_host, "cookies")
        with open(directory+"cookies", "a+") as f:
            for old_cookie in old_cookies:
                print old_cookie, _cookie
                if _cookie==old_cookie:
                    print "found same"
                    break
            else:
                f.write(_cookie+"\n")

def add_forms(_host, _new_forms):
    directory = test_host_directory(_host)
    if directory:
        all_forms = []
        old_forms = get_file_contents(_host, "forms")
        with open(directory+"forms", "w") as f:
            _old_forms = []
            for old_form in old_forms:
                if old_form:
                    _old_forms.append(json.loads(old_form))
            forms = _new_forms+_old_forms
            _final_forms = []
            for f1 in xrange(0,len(forms)):
                for f2 in xrange(f1+1,len(forms)):
                    form1 = forms[f1]
                    form2 = forms[f2]
                    if form1 and form2:
                        if set([input1["name"] for input1 in form1['inputs']]) == set([input2["name"] for input2 in form2['inputs']]):
                            for input1 in form1['inputs']:
                                for input2 in form2['inputs']:
                                    if input1['name'] == input2['name']:
                                        input1['value']+=input2['value']
                                        input1['value']=list(set(input1['value']))
                                        print "merged and now remove"
                                        forms[f2]=None
                            form1['action']+=form2['action']
                            form1['action']=list(set(form1['action']))

                _final_forms.append(form1)
            all_forms = []
            for form in forms:
                if form and (form['action'] or form['inputs']):
                    all_forms.append(json.dumps(form))
            f.write("\n".join(all_forms)+"\n")

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
        all_paths = []
        with open(directory+"paths", "a+") as f:
            url_path_filters = get_url_path_filters(_host)
            old_paths = get_file_contents(_host, 'paths')
            for new_url in _new_urls:
                if urlparse(new_url).netloc == _host:

                    new_path = urlparse(new_url).path

                    for old_path in old_paths:
                        if old_path == new_path:
                            break
                    else:
                        old_paths.append(new_path)
                        all_paths.append(new_path)

            f.write("\n".join(all_paths))
        with open(directory+"paths_filtered", "a+") as f:
            for url_path_filter in url_path_filters:
                all_paths = filter_url_paths(all_paths, url_path_filter)
            print "new paths", "\n".join(all_paths)
            f.write("\n".join(all_paths))
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

def get_urls_with_parameters(_host):
    directory = test_host_directory(_host)
    urls = get_file_contents(_host, "in_urls")
    urls_return = []
    for url in urls:
        parsed_url = urlparse(url)
        #print parsed_url.query
        if parsed_url.query:
            urls_return.append(url)
    return urls_return

