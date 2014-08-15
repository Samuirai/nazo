// Copyright (c) 2014 samuirai. All rights reserved.
// Use of this source code is governed by the MIT license that can be
// found in the LICENSE file.

d = function(_msg) {
    console.log(_msg);
}

get_all_links = function() {
    var _as = document.links;
    var _links = [];
    for(var i=0; i<_as.length; ++i) {
        _links.push(_as[i].href);
    }
    return _links;
}

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    console.log("Request: "+request.action);
    if (request.action == 'get_host') {
        console.log("send: "+window.location.host);
        sendResponse({host: window.location.host});
    }
});


chrome.runtime.sendMessage({action: "am_i_tracked", host: window.location.host}, function(response) {
    if(response.tracked) {
        d("[謎]nazo is tracking this site");
        chrome.runtime.sendMessage({
                action: "track", 
                href: window.location.href,
                host: window.location.host,
                links: get_all_links(),
            }, function() {});
    }
});