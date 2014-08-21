// Copyright (c) 2014 samuirai. All rights reserved.
// Use of this source code is governed by the MIT license that can be
// found in the LICENSE file.

var host;
var tracked = false;
var server_error = false;

d = function(_msg) {
    console.log(_msg);
}

update_tracking_status = function() {
    var main_panel = document.getElementById("main_panel");
    var main_panel_title = document.getElementById("main_panel_title");
    var track_button = document.getElementById("track_button");
    var rescan_button = document.getElementById("rescan_button");
    var eye_icon = document.getElementById("eye_icon");
    var server_get_urls = document.getElementById('server_get_urls');

    document.getElementById('host').innerText = host;
    if(server_error) {
        main_panel.className = "panel panel-warning";
        main_panel_title.innerText = "[謎]nazo - no server connection";
        rescan_button.className = "btn btn-warning btn-xs";
        track_button.className = "btn btn-warning btn-xs";
        eye_icon.className = "glyphicon glyphicon-eye-close";
        server_get_urls.classList.add("disabled");
    } else {
        if(tracked) {
            main_panel.className = "panel panel-success";
            main_panel_title.innerText = "[謎]nazo - tracking enabled";
            rescan_button.className = "btn btn-success btn-xs";
            track_button.className = "btn btn-success btn-xs";
            eye_icon.className = "glyphicon glyphicon-eye-open";
            server_get_urls.classList.remove("disabled");
        } else {
            main_panel.className = "panel panel-danger";
            main_panel_title.innerText = "[謎]nazo - tracking disabled";
            rescan_button.className = "btn btn-danger btn-xs";
            track_button.className = "btn btn-danger btn-xs";
            eye_icon.className = "glyphicon glyphicon-eye-close";
        server_get_urls.classList.add("disabled");
        }
    }
}

get_url_tracking = function() {
    host = "unknown";
    // send message to content script to get the current window.location.host
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action: "get_host"}, function(response) {
            console.log(response);
            if(response !== undefined && response.host !== undefined) {
                host = response.host;
                chrome.runtime.getBackgroundPage(function(backgroundPage) {
                    tracked = backgroundPage.get_url_tracking(response.host);
                    update_tracking_status();
                });

            }
        });
    });
  
}

rescan_site = function() {
    // send message to content script to get the current window.location.host
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action: "track"}, function(response) {
            console.log(response);
        });
    });
}


track_button_click = function() {
    if(host===undefined) {
        get_url_tracking();  
    }
    if(tracked) {
        if(host!==undefined) {
            console.log("remove");
            chrome.runtime.getBackgroundPage(function(backgroundPage) {
                backgroundPage.remove_url_tracking(host);
                get_url_tracking();
            });
            
        }
    } else {
        if(host!==undefined) {
            console.log("add new");
            chrome.runtime.getBackgroundPage(function(backgroundPage) {
                backgroundPage.add_url_tracking(host);
                get_url_tracking();
            });
        }
    }
}

server_test_connection = function() {
    d("server_test_connection: ");
    var request = new XMLHttpRequest();  
    request.open('GET', 'http://127.0.0.1:5000/api/ping', true);
    request.onload = function() {
        response = JSON.parse(request.response);
        if(response!==undefined && response.ping=='pong') {
            server_error = false;
            update_tracking_status();
        } else {
            server_error = true;
        }
        d(response);
    }
    request.onerror = function() {
        server_error = true;
    }
    request.send();
}

open_url = function(url) {
  chrome.tabs.create({ url: url });
}

document.addEventListener('DOMContentLoaded', function() {
    get_url_tracking();
    server_test_connection();
    document.getElementById('track_button').addEventListener('click', track_button_click);
    document.getElementById('rescan_button').addEventListener('click', rescan_site);
    document.getElementById('server_get_urls').addEventListener('click', function() { open_url("http://127.0.0.1:5000/get/urls/"+host) });
    document.getElementById('server_get_hosts').addEventListener('click', function() { open_url("http://127.0.0.1:5000/get/hosts") });
    //document.getElementById('status').addEventListener('click', get_url_tracking);
});


