#!/usr/bin/env python

# Copyright (c) 2018  Floyd Terbo

import logging
import os
import os.path
import shutil
import sys
import time

import BeautifulSoup as BS
import requests

logging.basicConfig(level=logging.DEBUG)

HEADERS = {"User-Agent" : "SCOTUS Orders Grabber (https://github.com/fterbo/scotus-tools)"}
BASE = "https://www.supremecourt.gov"

def parse_args ():
  parser = argparse.ArgumentParser()
  parser.add_argument("-t", "--term", dest="term", type=int)
  parser.add_argument("--root", dest="root", type=str, default=".")
  args = parser.parse_args()
  return args

def GET (url):
  logging.debug("GET: %s" % (url))
  return requests.get(url, headers=HEADERS)

def download (term, path):
  r = GET("%s/orders/ordersofthecourt/%d" % (BASE, term))
  if r.status_code != 200:
    print r.status_code
    sys.exit(1)

  root = BS.BeautifulSoup(r.content)
  links = root.findAll("a")
  for link in links:
    href = link.get("href")
    if href and len(href) > 4 and href[-4:] == ".pdf":
      if href.count("orders"):
        fname = href.split("/")[-1]
        outpath = "%s/%s" % (path, fname)

        # Skip orders we already have
        if os.path.exists(outpath):
          logging.info("Skipping: %s" % (href))
          continue

        logging.info("Downloading: %s" % (href))
        order = GET("%s%s" % (BASE, href))
        with open(outpath, "w+") as f:
          f.write(order.content)

if __name__ == '__main__':
  opts = parse_args()

  path = "%s/OT-%d/orders" % (opts.root, opts.term)
  try:
    os.makedirs(path)
  except OSError:
    pass
  download(opts.term, path)

