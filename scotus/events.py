# Copyright (c) 2018  Floyd Terbo

import dateutil.parser

class DocketEvent(object):
  def __init__ (self, edict):
    self.date = None
    self.text = None
    self._e_dict = edict
    self._build()

  def _build (self):
    self.date = dateutil.parser.parse(self._e_dict["Date"]).date()
    self.text = self._e_dict["Text"]

  def __str__ (self):
    return "(%s) %s" % (self.date.strftime("%Y-%m-%d"), self.text)

    

