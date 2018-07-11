# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import

from . import decorators as SD
from .courts import NAMEMAP as LCNAMEMAP

OUTPUTTYPES = {}

def output (typ):
  def decorator(k):
    OUTPUTTYPES[typ] = k
    return k
  return decorator


@output("docket-oneline")
@SD.inputs("docket-reference")
class OneLineDocketSummary(object):
  def output (self, docket_ref, extra_list):
    di = docket_ref.info
    dstr = "%d-%d" % (di.term, di.docket)

    cabbr = None
    for k,v in LCNAMEMAP.items():
      if v == di.lowercourt:
        cabbr = k

    return (di.term, di.docket, "[%7s][%11s][%5s] %s %s" % (dstr, di.casetype, cabbr, di.casename, di.getFlagString()))

