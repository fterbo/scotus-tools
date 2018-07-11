# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import

import codecs
import os
import os.path
import sys
import urllib

import dateutil.parser

PETITION_LINKS = set(["Petition", "Appendix", "Jurisdictional Statement"])
PETITION_TYPES = set(["certiorari", "mandamus", "habeas", "jurisdiction", "prohibition"])

class SCOTUSError(Exception): pass

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


class DocketStatusInfo(object):
  def __init__ (self, docket_obj):
    self.docket_date = None
    self.term = None
    self.docket = None
    self.capital = False
    self.casename = None
    self.casetype = None
    self.lowercourt = None
    self.lowercourt_docket = None
    self.lowercourt_decision_date = None
    self.petition_path = None

    self.related = []

    self.granted = False
    self.grant_date = None
    self.argued = False
    self.argued_date = None
    self.distributed = []
    self.dismissed = False
    self.dismiss_date = None
    self.denied = False
    self.deny_date = None
    self.judgment_issued = False
    self.judgment_date = None
    self.gvr = False
    self.gvr_date = None

    self.attys_petitioner = []
    self.attys_respondent = []
    self.cert_amici = []

    self._errors = []

    self._build(docket_obj)

  def __hash__ (self):
    return hash("%d-%d" % (self.term, self.docket))

  def _getLocalPath (self, link):
    path1 = "OT-%d/dockets/%d/%s" % (self.term, self.docket, link["File"])
    if os.path.exists(path1):
      return path1

    fname = urllib.unquote_plus(link["DocumentUrl"].split("/")[-1])
    path2 = "OT-%d/dockets/%d/%s" % (self.term, self.docket, fname)
    if os.path.exists(path2):
      return path2


  def _build (self, docket_obj):
    (tstr,dstr) = docket_obj["CaseNumber"].split()[0].split("-")
    self.term = int(tstr)
    self.docket = int(dstr)

    try:
      self.docket_date = dateutil.parser.parse(docket_obj["DocketedDate"])
      self.capital = docket_obj["bCapitalCase"]
      self.casename = buildCasename(docket_obj)
      self.casetype = getCaseType(docket_obj)

      if "Petitioner" in docket_obj:
        for info in docket_obj["Petitioner"]:
          self.attys_petitioner.append(info["Attorney"])

      if "Respondent" in docket_obj:
        for info in docket_obj["Respondent"]:
          self.attys_respondent.append(info["Attorney"])

      if "RelatedCaseNumber" in docket_obj:
        for rc in docket_obj["RelatedCaseNumber"]:
          rcnl = rc["DisplayCaseNumber"].split(",")
          for rcn in rcnl:
            (tstr, dstr) = rcn.split("-")
            self.related.append((int(tstr), int(dstr), rc["RelatedType"]))

      if "LowerCourt" in docket_obj and docket_obj["LowerCourt"]:
        self.lowercourt = docket_obj["LowerCourt"].strip()
        try:
          self.lowercourt_docket = docket_obj["LowerCourtCaseNumbers"]
          self.lowercourt_decision_date = dateutil.parser.parse(docket_obj["LowerCourtDecision"]).date()
        except KeyError:
          pass
        except ValueError as e:
          self._errors.append(str(e))

      for event in docket_obj["ProceedingsandOrder"]:
        try:
          for link in event["Links"]:
            if link["Description"] == "Petition":
              self.petition_path = self._getLocalPath(link)
        except KeyError:
          pass

        etxt = event["Text"]
        if etxt.startswith("DISTRIBUTED"):
          confdate = dateutil.parser.parse(etxt.split()[-1]).date()
          edate = dateutil.parser.parse(event["Date"]).date()
          self.distributed.append((edate, confdate))
        elif etxt.startswith("Brief amici curiae of"):
          if not self.granted:
            self.cert_amici.append(" ".join(etxt.split()[4:-1]))
        elif etxt == "Petition GRANTED.":
          self.granted = True
          self.grant_date = dateutil.parser.parse(event["Date"]).date()
        elif etxt.count("GRANTED"):
          statements = etxt.split(".")
          gs = [x for x in statements if x.count("GRANTED")][0]
          if gs.count("expedite consideration"):
            continue
          self.granted = True
          self.grant_date = dateutil.parser.parse(event["Date"]).date()
          if etxt.count("REVERSED") and etxt.count("REMANDED"):
            # This is not really a GVR, but we'll throw it in the bucket for now
            self.gvr = True
            self.gvr_date = self.grant_date
          elif etxt.count("VACATED") and etxt.count("REMANDED"):
            self.gvr = True
            self.gvr_date = self.grant_date
        elif etxt.startswith("Argued."):
          self.argued = True
          self.argued_date = dateutil.parser.parse(event["Date"]).date()
        elif etxt.startswith("Petition Dismissed"):
          self.dismissed = True
          self.dismiss_date = dateutil.parser.parse(event["Date"]).date()
        elif etxt.startswith("Petition DENIED"):
          self.denied = True
          self.deny_date = dateutil.parser.parse(event["Date"]).date()
        elif etxt == "JUDGMENT ISSUED.":
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(event["Date"]).date()
        elif etxt.startswith("Adjudged to be AFFIRMED."):
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(event["Date"]).date()
        elif etxt.startswith("Judgment REVERSED"):
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(event["Date"]).date()
        elif etxt.count("petition for a writ of certiorari is dismissed"):
          self.dismissed = True
          self.dismiss_date = dateutil.parser.parse(event["Date"]).date()
    except Exception:
      print "Exception in case: %s" % (docket_obj["CaseNumber"])
      raise

  @property
  def pending (self):
    if self.dismissed or self.denied or self.judgment_issued or self.gvr:
      return False
    return True

  def getFlagString (self):
    flags = []
    if self.capital: flags.append("CAPITAL")
    if self.related: flags.append("RELATED")
    if self.argued: flags.append("ARGUED")
    if self.gvr:
      flags.append("GVR")
    else:
      if self.granted: flags.append("GRANTED")
      if self.dismissed: flags.append("DISMISSED")
      if self.denied: flags.append("DENIED")
      if self.judgment_issued: flags.append("ISSUED")
    if flags:
      return "[%s]" % (", ".join(flags))
    else:
      return ""


def getCaseType (docket_obj):
  if ("PetitionerTitle" in docket_obj) and ("RespondentTitle" in docket_obj):
    # TODO: Yes yes, we'll fix it later
    return "certiorari"

  founditem = None
  for item in docket_obj["ProceedingsandOrder"]:
    try:
      if item["Text"].startswith("Petition"):
        for ptype in PETITION_TYPES:
          if item["Text"].count(ptype):
            return ptype
      for link in item["Links"]:
        if link["Description"] == "Petition":
          # TODO: This does not tend to capture original actions or mandatory appeals
          founditem = item
          break
      if founditem:
        break
    except KeyError:
      continue

  if not founditem:
    raise CaseTypeError(docket_obj["CaseNumber"].strip())

  match = list(set(founditem["Text"].split()) & PETITION_TYPES)
  return match[0]


def buildCasename (docket_obj):
  casetype = getCaseType(docket_obj)

  casename = ""
  try:
    # TODO: This is all horrible, but works for most cases
    if casetype in ["mandamus", "habeas"]:
      pt = docket_obj["PetitionerTitle"]
      parts = pt.split(",")
      if parts[-1].count("Petitioner"):
        casename = ",".join(parts[:-1])
      else:
        casename = pt
    else:
      pt = docket_obj["PetitionerTitle"]
      if pt[:5] == "In Re":
        parts = pt.split(",")
        if parts[-1].count("Petitioner"):
          casename = ",".join(parts[:-1])
        else:
          casename = pt
      else:
        petitioner = docket_obj["PetitionerTitle"][:-12]  # Remove ", Petitioner" from metadata
        casename = "%s v. %s" % (petitioner, docket_obj["RespondentTitle"])
  except Exception:
    raise CasenameError(docket_obj["CaseNumber"].strip())

  return casename


def setOutputEncoding (encoding='utf-8'):
  if not sys.stdout.encoding:
    sys.stdout = codecs.getwriter(encoding)(sys.stdout)
  if not sys.stderr.encoding:
    sys.stderr = codecs.getwriter(encoding)(sys.stderr)
    
