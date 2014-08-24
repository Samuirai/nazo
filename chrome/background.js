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

display_badge = function(show) {
    if(settings['server']) {
        if(show) {
            chrome.browserAction.setBadgeBackgroundColor({color:[50, 230, 50, 220]});
            chrome.browserAction.setBadgeText({text:"+"}); // 謎
        } else {
            chrome.browserAction.setBadgeText({text:""});
        }
    } else {
        chrome.browserAction.setBadgeBackgroundColor({color:[230, 50, 50, 220]});
        chrome.browserAction.setBadgeText({text:"-"}); // 謎
    }
}

focus_on_tab = function(host) {
    d("focus1: "+host)
    display_badge(false);
    if(host===undefined) {
        d("ask content script for host")
        // send message to content script to get the current window.location.host
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {action: "get_host"}, function(response) {
                d("response: "+response);
                if(response !== undefined && response.host !== undefined) {
                    tracking_active = get_url_tracking(response.host)
                    d("tracking active? "+tracking_active)
                    if(tracking_active) {
                        display_badge(true);
                    } else {
                        display_badge(false);
                    }
                }
            });
        });
    } else {
        tracking_active = get_url_tracking(host)
        d("tracking active? "+tracking_active)
        if(tracking_active) {
            display_badge(true);
        } else {
            display_badge(false);
        }
    }

    
}

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
    display_badge(true);
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
    display_badge(false);
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

server_add_forms = function(_host, _forms) {
    var request = new XMLHttpRequest();  
    request.open('POST', 'http://127.0.0.1:5000/api/add/forms/'+_host, true);
    request.setRequestHeader("Content-Type", "application/json");
    request.onload = function() {
        d(" <- Status: "+request.status+"\nreadyState: "+request.readyState);
        d(JSON.parse(request.response));
    }
    request.send(JSON.stringify({
        'forms': _forms
    }));
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

//listen for new tab to be activated
chrome.tabs.onActivated.addListener(function(activeInfo) { focus_on_tab(); });

//listen for current tab to be changed
//chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) { focus_on_tab(); });

// messages from content script
chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if (request.action == "am_i_tracked") {
        tracking_active = get_url_tracking(request.host)
        sendResponse({tracked: tracking_active});
    } else if (request.action == "track") {
        d("TRACKING...")
        _urls = [request.href]
        Array.prototype.push.apply(_urls, request.links)
        server_add_urls(request.host, _urls);
        server_add_forms(request.host, request.forms);
    }
});

server_test_connection();
