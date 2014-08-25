from flask import Flask
from flask import json
from flask import request
from flask import Response
from flask import render_template

import os
import urllib

import config
import utils

app = Flask(__name__)


@app.template_filter('urldecode')
def urldecode_filter(s):
    return urllib.unquote(s).decode('utf8') 

@app.context_processor
def global_variables():
    hosts = utils.get_hosts()
    return dict(hosts=hosts)

@app.route('/')
def index():
    return 'working asd'

# /about
# display an about page
@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html')

# /tutorial
# display a tutorial page
@app.route('/tutorial', methods = ['GET'])
def tutorial():
    return render_template('tutorial.html')

# /get/urls/www.example.com
@app.route('/get/hosts', methods = ['GET'])
def get_hosts():
    hosts = utils.get_hosts()
    return render_template('get_hosts.html', hosts=hosts)

# /get/host/www.example.com
@app.route('/get/host/<host>', methods = ['GET'])
def get_host(host):
    return render_template('host_overview.html', host=host)

# /get/urls/www.example.com
@app.route('/get/urls/<host>', methods = ['GET'])
def get_urls(host):
    urls = utils.get_file_contents(host, "in_urls")
    return render_template('get_urls.html', urls=urls, host=host)

# /analyse/forms/www.example.com
@app.route('/analyse/forms/<host>', methods = ['GET'])
def analyse_forms(host):
    forms = utils.get_forms(host)
    return render_template('analyse_forms.html', forms=forms, host=host)

# /analyse/cookies/www.example.com
@app.route('/analyse/cookies/<host>', methods = ['GET'])
def analyse_cookies(host):
    cookies = utils.get_cookies(host)
    return render_template('analyse_cookies.html', cookies=cookies, host=host)

# /analyse/paths/www.example.com
@app.route('/analyse/paths/<host>', methods = ['GET'])
def analyse_paths(host):

    directory = utils.test_host_directory(host)
    filters = utils.get_url_path_filters(host)
    if os.path.isfile(directory+"paths_filtered"):
        print "paths_filtered exists"
        paths = utils.get_file_contents(host, "paths_filtered")
    else:
        print "paths_filtered doesn't exists"
        paths = utils.get_file_contents(host, "paths")
    paths.sort()
    return render_template('analyse_paths.html', paths=paths, host=host, num_all_paths=len(paths), filters=filters)

# /analyse/parameters/www.example.com
@app.route('/analyse/parameters/<host>', methods = ['GET'])
def analyse_parameters(host):
    print "asd"
    urls = utils.get_urls_with_parameters(host)
    parameters = utils.parse_url_parameters(urls)
    return render_template('analyse_parameters.html', parameters=parameters, host=host)


#########################
# API
#########################

# /api/ping
# returns "pong". Used to test if server is running.
@app.route('/api/ping')
def api_ping():
    return Response(json.dumps({'ping': 'pong'}), status=200, mimetype='application/json')


# /api/get/urls/www.example.com
# get all urls for this host
@app.route('/api/get/urls/<host>', methods = ['GET'])
def api_get_urls(host):
    urls = utils.get_file_contents(host, "in_urls")
    return Response(json.dumps({'status': 'OK', 'urls': urls}), status=200, mimetype='application/json')


# /api/add/urls/www.example.com
# POST: {"urls": ["...", ...]}
# add a bunch of urls to a host
@app.route('/api/add/urls/<host>', methods = ['POST'])
def api_add_urls(host):
    if request.headers['Content-Type'] == 'application/json':
        utils.add_urls(host, request.json["urls"])
        return Response(json.dumps({'status': 'OK'}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'error', 'reason': 'Unsupported Media Type'}), status=415, mimetype='application/json')

# /api/add/forms/www.example.com
# POST: {"forms": ["...", ...]}
# add a bunch of forms to a host
@app.route('/api/add/forms/<host>', methods = ['POST'])
def api_add_forms(host):
    if request.headers['Content-Type'] == 'application/json':
        utils.add_forms(host, request.json["forms"])
        return Response(json.dumps({'status': 'OK'}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'error', 'reason': 'Unsupported Media Type'}), status=415, mimetype='application/json')

# /api/add/cookie/www.example.com
# POST: {"cookie": "..."}
# add a cookie to a host
@app.route('/api/add/cookie/<host>', methods = ['POST'])
def api_add_cookie(host):
    if request.headers['Content-Type'] == 'application/json':
        utils.add_cookie(host, request.json["cookie"])
        return Response(json.dumps({'status': 'OK'}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'error', 'reason': 'Unsupported Media Type'}), status=415, mimetype='application/json')


# /api/test_filter/paths/www.example.com
# POST: [{"u": "", "t": "fixed"}, ... ]
# add a bunch of urls to a host
@app.route('/api/test_filter/paths/<host>', methods = ['POST'])
def api_test_filter_paths(host):
    if request.headers['Content-Type'] == 'application/json':
        
        print request.json["filter"]
        paths = []
        directory = utils.test_host_directory(host)
        if os.path.isfile(directory+"paths_filtered"):
            paths = utils.get_file_contents(host, "paths_filtered")
        else:
            paths = utils.get_file_contents(host, "paths")

        pre_filter_num = len(paths)
        paths = utils.filter_url_paths(paths, request.json["filter"])
        post_filter_num = len(paths)

        return Response(json.dumps({'status': 'OK', 'filters': utils.get_url_path_filters(host), 'pre_filter_num': pre_filter_num, "post_filter_num": post_filter_num}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'error', 'reason': 'Unsupported Media Type'}), status=415, mimetype='application/json')


# /api/filter/paths/www.example.com
# POST: [{"u": "", "t": "fixed"}, ... ]
# add a bunch of urls to a host
@app.route('/api/filter/paths/<host>', methods = ['POST'])
def api_filter_paths(host):
    if request.headers['Content-Type'] == 'application/json':

        print request.json["filter"]
        utils.add_url_path_filter(host, request.json["filter"])
    
        return Response(json.dumps({'status': 'OK', 'filters': utils.get_url_path_filters(host) }), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'error', 'reason': 'Unsupported Media Type'}), status=415, mimetype='application/json')

# /api/split/urls/host
# POST: {"urls": "<all>"}
# POST: {"urls": ["...", ...]}
# urlparse urls
@app.route('/api/split/urls/<host>', methods = ['POST'])
def api_split_urls(host):

    if request.headers['Content-Type'] == 'application/json':
        if request.json["urls"] == '<all>':
            urls = utils.get_file_contents(host)
            urls = utils.divide_in_out_urls(host, urls)['in_urls']
            return Response(json.dumps({'status': 'OK', 'urls': utils.parse_urls(urls)}), status=200, mimetype='application/json')
        else:
            return Response(json.dumps({'status': 'error', 'reason': 'not implemented'}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'error', 'reason': 'Unsupported Media Type'}), status=415, mimetype='application/json')

# /api/remove/path_filter/<host>
# POST: {"urls": "<all>"}
# POST: {"urls": ["...", ...]}
# urlparse urls
@app.route('/api/remove/filter/path/<host>', methods = ['POST'])
def api_remove_filter_path(host):

    if request.headers['Content-Type'] == 'application/json':
        if request.json["filter"]:
            utils.remove_filter(host, request.json["filter"])
            return Response(json.dumps({'status': 'OK'}), status=200, mimetype='application/json')
        else:
            return Response(json.dumps({'status': 'error', 'reason': 'not implemented'}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'error', 'reason': 'Unsupported Media Type'}), status=415, mimetype='application/json')

# /api/remove/urls/www.example.com
# POST: {"urls": "<all>"}
# POST: {"urls": ["...", ...]}
# remove a bunch of urls for a host
@app.route('/api/remove/urls/<host>', methods = ['POST'])
def api_remove_urls(host):

    if request.headers['Content-Type'] == 'application/json':
        if request.json["urls"] == '<all>':
            utils.clear_urls(host)
            return Response(json.dumps({'status': 'OK'}), status=200, mimetype='application/json')
        else:
            return Response(json.dumps({'status': 'error', 'reason': 'not implemented'}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'error', 'reason': 'Unsupported Media Type'}), status=415, mimetype='application/json')

# /api/remove/host/www.example.com
# POST
# remove a host
@app.route('/api/remove/host/<host>', methods = ['POST'])
def api_remove_host(host):
    utils.remove_host(host)
    return Response(json.dumps({'status': 'OK'}), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)