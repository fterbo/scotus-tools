# Copyright (c) 2018-2019  Floyd Terbo

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

    cabbr = None
    for k,v in LCNAMEMAP.items():
      if v == di.lowercourt:
        cabbr = k

    return (di.term, di.docket, di.docketstr,
            "[%11s][%5s] %s %s" % (di.casetype, cabbr, di.casename, di.getFlagString()))


@output("petitioner-counsel-of-record")
@SD.inputs("docket-reference")
class TopsideCounsel(object):
  def output (self, docket_ref, extra_list):
    di = docket_ref.info
    if di:
      if di.atty_petitioner_cor:
        atty_str = di.atty_petitioner_cor
      else:
        atty_str = "Pro Se (Probable)"
      return (di.term, di.docket, atty_str)
    return (-1, -1, "<No Info>")


@output("distribution-data")
@SD.inputs("docket-reference")
  def output (self, docket_ref, extra_list):
    di = docket_ref.info
    if di:
      return (di.docketstr, di.distributed)
    return (None, [])
