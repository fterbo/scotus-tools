# Copyright (c) 2018-2019  Floyd Terbo

import dateutil.parser

class DocketEvent(object):
  def __init__ (self, edict):
    self.date = None
    self.text = None
    self._e_dict = edict
    self._build()

    self.distributed = False
    self.denied = False
    self.dismissed = False
    self.brief = False
    self.granted = False
    self.argued = False
    self.removed = False
    self.remanded = False
    self.cvsg = False
    self.argued = False
    self.issued = False
    self.ifp_denied = False
    self.response_requested = False
    self.record_requested = False
    self.mooted = False
    self.rehearing_denied = False
    self.affirmed = False
    self.inquorate = False
    self.motion_denied = False
    self.counsel_granted = False

  def _build (self):
    self.date = dateutil.parser.parse(self._e_dict["Date"]).date()
    self.text = self._e_dict["Text"]

  def __str__ (self):
    sl = []
    for k,v in self.__dict__.items():
      if v == True:
        sl.append(k)
    return "(%s) %s [%s]" % (self.date.strftime("%Y-%m-%d"), self.text, ", ".join(sl))

    

