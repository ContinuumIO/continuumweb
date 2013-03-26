import json
import os
import re
import urlparse
import sys

slug_path = None

def slug_json():
    path = os.path.join(slug_path, 'slug.json')
    with open(path) as f:
        return json.load(f)
    return os.path.join(os.path.dirname(__file__))

def hemprefixes():
    prefixes = [os.path.join(slug_path, x) for x in slug_json()['paths']]
    prefixes = [os.path.normpath(x) for x in prefixes]
    return prefixes

def all_coffee_assets(host, port):
    targets = []
    for prefix in hemprefixes():
        targets.extend(coffee_assets(prefix, host, port))
    return targets
                       
ignores = [".*~", "^#", "^\."]
def coffee_assets(prefix, host, port, excludes=None):
    #walk coffee tree
    if excludes is None:
        excludes = set()
    else:
        excludes = set(excludes)
    ftargets = []
    for path, dirs, files in os.walk(prefix, followlinks=True):
        if path in excludes:
            print "coffee_assets() skipping", path
            continue
        for f in files:
            fname = os.path.join(path, f)
            print fname
            ftargets.append(fname)
    #filter out ignores
    ftargets = [f for f in ftargets if not \
             any([re.match(ignore, os.path.basename(f)) for ignore in ignores])]
    
    return make_urls(ftargets, host, port)    

def make_urls(filenames, host, port):
    """ Returns a list of URLs to the given files on the filesystem 
    
    The filenames should be .coffee files, and the returned URLs
    will strip the extension appropriately.
    """
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
