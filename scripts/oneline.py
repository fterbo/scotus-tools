#!/usr/bin/env python

import json
import sys

import scotus.util

def main():
  infile = sys.stdin
  with infile:
    try:
      obj = json.load(infile)
    except ValueError as e:
      raise SystemExit(e)

  sumdata = obj["output"]
  for term,num,dstr,summary in sumdata:
    print "[%8s] %s" % (dstr, summary)

if __name__ == '__main__':
  scotus.util.setOutputEncoding()
  main()
