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

  outdata = []
  sumdata = obj["output"]
  for term,num,dstr,summary in sumdata:
    djson = json.loads(open("OT-%d/dockets/%d/docket.json" % (term, num), "rb").read())
    docket = scotus.util.DocketStatusInfo(djson)

    if docket.distributed:
      outdata.append((docket, docket.distributed[-1][1].strftime("%Y-%m-%d")))
    else:
      outdata.append((docket, ""))

  outdata.sort(key=lambda x: x[0].docket)
  for docket,datestr in outdata:
    print "[%8s] [%10s] %s %s" % (docket.docketstr, datestr, docket.casename, docket.getFlagString())


if __name__ == '__main__':
  scotus.util.setOutputEncoding()
  main()
