# Copyright (c) 2018  Floyd Terbo

class SCOTUSError(Exception): pass

class NoDocketError(SCOTUSError):
  def __init__ (self, docketstr):
    super(NoDocketError, self).__init__()
    self.docket = docketstr
  def __str__ (self):
    return "No docket info found for %s" % (self.docket)


class CasenameError(SCOTUSError):
  def __init__ (self, docket):
    self.docket = docket
  def __str__ (self):
    return "Unable to create case name for %s" % (self.docket)


class CaseTypeError(SCOTUSError):
  def __init__ (self, docket):
    self.docket = docket
  def __str__ (self):
    return "Unable to determine case type for %s" % (self.docket)


class NoPetitionForApplicationError(SCOTUSError):
  def __init__ (self, docket):
    super(NoPetitionForApplicationError, self).__init__()
    self.docket = docket
  def __str__ (self):
    return "Application docket (%s) does not contain cert petition" % (self.docket)
