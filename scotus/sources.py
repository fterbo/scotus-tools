# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import

import json
import os

from . import decorators as SD
from . import parse
from . import util

SOURCETYPES = {}

def source (typ):
  def decorator(k):
    SOURCETYPES[typ] = k
    return k
  return decorator


@source("docket")
@SD.returns("docket-reference")
class DocketSource(object):
  def __init__ (self, root_path, term, paid = False, ifp = False):
    self.term = term
    self.root_path = root_path
    self.paid = paid
    self.ifp = ifp

    self.didxs  = [int(x) for x in os.listdir("%s/OT-%d/dockets/" % (root_path, term)) if not x.startswith(".")]
    self.didxs.sort()

  def __iter__ (self):
    for didx in self.didxs:
      if not self.paid and didx < 5000:
        continue
      elif not self.ifp and didx > 5000:
        continue
      yield DocketReference("%s/OT-%d/dockets/%s" % (self.root_path, self.term, didx))


class DocketReference(object):
  def __init__ (self, path):
    self.path = path

    self._info = None
    self._index = None

  @property
  def info (self):
    if not self._info:
      with open("%s/docket.json" % (self.path), "rb") as df:
        docket_obj = json.loads(df.read())

      self._info = util.DocketStatusInfo(docket_obj)
    return self._info

  @property
  def index (self):
    if not self._index:
      self._index = parse.DirIndex(self.path)
    return self._index

