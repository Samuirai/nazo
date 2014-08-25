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

get_all_forms = function() {
    var forms = document.forms;
    var formdata = Array()
    for(var i=0; i<forms.length; ++i) {
        _tmp_formdata = {'method': forms[i].method, 'action': [forms[i].action], 'inputs': Array()};
        
        var inputs = forms[i].getElementsByTagName('input');
        for(var j=0; j<inputs.length; ++j) {
            _tmp_formdata['inputs'].push({'type': inputs[j].type, 'name': inputs[j].name, 'value': [inputs[j].value]});
        }

        var inputs = forms[i].getElementsByTagName('textarea');
        for(var j=0; j<inputs.length; ++j) {
            _tmp_formdata['inputs'].push({'type': "textarea", 'name': inputs[j].name, 'value': [inputs[j].value]});
        }

        formdata.push(_tmp_formdata);
    }
    return formdata
}

gather_tracking_info = function() {
    return {
            action: "track", 
            href: window.location.href,
            host: window.location.host,
            links: get_all_links(),
            forms: get_all_forms(),
            cookie: document.cookie,
        }
}


chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    d("Request: "+request.action);
    if (request.action == 'get_host') {
        sendResponse({ host: window.location.host });
    } else if (request.action == 'track') {
        chrome.runtime.sendMessage(gather_tracking_info(), function() {});
    }
});


chrome.runtime.sendMessage({action: "am_i_tracked", host: window.location.host}, function(response) {
    if(response.tracked) {
        d("[謎]nazo is tracking this site");
        chrome.runtime.sendMessage(gather_tracking_info(), function() {});
    }
});

get_all_forms();