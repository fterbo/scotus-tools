#!/usr/bin/env python

import codecs
import json
import sys

import dateutil.parser

import scotus.util

PAGE = """<html>
<head>
  <meta chartset="UTF-8">
  <title>Conference Report (%s)</title>
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

  tr:nth-child(even) {background-color: #f2f2f2;}

  .hidden {
    display: none;
  }
  </style>
  <link type="text/css" rel="stylesheet" href="http://qtip2.com/v/stable/jquery.qtip.css"/>
</head>
<body>
  <script type="text/javascript" src="https://code.jquery.com/jquery-2.2.4.min.js"></script>
  <script type="text/javascript" src="http://qtip2.com/v/stable/jquery.qtip.js"></script>
  <script>
  $(document).ready(function() {
    $('.hasTooltip').each(function() { // Notice the .each() loop, discussed below
        $(this).qtip({
            content: {
                text: $(this).next('div') // Use the "div" element next to this for the content
            }
        });
    });
  });
  </script>
<h2>Petitions considered for conference on %s</h2>
<table>
<tr>
  <th>Docket</th><th>Type</th><th>LC</th><th>Name</th><th>Flags</th><th>Dist.</th>
</tr>
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

  for fname,fargs in obj["arguments"]["filters"]:
    if fname == "distribution":
      cdate = dateutil.parser.parse(fargs["conf_date"])
      cdatestr = cdate.strftime("%B %d, %Y")
      cshortstr = cdate.strftime("%Y%m%d")
    
  tdata = []
  for term,num,cabbr in sumdata:
    djson = json.loads(open("OT-%d/dockets/%d/docket.json" % (term, num), "rb").read())
    docket = scotus.util.DocketStatusInfo(djson)

    dstrl = []
    for (ed, cd, r) in docket.distributed:
      cds = cd.strftime("%Y-%m-%d")
      if r:
        dstrl.append("%s[R]" % (cds))
      else:
        dstrl.append(cds)

    row = [u'<a href="%s" target="_blank">%s</a>' % (docket.docketurl, docket.docketstr)]
    row.extend([docket.casetype, cabbr])
    qp = docket.getQPText().strip().decode("utf-8")
    if qp:
      row.append(u'<details><summary>%s</summary><pre>%s</pre></details>' % (docket.casename, docket.getQPText().decode("utf-8")))
    else:
      row.append(docket.casename)
    row.append(docket.getFlagString())
    row.append("<br>".join(dstrl))
    tdata.append(tuple(row))

  ROWFMT = u"<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
  out = PAGE % (cdatestr, cdatestr, u"\n".join([ROWFMT % x for x in tdata]))

  with codecs.open("webroot/reports/conf.html", "w+", encoding="utf-8") as f:
    f.write(out)

  with codecs.open("webroot/reports/conf/%s.html" % (cshortstr), "w+", encoding="utf-8") as f:
    f.write(out)


if __name__ == '__main__':
  scotus.util.setOutputEncoding()
  main()

