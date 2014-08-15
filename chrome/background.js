// Copyright (c) 2014 samuirai. All rights reserved.
// Use of this source code is governed by the MIT license that can be
// found in the LICENSE file.

var settings={};

d = function(_msg) {
    console.log(_msg);
}

load_settings = function() {
    settings = JSON.parse(localStorage.getItem('nazo'));
    settings['working'] = true;
    d("load_settings: "+JSON.stringify(settings));
}

save_settings = function() {
    d("save_settings: "+JSON.stringify(settings));
    localStorage.setItem('nazo', JSON.stringify(settings));
    settings['working'] = true;
}

// messages from content script
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if (request.action == "am_i_tracked") {
        sendResponse({tracked: get_url_tracking(request.host)});
    } else if (request.action == "track") {
        console.log("TRACKING...")
        _urls = [request.href]
        Array.prototype.push.apply(_urls, request.links)
        server_add_urls(request.host, _urls);
    }
});


// define loalStorage interface
url_in_tracking = function(_url) {
    d("url_in_tracking: "+_url);
    load_settings();
    var match = [];
    for(var i=0; i<settings['tracking'].length; ++i) {
        _element = settings['tracking'][i]
        if(_url.slice(-_element.length)==_element) {
            match.push(i);
        }
    }
    d(" <- "+match);
    return match;
}

get_url_tracking =  function(_url) {
    d("get_url_tracking: "+_url);
    load_settings();
    return url_in_tracking(_url).length?true:false;
}

add_url_tracking = function(_url) {
    d("add_url_tracking: "+_url);
    load_settings();
    if(url_in_tracking(_url).length==0) {
        var match = [];
        for(var i=0; i<settings['tracking'].length; ++i) {
            _element = settings['tracking'][i]
            
            if(_element.slice(-_url.length)==_url) {
                match.push(i) 
            }
        }
        match.reverse()
        for(var i=0; i<match.length; ++i) {
            settings['tracking'].splice(match[i], 1);
        }
        d("add_url_tracking: push <- "+_url);
        settings['tracking'].push(_url)
    }
    save_settings();
}

remove_url_tracking = function(_url) {
    d("remove_url_tracking: "+_url);
    load_settings();
    var _ids = url_in_tracking(_url);
    _ids.reverse();
    for(var i=0; i<_ids.length; ++i) {
        settings['tracking'].splice(_ids[i], 1);
    }
    save_settings();
}

get_urls = function() {
    d("get_urls: ");
    load_settings();
    return settings['tracking']
}

clean_storage = function() {
    d("clean_storage: ");
    localStorage.clear();
    settings = {
        'tracking': [],
        'working': false,
        'server': false,
    }
    save_settings();
}


// client/server api interface
server_test_connection = function() {
    d("server_test_connection: ");
    var request = new XMLHttpRequest();  
    request.open('GET', 'http://127.0.0.1:5000/api/ping', true);
    request.onload = function() {
        response = JSON.parse(request.response);
        if(response!==undefined && response.ping=='pong') {
            load_settings();
            settings['server'] = true;
            save_settings();
        }
        d(response);
    }
    request.send();
}

server_add_urls = function(_host, _urls) {
    d("server_add_url: "+_urls);
    var request = new XMLHttpRequest();  
    request.open('POST', 'http://127.0.0.1:5000/api/add/urls/'+_host, true);
    request.setRequestHeader("Content-Type", "application/json");
    request.onload = function() {
        d(" <- Status: "+request.status+"\nreadyState: "+request.readyState);
        d(JSON.parse(request.response));
    }
    request.send(JSON.stringify({
        'urls': _urls
    }));
}

// init localStorage/settings
if(localStorage['nazo']===undefined) {
    clean_storage();
} else {
    load_settings();
}

server_test_connection()
