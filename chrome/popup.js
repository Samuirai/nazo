// Copyright (c) 2014 samuirai. All rights reserved.
// Use of this source code is governed by the MIT license that can be
// found in the LICENSE file.

var backgroundPage = chrome.extension.getBackgroundPage();
var host;
_get_url_tracking = function() {

    // send message to content script to get the current window.location.host
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action: "get_host"}, function(response) {
            console.log(response);
            if(response !== undefined && response.host !== undefined) {
                host = response.host;
                backgroundPage.get_url_tracking(response.host);
                document.getElementById('status').innerText = response.host+" ("+backgroundPage.get_url_tracking(response.host)+")";
            }
        });
    });
  
}

_add_url_tracking = function() {
    if(host===undefined) {
        _get_url_tracking();  
    }
    if(host!==undefined) {
        console.log("add new")
        backgroundPage.add_url_tracking(host);
        _get_url_tracking();
    }
}

_remove_url_tracking = function() {
    if(host===undefined) {
        _get_url_tracking();  
    }
    if(host!==undefined) {
        console.log("remove")
        backgroundPage.remove_url_tracking(host);
        _get_url_tracking();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    _get_url_tracking();
    document.getElementById('status').addEventListener('click', _get_url_tracking);
    document.getElementById('track').addEventListener('click', _add_url_tracking);
    document.getElementById('remove').addEventListener('click', _remove_url_tracking);
});


