// Copyright (c) 2014 samuirai. All rights reserved.
// Use of this source code is governed by the MIT license that can be
// found in the LICENSE file.

var backgroundPage = chrome.extension.getBackgroundPage();

get_urls = function() {
    document.getElementById('urls').innerText = backgroundPage.get_urls();
}

get_url_tracking = function() {
    document.getElementById('status').innerText = backgroundPage.get_url_tracking(document.getElementById('url').value);
    get_urls();
}

add_url_tracking = function() {
    backgroundPage.add_url_tracking(document.getElementById('url').value);
    get_urls();
}

clear_storage = function() {
    backgroundPage.clean_storage();
    get_urls();
}

remove_url_tracking = function() {
    backgroundPage.remove_url_tracking(document.getElementById('url').value);
    get_urls();
}

document.addEventListener('DOMContentLoaded', function(){
    get_urls();
    document.getElementById('get_urls').addEventListener('click', get_urls);
    document.getElementById('add_url_tracking').addEventListener('click', add_url_tracking);
    document.getElementById('get_url_tracking').addEventListener('click', get_url_tracking);
    document.getElementById('clear_storage').addEventListener('click', clear_storage);
    document.getElementById('remove_url_tracking').addEventListener('click', remove_url_tracking);
});