# Copyright (c) 2018  Floyd Terbo

import json
import os

import scotus.util

@source(type="docket")
class DocketSource(object):
  def __init__ (self, root_path, term):
    self.term = term
    self.root_path = root_path

    self.ddirs = [int(x) for x in os.listdir("%s/OT-%d/dockets/" % (root_path, term)) if not x.startswith(".")]
    self.ddirs.sort()

  def __iter__ (self):
    for ddir in self.ddirs:
      yield DocketReference(ddir)


class DocketReference(object):
  def __init__ (self, path):
    self.path = path

  @property
  def info (self):
    with open("%s/docket.json" % (self.path), "rb") as df:
      docket_obj = json.loads(df.read())

    return scotus.util.DocketStatusInfo(docket_obj)

  @property
  def index (self):
    with open("%s/indexes.json" % (self.path), "rb") as idxf:
      index_obj = json.loads(idxf.read())

    return index_obj

