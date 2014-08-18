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
        return Response(json.dumps({'error': 'Unsupported Media Type'}), status=415, mimetype='application/json')


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
        return Response(json.dumps({'error': 'Unsupported Media Type'}), status=415, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)