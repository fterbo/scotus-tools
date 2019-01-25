#!/usr/bin/env python

import codecs
import json
import sys

import dateutil.parser

import scotus.util

PAGE = """<html>
<head>
  <meta charset="UTF-8">
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

  .tooltip {
          position: relative;
          display: inline-block;
          border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
  }

  /* Tooltip text */
  .tooltip .tooltiptext {
          visibility: hidden;
          width: 600px;
          background-color: #555;
          color: #fff;
          text-align: left;
          padding: 10px 0;
          border-radius: 6px;

          /* Position the tooltip text */
          position: absolute;
          z-index: 1;
          bottom: -200%%;
          left: 50%%;
          margin-left: 20px;

          /* Fade in tooltip */
          opacity: 0;
          transition: opacity 0.3s;
  }

  /* Tooltip arrow */
  .tooltip .tooltiptext::after {
          content: "";
          position: absolute;
          top: 100%%;
          left: 50%%;
          margin-left: 10px;
          border-width: 5px;
          border-style: solid;
          border-color: #555 transparent transparent transparent;
  }

  /* Show the tooltip text when you mouse over the tooltip container */
  .tooltip:hover .tooltiptext {
          visibility: visible;
          opacity: 1;
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
  for idx,(term,num,cabbr) in enumerate(sumdata):
    djson = json.loads(open("OT-%d/dockets/%d/docket.json" % (term, num), "rb").read())
    docket = scotus.util.DocketStatusInfo(djson)

    lcinfo = []
    lcinfo.append(docket.lowercourt)
    if docket.lowercourt_decision_date:
      lcinfo.append("%s - %s" % (docket.lowercourt_docket, docket.lowercourt_decision_date.strftime("%Y-%m-%d")))
    else:
      lcinfo.append(docket.lowercourt_docket)

    dstrl = []
    dcount = 0
    rdcount = 0
    for (ed, cd, r) in docket.distributed:
      dcount += 1
      cds = cd.strftime("%Y-%m-%d")
      if r:
        dstrl.append("%s[R]" % (cds))
        rdcount += 1
      else:
        dstrl.append(cds)

    if docket.granted:
      row = ["#cceecc"]
    elif docket.denied or docket.dismissed:
      row = ["#ffcccc"]
    elif idx % 2:
      row = ["#FFFFFF"]
    else:
      row = ["#f2f2f2"]

    row.append(u'<a href="%s" target="_blank">%s</a>' % (docket.docketurl, docket.docketstr))
    row.append(docket.casetype)
    if cabbr != "None":
      row.append(u'<div class="hasTooltip">%s</div><div class="hidden">%s</div>' % (cabbr, "<br>".join(lcinfo)))
    else:
      row.append(cabbr)
    qp = docket.getQPText().strip().decode("utf-8")
    if qp:
      row.append(u'<details><summary>%s</summary><pre>%s</pre></details>' % (docket.casename, docket.getQPText().decode("utf-8")))
    else:
      row.append(docket.casename)
    row.append(docket.getFlagString())
    row.append(u'<details><summary>%d (%d Resch.)</summary>%s</details' % (dcount, rdcount, "<br>".join(dstrl)))
    tdata.append(tuple(row))

  ROWFMT = u"<tr bgcolor=\"%s\"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
  out = PAGE % (cdatestr, cdatestr, u"\n".join([ROWFMT % x for x in tdata]))

  with codecs.open("webroot/reports/conf.html", "w+", encoding="utf-8") as f:
    f.write(out)

  with codecs.open("webroot/reports/conf/%s.html" % (cshortstr), "w+", encoding="utf-8") as f:
    f.write(out)


if __name__ == '__main__':
  scotus.util.setOutputEncoding()
  main()
