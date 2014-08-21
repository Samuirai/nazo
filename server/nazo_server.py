from flask import Flask
from flask import json
from flask import request
from flask import Response
from flask import render_template

import os

import config
import utils

app = Flask(__name__)

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

# /get/urls/www.example.com
@app.route('/get/urls/<host>', methods = ['GET'])
def get_urls(host):
    urls = utils.get_urls(host)
    return render_template('get_urls.html', urls=urls, host=host)

# /analyse/urls/www.example.com
@app.route('/analyse/urls/<host>', methods = ['GET'])
def analyse_urls(host):
    urls = utils.get_urls(host)
    filterd_urls = utils.filter_urls(host, urls, 200)
    sliced = False
    if len(urls)>200:
        sliced = True
    return render_template('analyse_urls.html', urls=urls, filterd_urls=filterd_urls, host=host, sliced=sliced, num_all_urls=len(urls))


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
    urls = utils.get_urls(host)
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

# /api/test_filter/urls/www.example.com
# POST: [{"u": "", "t": "fixed"}, ... ]
# add a bunch of urls to a host
@app.route('/api/test_filter/urls/<host>', methods = ['POST'])
def api_test_filter_urls(host):
    if request.headers['Content-Type'] == 'application/json':
        
        print request.json["filter"]
        urls = utils.get_urls(host)

        filterd_urls = utils.filter_urls(host, urls)
        pre_filter_num = len(filterd_urls["in_urls"])
        urls = utils.filter(filterd_urls["in_urls"], request.json["filter"])
        post_filter_num = len(urls)

        return Response(json.dumps({'status': 'OK', 'pre_filter_num': pre_filter_num, "post_filter_num": post_filter_num}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'status': 'error', 'reason': 'Unsupported Media Type'}), status=415, mimetype='application/json')


# /api/filter/urls/www.example.com
# POST: [{"u": "", "t": "fixed"}, ... ]
# add a bunch of urls to a host
@app.route('/api/filter/urls/<host>', methods = ['POST'])
def api_filter_urls(host):
    if request.headers['Content-Type'] == 'application/json':
        
        print request.json["filter"]
        urls = utils.get_urls(host)

        filterd_urls = utils.filter_urls(host, urls)
        pre_filter_num = len(filterd_urls["in_urls"])
        urls = utils.filter(filterd_urls["in_urls"], request.json["filter"])
        post_filter_num = len(urls)

        return Response(json.dumps({'status': 'OK', 'pre_filter_num': pre_filter_num, "post_filter_num": post_filter_num}), status=200, mimetype='application/json')
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
            urls = utils.get_urls(host)
            urls = utils.filter_urls(host, urls)['in_urls']
            return Response(json.dumps({'status': 'OK', 'urls': utils.parse_urls(urls)}), status=200, mimetype='application/json')
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
    utils.delete_host(host)
    return Response(json.dumps({'status': 'OK'}), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)