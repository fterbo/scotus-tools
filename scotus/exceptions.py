# Copyright (c) 2018  Floyd Terbo

class NoDocketError(Exception):
  def __init__ (self, docketstr):
    self.docket = docketstr
  def __str__ (self):
    return "No docket info found for %s" % (self.docket)
