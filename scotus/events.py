# Copyright (c) 2018-2020  Floyd Terbo

import dateutil.parser

class DocketEvent(object):
  def __init__ (self, edict):
    self.date = None
    self.text = None
    self._e_dict = edict
    self._build()

    self.affirmed = False
    self.amici_court_appointed = False
    self.amicus_brief = False
    self.argued = False
    self.brief = False
    self.circulated = False
    self.counsel_granted = False
    self.cvsg = False
    self.cvsg_return = False
    self.denied = False
    self.dismissed = False
    self.distributed = False
    self.granted = False
    self.ifp_denied = False
    self.ifp_granted = False
    self.ifp_paid = False
    self.ifp_respondent = False
    self.inquorate = False
    self.issued = False
    self.joint_appendix = False
    self.joint_motion = False
    self.letter = False
    self.mooted = False
    self.motion_denied = False
    self.motion_divided_argument = False
    self.motion_divided_denied = False
    self.motion_divided_granted = False
    self.not_accepted = False
    self.petitioner_blanket_consent = False
    self.record_received = False
    self.record_requested = False
    self.rehearing_requested = False
    self.rehearing_denied = False
    self.removed = False
    self.remanded = False
    self.respondent_blanket_consent = False
    self.response_requested = False
    self.set_for_argument = False
    self.set_for_reargument = False
    self.sg_motion_divided_argument = False
    self.sg_grant_divided_argument = False
    self.time_to_file = False
    self.vacated = False


  def _build (self):
    self.date = dateutil.parser.parse(self._e_dict["Date"]).date()
    self.text = self._e_dict["Text"]

  def __str__ (self):
    sl = []
    for k,v in self.__dict__.items():
      if v == True:
        sl.append(k)
    return "(%s) %s [%s]" % (self.date.strftime("%Y-%m-%d"), self.text, ", ".join(sl))

    

