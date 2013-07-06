import json
import os
import re
import urlparse
import sys

slug_path = None
slug_file = None
def hem_port():
    data = slug_json()
    return data.get('port', 9294)

def slug_json():
    sfile = slug_file if slug_file else "slug.json"
    path = os.path.join(slug_path, sfile)
    with open(path) as f:
        return json.load(f)
    return os.path.join(os.path.dirname(__file__))

def hemprefixes():
    prefixes = [os.path.join(slug_path, x) for x in slug_json()['paths']]
    prefixes = [os.path.normpath(x) for x in prefixes]
    return prefixes

def all_coffee_assets(host, port=None):
    if port is None: port = hem_port()
    targets = []
    for prefix in hemprefixes():
        targets.extend(coffee_assets(prefix, host, port))
    return targets
                       
ignores = [".*~", "^#", "^\.", "^.*.sw?"]
def coffee_assets(prefix, host, port=None, excludes=None):
    if port is None: port = hem_port()    
    #walk coffee tree
    if excludes is None:
        excludes = set()
    else:
        excludes = set(excludes)
    ftargets = []
    for path, dirs, files in os.walk(prefix, followlinks=True):
        if path in excludes:
            continue
        for f in files:
            fname = os.path.join(path, f)
            ftargets.append(fname)
    #filter out ignores
    ftargets = [f for f in ftargets if not \
             any([re.match(ignore, os.path.basename(f)) for ignore in ignores])]
    
    return make_urls(ftargets, host, port)    

def make_urls(filenames, host, port=None):
    """ Returns a list of URLs to the given files on the filesystem 
    
    The filenames should be .coffee files, and the returned URLs
    will strip the extension appropriately.
    """
    if port is None: port = hem_port()
    slugpath = slug_path
    filenames = [os.path.relpath(x, slugpath) for x in filenames]
    
    #remove extension
    filenames = [os.path.splitext(f)[0] for f in filenames]
    base = "http://%s:%s" % (host, port)
    #make urls
    return [urlparse.urljoin(base, x) for x in filenames]
    
def slug_libs(app, libs):
    import flask
    targets = [os.path.join(slug_path, os.path.normpath(x)) for x in libs]
    targets = [os.path.relpath(x, app.static_folder) for x in targets]
    targets = [flask.url_for('static', filename=x) for x in targets]
    return targets

def django_slug_libs(static_root, static_url, libs):
    targets = [os.path.join(slug_path, os.path.normpath(x)) for x in libs]
    targets = [os.path.relpath(x, static_root) for x in targets]
    targets = [urlparse.urljoin(static_url, x) for x in targets]
    return targets

def flask_template_context(app, port=None):
    if port is None: port = hem_port()    
    if getattr(app, "debugjs", False):
        slug = slug_json()
        static_js = slug_libs(app, slug['libs'])
        cssfiles =  [
            "http://localhost:%s/css/application.css" % port
            ]
        hem_js = all_coffee_assets("localhost", port)
    else:
        from flask import url_for
        static_js = [url_for('static', filename='js/application.js')]
        cssfiles = [url_for('static', filename='css/application.css')]
        hem_js = []
    return dict(static_js=static_js,
                cssfiles=cssfiles,
                hem_js=hem_js)


    
