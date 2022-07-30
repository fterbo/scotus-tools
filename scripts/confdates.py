#!/usr/bin/env python

# Copyright (c) 2019-2022  Floyd Terbo

import datetime
import json
import sys

import scotus.exceptions
import scotus.util

scotus.exceptions.CasenameError.IGNORE = True

BOUNDS = {
  10 : (datetime.date(2010, 9, 20), datetime.date(2011, 7, 20)),
  11 : (datetime.date(2011, 9, 20), datetime.date(2012, 7, 20)),
  12 : (datetime.date(2012, 9, 20), datetime.date(2013, 7, 20)),
  13 : (datetime.date(2013, 9, 29), datetime.date(2014, 7, 10)),
  14 : (datetime.date(2014, 9, 29), datetime.date(2015, 7, 10)),
  15 : (datetime.date(2015, 9, 28), datetime.date(2016, 7, 10)),
  16 : (datetime.date(2016, 9, 26), datetime.date(2017, 7, 10)),
  17 : (datetime.date(2017, 9, 25), datetime.date(2018, 7, 10)),
  18 : (datetime.date(2018, 9, 24), datetime.date(2019, 7, 10)),
  19 : (datetime.date(2019, 9, 20), datetime.date(2020, 7, 10)),
  20 : (datetime.date(2020, 9, 20), datetime.date(2021, 8, 1)),
  21 : (datetime.date(2021, 9, 20), datetime.date(2022, 8, 1))
}

def main():
  infile = sys.stdin
  with infile:
    try:
      obj = json.load(infile)
    except ValueError as e:
      raise SystemExit(e)

  confdates = {} # { term : <date, ...>, ... }
  sumdata = obj["output"]
  for term,num,cabbr in sumdata:
    if not term:
      continue

    djson = json.loads(open("OT-%d/dockets/%d/docket.json" % (term, num), "rb").read())
    docket = scotus.util.DocketStatusInfo(djson)

    ts, te = BOUNDS[term]
    for (edate, cdate, resch) in docket.distributed:
      if cdate >= ts and cdate <= te:
        confdates.setdefault(term, set([])).add(cdate)

  nconfdates = {"terms" : []}
  for k,v in confdates.items():
    obj = {"term" : k}
    tlist = [{"y" : x.year, "m" : x.month, "d" : x.day} for x in sorted(list(v), reverse=True)]
    obj["confdates"] = tlist
    nconfdates["terms"].append(obj)

  nconfdates["terms"] = sorted(nconfdates["terms"], key = lambda x: x["term"], reverse=True)


  print json.dumps(nconfdates)


if __name__ == '__main__':
  scotus.util.setOutputEncoding()
  main()
