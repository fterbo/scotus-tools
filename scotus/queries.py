# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import, print_function

import os.path

from . import decorators as SD

QUERYTYPES = {}

def query (typ):
  def decorator(k):
    QUERYTYPES[typ] = k
    return k
  return decorator


@query("petition-ngram")
@SD.inputs("docket-reference")
@SD.returns("docket-reference")
class PetitionQuery(object):
  def __init__ (self, query_term, min_count = 1):
    self.query_term = query_term
    self.min_count = min_count

  def query (self, docket_ref):
    qgram = len(self.query_term.split())
    if not docket_ref.info:
      return None

    try:
      ppath = docket_ref.info.petition_path
      if not ppath:
#        print("No petition for %d" % (self.docket_ref.info.docket))
        return None
    except IOError:
      return None

    pfname = os.path.basename(ppath)
    if not pfname:
      return None

    count = docket_ref.index.gramsearch(pfname, qgram, self.query_term)
    if count < self.min_count:
      return False
    return (docket_ref, {"query_term" : self.query_term, "count" : count})
