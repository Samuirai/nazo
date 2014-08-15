// Copyright (c) 2014 samuirai. All rights reserved.
// Use of this source code is governed by the MIT license that can be
// found in the LICENSE file.

var backgroundPage = chrome.extension.getBackgroundPage();

_get_urls = function() {
    document.getElementById('urls').innerText = backgroundPage.get_urls();
}

_get_url_tracking = function() {
    document.getElementById('status').innerText = backgroundPage.get_url_tracking(document.getElementById('url').value);
    _get_urls();
}

_add_url_tracking = function() {
    backgroundPage.add_url_tracking(document.getElementById('url').value);
    _get_urls();
}

_clear_storage = function() {
    backgroundPage.clean_storage();
    _get_urls();
}

_remove_url_tracking = function() {
    backgroundPage.remove_url_tracking(document.getElementById('url').value);
    _get_urls();
}

document.addEventListener('DOMContentLoaded', function(){
    _get_urls();
    document.getElementById('get_urls').addEventListener('click', _get_urls);
    document.getElementById('add_url_tracking').addEventListener('click', _add_url_tracking);
    document.getElementById('get_url_tracking').addEventListener('click', _get_url_tracking);
    document.getElementById('clear_storage').addEventListener('click', _clear_storage);
    document.getElementById('remove_url_tracking').addEventListener('click', _remove_url_tracking);
});