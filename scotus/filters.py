# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import

from . import decorators as SD
from .courts import NAMEMAP as LCNAMEMAP
from .attorneys import Attorney, ATTYMAP

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


ATTY_ROLES = {
  "gov" : "isGov",
  "sg" : "isSG",
  "ag" : "isAG",
  "priv" : "isPrivate",
}

@srcfilter("attorney")
@SD.inputs("docket-reference")
class PartyAttorney(object):
  def __init__ (self, atty_name, role = None):
    self.atty = ATTYMAP[atty_name]
    self.role = getattr(Attorney, ATTY_ROLES[role])

  def include (self, docket_ref):
    if not docket_ref.info:
      return False

    docket = docket_ref.info

    for atty in docket.attys_petitioner:
      try:
        aobj = ATTYMAP[atty]
        if self.atty == aobj:
          if self.role:
            if self.role(aobj, docket.docket_date):
              return True
          else:
            return True
      except KeyError:
        continue

    for atty in docket.attys_respondent:
      try:
        aobj = ATTYMAP[atty]
        if self.atty == aobj:
          if self.role:
            if self.role(aobj, docket.docket_date):
              return True
          else:
            return True
      except KeyError:
        continue

