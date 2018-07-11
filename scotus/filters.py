# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import

from . import decorators as SD
from .courts import NAMEMAP as LCNAMEMAP

FILTERTYPES = {}

def srcfilter (typ):
  def decorator(k):
    FILTERTYPES[typ] = k
    return k
  return decorator


@srcfilter("lowercourt")
@SD.inputs("docket-reference")
class LowerCourtFilter(object):
  def __init__ (self, court_abbrev):
    self.court = LCNAMEMAP[court_abbrev]

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    if not docket_ref.info.lowercourt:
      return False

    if self.court == docket_ref.info.lowercourt:
      return True

