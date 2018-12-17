# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import

from datetime import date

from .util import MultiMatch

# Don't use this for things, a pattern example right now, unclear later
class POSITIONS(object):
  SGUS = "sg.us"
  SSG = "sg.state"
  PRACTICE = "practice"
  CLINIC = "practice.clinic"
  FIRM = "practice.firm"

ATTYMAP = {}

class Attorney(object):
  def __init__ (self, *names):
    self.names = names
    self.positions = []

    for name in self.names:
      ATTYMAP[unicode(name)] = self

  @property
  def name (self):
    return self.names[0]

  def __str__ (self):
    return unicode(self).encode('utf-8')

  def __unicode__ (self):
    try:
      return unicode(self.names[0], "utf-8")
    except TypeError:
      return self.names[0]

  def setSG (self, entity, start, end = None):
    self.positions.append(("sg.%s" % (entity), start, end))
    return self

  def setAG (self, entity, start, end = None):
    self.positions.append(("ag.%s" % (entity), start, end))
    return self

  def setDA (self, entity, start, end = None):
    self.positions.append(("da.%s" % (entity), start, end))
    return self

  def setFirm (self, entity, start, end = None):
    self.positions.append(("practice.firm.%s" % (entity), start, end))
    return self

  def setFPD (self, entity, start, end = None):
    self.positions.append(("fpd.%s" % (entity), start, end))
    return self

  def setSPD (self, entity, start, end = None):
    self.positions.append(("spd.%s" % (entity), start, end))
    return self

  def isPD (self, qdate):
    for (position, start, end) in self.positions:
      if end is None and qdate > start:
        if position.startswith("fpd.") or position.startswith("spd."):
          return True
      elif qdate > start and qdate <= end:
        if position.startswith("fpd.") or position.startswith("spd."):
          return True
    return False
      

  def isSG (self, qdate):
    for (position, start, end) in self.positions:
      if end is None and qdate > start:
        if position.startswith("sg."):
          return True
      elif qdate > start and qdate <= end:
        if position.startswith("sg."):
          return True
    return False

  def isAG (self, qdate):
    for (position, start, end) in self.positions:
      if end is None and qdate > start:
        if position.startswith("ag."):
          return True
      elif qdate > start and qdate <= end:
        if position.startswith("ag."):
          return True
    return False

  def isDA (self, qdate):
    for (position, start, end) in self.positions:
      if end is None and qdate > start:
        if position.startswith("da."):
          return True
      elif qdate > start and qdate <= end:
        if position.startswith("da."):
          return True
    return False

  def isGov (self, qdate):
    if self.isSG(qdate) or self.isAG(qdate) or self.isDA(qdate):
      return True
    return False

  def isPrivate (self, qdate):
    # Gov't practice is much easier to track than moves in private firms, so we just assume they were in
    # private practice for dates not covered by known government service.  Of course if you supply some
    # random date instead of one retrieved from a filing, we'll be happy to report private practive even
    # if they weren't alive.
    return not self.isGov(qdate)


# Many of these are conservative date ranges based on filings, they are definitely NOT complete or accurate 

_attys = [
  Attorney("Kristafer Ross Ailslieger")
    .setAG("ks.deputy", date(2017, 1, 1), None),
  Attorney("Jerry V. Beard")
    .setFPD("tx.nd", date(2017, 2, 1), None),
  Attorney("Julie Marie Blake")
    .setAG("wv.assistant", date(2014, 1, 1), date(2017, 1, 27))  # Can't find a good start date
    .setAG("mo.unknown", date(2017, 1, 28), None),
  Attorney("Eric Joseph Brignac")
    .setFPD("nc", date(2014, 5, 1), None),
  Attorney("Melody Jane Brown")
    .setAG("sc.unknown", date(2014, 1, 1), None),
  Attorney("Scott Andrew Browne")
    .setAG("fl.assistant", date(1996, 4, 1), None),
  Attorney("Matthew A. Campbell")
    .setFPD("wa.ed", date(2009, 05, 18), None),
  Attorney("Paul D. Clement")
    .setFirm("kirkland-ellis", date(2016, 9, 12), None)
    .setFirm("bancroft", date(2011, 3, 25), date(2016, 9, 12))
    .setFirm("king-spalding", date(2008, 11, 20), date(2011, 3, 25))
    .setSG("us.deputy", date(2001, 2, 1), date(2004, 7, 11))
    .setSG("us.acting", date(2004, 7, 11), date(2005, 6, 13))
    .setSG("us", date(2005, 6, 13), date(2008, 6, 19)),
  Attorney("L. Andrew Cooper")
    .setAG("co.unknown", date(2017, 10, 1), None),
  Attorney("Trevor Stephen Cox")
    .setAG("va.unknown", date(2017, 2, 21), None),
  Attorney("Stephen R. Creason", "Stephen Richard Creason")
    .setAG("in.unknown", date(2006, 12, 13), None),
  Attorney("Christopher A. Curtis")
    .setFPD("tx.nd", date(2016, 12, 15), None),
  Attorney("Tracy Dreispul", "Tracy M. Dreispul")
    .setFPD("fl.sd", date(2006, 11, 20), None),
  Attorney("Ronald  Eisenberg")
    .setDA("phi", date(2017, 1, 1), None),
  Attorney("Thomas M. Fisher")
    .setSG("in", date(2005, 7, 1), None)
    .setAG("in.deputy", date(2001, 2, 1), date(2005, 6, 30)),
  Attorney("Peter Michael Fleury")
    .setFPD("tx", date(2018, 1, 1), None),
  Attorney("Noel J. Francisco", "Noel Francisco")
    .setSG("us.acting", date(2017, 1, 23), date(2017, 3, 10))
    .setSG("us.stub", date(2017, 3, 11), date(2017, 9, 18))  # Stub for bad docket metadata
    .setSG("us", date(2017, 9, 19), None),
  Attorney("Michael Marc Glick")
    .setAG("illinois.ccad", date(2006, 7, 1), None),
  Attorney("Raed Gonzalez")
    .setFirm("gonzalez-olivieri", date(2015, 11, 20), None),
  Attorney("Benjamin Noah Gutman")
    .setSG("or", date(2016, 1, 1), None),
  Attorney("Toby Jay Heytens")
    .setSG("va", date(2018, 1, 9), None)
    .setSG("us.assistant", date(2007, 1, 1), date(2010, 12, 31)),
  Attorney("Michael Clark Holley")
    .setFPD("tn", date(2014, 10, 20), None),
  Attorney("Conrad Benjamin Kahn")
    .setFPD("fl.unknown", date(2015, 11, 9), None),
  Attorney("Paul Edward Kalil")
    .setSPD("fl.ccrc", date(2009, 5, 1), None),
  Attorney("Scott A. Keller")
    .setFirm("baker-botts", date(2018, 9, 10), None)
    .setSG("tx", date(2015, 1, 1), date(2018, 9, 9)),
  Attorney("John M. Klawikofsky")
    .setAG("fl.unknown", date(2005, 3, 14), None),
  Attorney("Aaron David Lindstrom", "Aaron D. Lindstrom Jr.")
    .setSG("mi", date(2013, 12, 1), None)
    .setSG("mi.assistant", date(2012, 10, 1), date(2013, 11, 30))
    .setFirm("warner-norcross-judd", date(2009, 5, 1), date(2012, 9, 30))
    .setFirm("gibson-dunn-crutcher", date(2005, 10, 1), date(2009, 4, 30)),
  Attorney("Matthew Robert McGuire")
    .setAG("va.unknown", date(2017, 2, 21), None),
  Attorney("Eric E. Murphy")
    .setSG("oh", date(2013, 9, 9), None),
  Attorney("Billy H. Nolas")
    .setFPD("fl.chu", date(2017, 6, 1), None),
  Attorney("Kevin Joel Page")
    .setFPD("tx", date(2016, 5, 1), None),
  Attorney("Trisha Meggs Pate")
    .setAG("fl.unknown", date(2011, 3, 3), None),
  Attorney("Andrew Alan Pinson")
    .setSG("ga", date(2018, 5, 1), None),
  Attorney("Margaret Scobey Russell")
    .setSPD("fl.ccrc", date(2018, 3, 1), None),
  Attorney("Kannon K. Shanmugam")
    .setSG("us.assistant", date(2003, 6, 23), date(2008, 3, 24))
    .setFirm("williams-connolly", date(2008, 5, 2), None),
  Attorney("Carolyn M. Snurkowski")
    .setAG("fl", date(2016, 8, 1), None),
  Attorney("Celia A. Terenzio")
    .setAG("fl.assistant", date(2013, 5, 1), None),
  Attorney("Jeffrey B. Wall")
    .setSG("us.acting", date(2017, 3, 10), date(2017, 9, 19))
    .setSG("us.deputy", date(2017, 9, 20), None),
  Attorney("Sarah Hawkins Warren")
    .setSG("ga", date(2016, 12, 8), None),
  Attorney("Carrie J. Williams")
    .setAG("md.assistant", date(2016, 1, 1), None),
  Attorney("Nancy Winkelman")
    .setDA("phi", date(2017, 11, 1), None),
]

