#!/usr/bin/env python

# Copyright (c) 2019  Floyd Terbo

import codecs
import logging
import json
import sys

import dateutil.parser

import scotus.util

def main():
  infile = sys.stdin
  with infile:
    try:
      obj = json.load(infile)
    except ValueError as e:
      raise SystemExit(e)

  cdata = json.loads(open("webroot/data/confdates.json", "r").read())
  dates = []
  for term in cdata.keys():
    for lobj in cdata[term]:
      for cinfo in lobj["confdates"]:
        dates.append(dateutil.parser.parse("%s-%s-%s" % (cinfo["y"], cinfo["m"], cinfo["d"])).date())
  dates.sort()

  sumdata = obj["output"]

  for fname,fargs in obj["arguments"]["filters"]:
    if fname == "distribution":
      cdate = dateutil.parser.parse(fargs["conf_date"]).date()
      cdatestr = cdate.strftime("%B %d, %Y")
      cshortstr = cdate.strftime("%Y%m%d")

  outdict = {"conf-date" : cdatestr}

  tdata = []
  for term,num,cabbr in sumdata:
    djson = json.loads(open("OT-%d/dockets/%d/docket.json" % (term, num), "rb").read())
    docket = scotus.util.DocketStatusInfo(djson)

    try:
      lcinfo = []
      lcinfo.append(docket.lowercourt)
      if docket.lowercourt_decision_date:
        lcinfo.append("%s - %s" % (docket.lowercourt_docket, docket.lowercourt_decision_date.strftime("%Y-%m-%d")))
      else:
        lcinfo.append(docket.lowercourt_docket)

      rd = {}

      dstrl = []
      dcount = 0
      rdcount = 0
      ddate = None
      for (ed, cd, r) in docket.distributed:
        if cd == cdate:
          ddate = ed
          rd["dist-date"] = {"y" : ed.year, "m" : ed.month, "d" : ed.day}
        dcount += 1
        cds = cd.strftime("%Y-%m-%d")
        if r:
          dstrl.append("%s[R]" % (cds))
          rdcount += 1
        else:
          dstrl.append(cds)

      skip = False
      for event in docket.events:
        if event.date >= ddate and event.date <= cdate:
          if event.response_requested or event.record_requested:
            skip = True
            break

      if skip:
        logging.debug("%s: skipping %s" % (cshortstr, docket.docketstr))
        continue


      rd["docket-url"] = docket.docketurl
      rd["docket-str"] = docket.docketstr
      rd["case-name"] = docket.casename
      rd["case-type"] = docket.casetype
      rd["current-status"] = docket.current_status
      rd["conf-action"] = docket.getConfAction(cdate, dates)
      rd["dist-count"] = dcount
      rd["resch-count"] = rdcount
      rd["dist-details"] = "<br>".join(dstrl)
      rd["flags"] = docket.getFlagDict()
      rd["tags"] = docket.getTagDict()
      rd["holding"] = docket.getHoldingDict()

      rd["lc-abbr"] = cabbr
      if cabbr != "None":
        rd["lc-info"] = "<br>".join([str(x) for x in lcinfo])

      qp = docket.getQPText().strip().decode("utf-8")
      if qp:
        rd["qp"] = qp

      tdata.append(rd)
    except Exception as e:
      logging.exception("Docket %d-%d" % (term, num))

  outdict["dockets"] = tdata

  with codecs.open("webroot/data/conf/%s.json" % (cshortstr), "w+", encoding="utf-8") as f:
    f.write(json.dumps(outdict))

  logging.info("%s: %d dockets" % (cshortstr, len(tdata)))


if __name__ == '__main__':
  scotus.util.setOutputEncoding()
  main()
