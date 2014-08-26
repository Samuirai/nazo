# [謎]nazo

[謎]nazo tracks URLs, cookies, parameters and forms in websites for later evaluation.

 * Chrome Browser Extension
 * Python Flask Server Component


## Chrome Browser Extension

The Browser extension injects a piece of javascript in everypage that gathers the following data
and sends it to the backend server:

 * current URL
 * all embedded hrefs
 * cookie
 * forms and inputs

**Warning!** The extension will log a lot of data which can contain sensitive information.
So you should use this extension carefully.


## Python Flask Server Component

The Server component exposes an API which is used by the Browser Extension to save collected data.
Which you can then analyse in various ways.

**Features:**

 * Path Analysis
   * www.example.com**/test/path**?a=parameter
 * Parameter Analysis
   * www.example.com/test/path?**a=parameter&another=param**
 * Form Analysis
   * Analyse collected forms and parameters
 * Cookie Analysis
    * Track changes in cookies

