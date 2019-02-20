# Copyright (c) 2019  Floyd Terbo

# Utilities used by the command line tools that might be best shared or available
# for use in scripts.  This will turn into a cesspool of random, but at least you
# can import it.

import logging
import os
import os.path
import sys

import requests

import scotus.util

HEADERS = {"User-Agent" : "SCOTUS Webutils Default UA (https://github.com/fterbo/scotus-tools)"}
JSONBASE = "https://www.supremecourt.gov/rss/cases/JSON/"
URL = "https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/%s.html"
OLDURL = "https://www.supremecourt.gov/search.aspx?filename=/docketfiles/%s.htm"

# We passed around options too much, so mock them here
class bdsOpts(object):
  def __init__ (self, term, docket_num, application = False, orig = False):
    self.term = term
    self.docket_num = docket_num
    self.application = application
    self.orig = orig
    self.action = "none"

def GET (url):
  logging.debug("GET: %s" % (url))
  return requests.get(url, headers=HEADERS)

def getPage (term, docket_num, root = ".", application = False, force = False):
  opts = bdsOpts(term, docket_num, application)
  dstr = scotus.util.buildDocketStr(opts)

  if application:
    droot = "%s/OT-%d/dockets/A/%d" % (root, term, docket_num)
  else:
    droot = "%s/OT-%d/dockets/%d" % (root, term, docket_num)

  local_path = "%s/legacy.html" % (droot)
  if not os.path.exists(droot):
    os.makedirs(droot)

  old = False
  oldlocal_path = "%s/oldlegacy.html" % (droot)
  if os.path.exists(oldlocal_path):
    old = True

  if (not os.path.exists(local_path) and not os.path.exists(oldlocal_path)) or force:
    if not force:
      jr = GET("%s%s.json" % (JSONBASE, dstr))
      if jr.status_code == 200:
        logging.error("[%s] Not a legacy docket" % (dstr))
        with open("%s/docket.json" % (droot), "w+") as jdf:
          jdf.write(jr.content)
        sys.exit(1)

    r = requests.get(URL % (dstr))
    if r.status_code == 404 or not r.content.count("Docketed"):
      r = requests.get(OLDURL % (dstr))
      local_path = oldlocal_path
      old = True

    if r.status_code == 200:
      with open(local_path, "w+") as dhtml:
        dhtml.write(r.content)
      return (r.content, old)
    else:
      logging.error(r.status_code)
      sys.exit(1)
  else:
    if old:
      content = open(oldlocal_path, "rb").read()
    else:
      content = open(local_path, "rb").read()
    return (content, old)
