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


class DocketReference(object):
  def __init__ (self, path):
    self.path = path

    self._info = None
    self._index = None

  @property
  def info (self):
    if self._info is None:
      try:
        with open("%s/docket.json" % (self.path), "rb") as df:
          docket_obj = json.loads(df.read())

        self._info = util.DocketStatusInfo(docket_obj)
      except IOError:
        self._info = False
    return self._info

  @property
  def index (self):
    if not self._index:
      self._index = parse.DirIndex(self.path)
    return self._index


@source("docket")
@SD.returns("docket-reference")
class DocketSource(object):
  def __init__ (self, root_path, term, paid = False, ifp = False, application = False):
    self.term = term
    self.root_path = root_path
    self.paid = paid
    self.ifp = ifp
    self.application = application

    self.didxs  = [int(x) for x in os.listdir("%s/OT-%d/dockets/" % (root_path, term))
                    if not x.startswith(".") and x != "A"]
    self.didxs.sort()

    self.adidxs = [int(x) for x in os.listdir("%s/OT-%d/dockets/A/" % (root_path, term))
                    if not x.startswith(".") and x != "indexes.json"]
    self.adidxs.sort()

  def __iter__ (self):
    if self.paid or self.ifp:
      for didx in self.didxs:
        if not self.paid and didx < 5000:
          continue
        elif not self.ifp and didx > 5000:
          continue
        yield DocketReference("%s/OT-%d/dockets/%s" % (self.root_path, self.term, didx))
    if self.application:
      for idx in self.adidxs:
        yield DocketReference("%s/OT-%d/dockets/A/%s" % (self.root_path, self.term, idx))


@source("opinion")
@SD.returns("opinion-reference")
class OpinionSource(object):
  def __init__ (self, root_path, term):
    self.term = term
    self.root_path = root_path

  def __iter__ (self):
    pass
