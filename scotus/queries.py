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
  def __init__ (self, docket_ref):
    self.docket_ref = docket_ref

  def query (self, query_term, min_count = 1):
    qgram = len(query_term.split())

    try:
      ppath = self.docket_ref.info.petition_path
      if not ppath:
#        print("No petition for %d" % (self.docket_ref.info.docket))
        return None
    except IOError:
      return None

    pfname = os.path.basename(ppath)
    if not pfname:
      return None

    count = self.docket_ref.index.gramsearch(pfname, qgram, query_term)
    if count < min_count:
      return False
    return self.docket_ref
