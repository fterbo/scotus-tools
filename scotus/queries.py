# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import, print_function

import logging
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
    logging.debug("<(petition-ngram) query_term : %s, min_count: %d>" % (query_term, min_count))

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


QTYPES = {
  "contains" : 0,
  "startswith" : 1,
  "endswith" : 2,
  "regexp" : 3
}

@query("event-text")
@SD.inputs("docket-reference")
@SD.returns("docket-reference")
class EventTextQuery(object):
  def __init__ (self, query_term, qtype = "contains", case_sensitive = False, min_count = 1):
    self.query_type = QTYPES[qtype]
    self.query_term = query_term
    self.case_sensitive = case_sensitive
    self.min_count = min_count

    if not self.case_sensitive:
      self.query_term = self.query_term.lower()

    logging.debug("<(event-text) query_type: %d, query_term: %s, case_sensitive: %s>" % (
                  self.query_type, self.query_term, self.case_sensitive))

  def query (self, docket_ref):
    if not docket_ref.info:
      return False

    for event in docket_ref.info.events:
      etxt = event.text
      if not self.case_sensitive:
        etxt = etxt.lower()

      if self.query_type == 0:
        if etxt.count(self.query_term) >= self.min_count:
          return (docket_ref, {})

    return False
