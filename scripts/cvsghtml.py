#!/usr/bin/env python

#analysis-engine '{"sources" : [["docket", {"term" : 17, "paid" : true, "ifp" : true}], ["docket", {"term" : 18, "paid" : true, "ifp" : true}]],
#                  "filters" : [["cvsg", {"has_cvsg" : true}]],
#                  "queries" : [],
#                  "output" : ["docket-meta", {}]}' | ./cvsghtml.py

import codecs
import json
import sys

import scotus.util

PAGE = """<html>
<head>
  <title>CVSG Report</title>
        <style>
        table {
                border-collapse: collapse;
                width: 100%%;
                border: 1px solid black;
        }

        th, td {
                text-align: left;
                padding: 2px;
                border: 1px solid black;
        }
        </style>
</head>
<body>
<table>
<tr>
  <th>Docket</th><th>Request</th><th>Return</th><th>Type</th><th>LC</th><th>Name</th><th>Flags</th>
<tr>
%s
</table>
</body>
</html>
"""

def main():
  infile = sys.stdin
  with infile:
    try:
      obj = json.load(infile)
    except ValueError as e:
      raise SystemExit(e)

  sumdata = obj["output"]
  tdata = []
  for idx,(term,num,cabbr) in enumerate(sumdata):
    djson = json.loads(open("OT-%d/dockets/%d/docket.json" % (term, num), "rb").read())
    docket = scotus.util.DocketStatusInfo(djson)

    cvsg_date = docket.cvsg_date.strftime("%Y-%m-%d")
    cvsg_return_date = "&nbsp;"
    if docket.cvsg_return_date:
      cvsg_return_date = docket.cvsg_return_date.strftime("%Y-%m-%d")

    if docket.granted:
      row = ["#cceecc"]
    elif docket.denied or docket.dismissed:
      row = ["#ffcccc"]
    elif idx % 2:
      row = ["#FFFFFF"]
    else:
      row = ["#f2f2f2"]

    row.append('<a href="%s">%s</a>' % (docket.docketurl, docket.docketstr))
    row.extend([cvsg_date, cvsg_return_date])
    row.extend([docket.casetype, cabbr, docket.casename])
    flagstr = [x for x in docket.getFlagList() if x != "CVSG"]
    row.append(flagstr)
    tdata.append(tuple(row))

  ROWFMT = u"<tr bgcolor=\"%s\"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
  out = PAGE % (u"\n".join([ROWFMT % x for x in tdata]))

  with codecs.open("webroot/reports/cvsg.html", "w+", encoding="utf-8") as f:
    f.write(out)


if __name__ == '__main__':
  scotus.util.setOutputEncoding()
  main()
