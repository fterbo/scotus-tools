#!/usr/bin/env python

# Copyright (c) 2019  Floyd Terbo

import codecs
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
    for (ed, cd, r) in docket.distributed:
      if cd == cdate:
        rd["dist-date"] = {"y" : ed.year, "m" : ed.month, "d" : ed.day}
      dcount += 1
      cds = cd.strftime("%Y-%m-%d")
      if r:
        dstrl.append("%s[R]" % (cds))
        rdcount += 1
      else:
        dstrl.append(cds)


    rd["docket-url"] = docket.docketurl
    rd["docket-str"] = docket.docketstr
    rd["case-name"] = docket.casename
    rd["case-type"] = docket.casetype
    rd["current-status"] = docket.current_status
    rd["conf-action"] = docket.getConfAction(cdate)
    rd["dist-count"] = dcount
    rd["resch-count"] = rdcount
    rd["dist-details"] = "<br>".join(dstrl)
    rd["flags"] = docket.getFlagDict()

    rd["lc-abbr"] = cabbr
    if cabbr != "None":
      rd["lc-info"] = "<br>".join([str(x) for x in lcinfo])

    qp = docket.getQPText().strip().decode("utf-8")
    if qp:
      rd["qp"] = qp

    tdata.append(rd)

  outdict["dockets"] = tdata

  with codecs.open("webroot/data/conf/%s.json" % (cshortstr), "w+", encoding="utf-8") as f:
    f.write(json.dumps(outdict))


if __name__ == '__main__':
  scotus.util.setOutputEncoding()
  main()
