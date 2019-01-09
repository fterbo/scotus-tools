# Copyright (c) 2018  Floyd Terbo

from __future__ import absolute_import

import codecs
import json
import logging
import os
import os.path
import subprocess
import sys
import urllib

import dateutil.parser
import requests

from . import events
from . import exceptions

HEADERS = {"User-Agent" : "SCOTUS Docket Utility (https://github.com/fterbo/scotus-tools)"}
QPURL = "https://www.supremecourt.gov/qp/%d-%05dqp.pdf"
OQPURL = "https://www.supremecourt.gov/qp/%d%%20origqp.pdf"

PETITION_LINKS = set(["Petition", "Appendix", "Jurisdictional Statement"])
PETITION_TYPES = set(["certiorari", "mandamus", "habeas", "jurisdiction", "prohibition", "stay",
                      "bail", "extension"])

def GET (url):
  logging.debug("GET: %s" % (url))
  return requests.get(url, headers=HEADERS)


class MultiMatch(object):
  def __init__ (self, *args):
    self.matches = args

  def __eq__ (self, val):
    if not val:
      return False
    if val in self.matches:
      return True
    return False


class DocketStatusInfo(object):
  def __init__ (self, docket_obj):
    self.docket_date = None
    self.term = None
    self.docket = None
    self.original = False
    self.application = False
    self.capital = False
    self.casename = None
    self.casetype = None
    self.lowercourt = None
    self.lowercourt_docket = None
    self.lowercourt_decision_date = None
    self.petition_path = None

    self.related = []

    self.events = []
    self.granted = False
    self.grant_date = None
    self.cvsg = False
    self.cvsg_date = None
    self.cvsg_return_date = None
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
    self.removed = False

    self.atty_petitioner_prose = None
    self.atty_petitioner_cor = None
    self.atty_respondent_cor = None
    self.attys_petitioner = []
    self.attys_respondent = []

    self.attys_amici = []
    self.cert_amici = []

    self._errors = []

    self._build(docket_obj)

  def __hash__ (self):
    return hash(self.docketstr)

  @property
  def docketstr (self):
    if self.original:
      return "22O%d" % (self.docket)
    elif self.application:
      return "%dA%d" % (self.term, self.docket)
    return "%d-%d" % (self.term, self.docket)

  @property
  def audiodocketstr (self):
    if self.original:
      return "%d-Orig" % (self.docket)
    return self.docketstr

  @property
  def docketdir (self):
    if self.original:
      path = "Orig/dockets/%d" % (self.docket)
    elif self.application:
      path = "OT-%d/dockets/A/%d" % (self.term, self.docket)
    else:
      path = "OT-%d/dockets/%d" % (self.term, self.docket)
    return path

  def _getLocalPath (self, link):
    path1 = "%s/%s" % (self.docketdir, link["File"])
    if os.path.exists(path1):
      return path1

    fname = urllib.unquote_plus(link["DocumentUrl"].split("/")[-1])
    path2 = "%s/%s" % (self.docketdir, fname)
    if os.path.exists(path2):
      return path2

  def _generateQPText (self):
    if self.granted:
      if self.original:
        r = GET(OQPURL % (self.docket))
      elif self.application:
        raise exceptions.NoPetitionForApplicationError(self.docketstr)
      else:
        r = GET(QPURL % (self.term, self.docket))

      if r.status_code != 200:
        logging.warning("%s returned code %d" % (r.url, r.status_code))
        open("%s/qp.txt" % (self.docketdir), "w+").close()
        return

      outpath = "%s/%s" % (self.docketdir, r.url.split("/")[-1])
      with open(outpath, "w+") as outfile:
        outfile.write(r.content)
    else:
      outpath = self.petition_path

    p = subprocess.Popen("pdftotext -layout \"%s\" -" % (outpath), stdout = subprocess.PIPE,
                         stderr = subprocess.PIPE, shell=True)
    (sout, serr) = p.communicate()

    START_TERMS = ["QUESTION PRESENTED", "QUESTIONS PRESENTED", "STATEMENT OF THE QUESTION"]
    END_TERMS = ["TABLE", "PARTIES TO", "CORPORATE DISCLOSURE", "LIST OF", "RULE 29.6",
                 "CERT. GRANTED"]
    qp_lines = []
    capture = False
    done = False
    for line in sout.split("\n"):
      if not capture:
        for term in START_TERMS:
          if line.strip().startswith(term):
            capture = True
            continue
      else:
        for term in END_TERMS:
          if line.strip().startswith(term):
            done = True
            break
        if done:
          break
        qp_lines.append(line)

    with open("%s/qp.txt" % (self.docketdir), "w+") as qpf:
      qpf.write("\n".join(qp_lines))

  def getQPText (self):
    qptxtpath = "%s/qp.txt" % (self.docketdir)
    if not os.path.exists(qptxtpath):
      self._generateQPText()
    return open(qptxtpath, "r").read()

  def _build (self, docket_obj):
    if docket_obj["CaseNumber"].startswith("22O"):
      self.original = True
      self.docket = int(docket_obj["CaseNumber"][3:])
    elif docket_obj["CaseNumber"].split()[0].count("A"):
      self.application = True
      (tstr,dstr) = docket_obj["CaseNumber"].split()[0].split("A")
      self.term = int(tstr)
      self.docket = int(dstr)
    else:
      (tstr,dstr) = docket_obj["CaseNumber"].split()[0].split("-")
      self.term = int(tstr)
      self.docket = int(dstr)

    try:
      if docket_obj["DocketedDate"].strip():
        self.docket_date = dateutil.parser.parse(docket_obj["DocketedDate"]).date()
      self.capital = docket_obj["bCapitalCase"]
      self.casename = buildCasename(docket_obj)
      self.casetype = getCaseType(docket_obj)

      if "Petitioner" in docket_obj:
        for info in docket_obj["Petitioner"]:
          if info["IsCounselofRecord"]:
            self.atty_petitioner_cor = info["Attorney"]
          if (info["Attorney"] == info["PartyName"]) or info["PrisonerId"]:
            self.atty_petitioner_prose = info["Attorney"]
          self.attys_petitioner.append(info["Attorney"])

      if "Respondent" in docket_obj:
        for info in docket_obj["Respondent"]:
          self.attys_respondent.append(info["Attorney"])
          if info["IsCounselofRecord"]:
            self.atty_respondent_cor = info["Attorney"]

      if "Other" in docket_obj:
        for info in docket_obj["Other"]:
          self.attys_amici.append(info["Attorney"])

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

      for einfo in docket_obj["ProceedingsandOrder"]:
        try:
          for link in einfo["Links"]:
            if link["Description"] == "Petition":
              self.petition_path = self._getLocalPath(link)
        except KeyError:
          pass

        self.events.append(events.DocketEvent(einfo))

        etxt = einfo["Text"]
        if etxt.startswith("DISTRIBUTED"):
          if etxt == "DISTRIBUTED.":
            continue  # Rehearing distribution, probably, not for conference
          confdate = dateutil.parser.parse(etxt.split()[-1]).date()
          edate = dateutil.parser.parse(einfo["Date"]).date()
          self.distributed.append((edate, confdate))
        elif etxt.startswith("Brief amici curiae of") or etxt.startswith("Brief amicus curiae of"):
          if not self.granted:
            self.cert_amici.append(" ".join(etxt.split()[4:-1]))
          if self.cvsg:
            if etxt.startswith("Brief amicus curiae of United States filed") or
               etxt.startswith("Brief amicus curiae of United States of America filed"):
              self.cvsg_return_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.startswith("The Solicitor General is invited to file a brief"):
          self.cvsg = True
          self.cvsg_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt == "Petition GRANTED.":
          self.granted = True
          self.grant_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.count("GRANTED"):
          if etxt.count("Motion for leave"): continue
          if etxt.count("Motion to substitute") : continue
          statements = etxt.split(".")
          gs = [x for x in statements if x.count("GRANTED")][0]
          if gs.count("expedite consideration"):
            continue
          self.granted = True
          self.grant_date = dateutil.parser.parse(einfo["Date"]).date()
          if etxt.count("REVERSED") and etxt.count("REMANDED"):
            # This is not really a GVR, but we'll throw it in the bucket for now
            self.gvr = True
            self.gvr_date = self.grant_date
          elif etxt.count("VACATED") and etxt.count("REMANDED"):
            self.gvr = True
            self.gvr_date = self.grant_date
        elif etxt.startswith("Argued."):
          self.argued = True
          self.argued_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.startswith("Petition Dismissed"):
          self.dismissed = True
          self.dismiss_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.startswith("Petition DENIED"):
          self.denied = True
          self.deny_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.count("before judgment DENIED"):
          self.denied = True
          self.deny_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt == "JUDGMENT ISSUED.":
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.startswith("Adjudged to be AFFIRMED."):
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.startswith("Judgment REVERSED"):
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.count("petition for a writ of certiorari is dismissed"):
          self.dismissed = True
          self.dismiss_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.count("petition for a writ of mandamus/prohibition is dismissed"):
          self.dismissed = True
          self.dismiss_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.count("petition for a writ of habeas corpus is dismissed"):
          self.dismissed = True
          self.dismiss_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.count("petition for a writ of mandamus is dismissed"):
          self.dismissed = True
          self.dismiss_date = dateutil.parser.parse(einfo["Date"]).date()
        elif etxt.count("Case removed from Docket"):
          self.removed = True
    except Exception:
      print "Exception in case: %s" % (docket_obj["CaseNumber"])
      raise

  @property
  def pending (self):
    if self.dismissed or self.denied or self.judgment_issued or self.gvr or self.removed:
      return False
    return True

  def getFlagString (self):
    flags = []
    if self.capital: flags.append("CAPITAL")
    if self.gvr:
      flags.append("GVR")
    else:
      if self.granted: flags.append("GRANTED")
    if self.related: flags.append("RELATED")
    if self.cvsg: flags.append("CVSG")
    if self.argued: flags.append("ARGUED")
    if self.dismissed: flags.append("DISMISSED")
    if self.denied: flags.append("DENIED")
    if self.removed: flags.append("REMOVED")
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
    for item in docket_obj["ProceedingsandOrder"]:
      if item["Text"].startswith("Application"):
        founditem = item
        break

  if not founditem:
    raise exceptions.CaseTypeError(docket_obj["CaseNumber"].strip())

  match = list(set(founditem["Text"].replace(",", "").split()) & PETITION_TYPES)
  if not match:
    raise exceptions.CaseTypeError(docket_obj["CaseNumber"].strip())

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
    raise exceptions.CasenameError(docket_obj["CaseNumber"].strip())

  return casename


def setOutputEncoding (encoding='utf-8'):
  if not sys.stdout.encoding:
    sys.stdout = codecs.getwriter(encoding)(sys.stdout)
  if not sys.stderr.encoding:
    sys.stderr = codecs.getwriter(encoding)(sys.stderr)


def buildDocketStr (opts, num = None):
  """Used to build the requested docket string before we know if we have a docket object"""
  if not num:
    num = opts.docket_num

  try:
    if opts.application or opts.action.count("application"):
      return "%dA%d" % (opts.term, num)
    elif opts.orig:
      return "22O%d" % (num)
  except AttributeError:
    pass

  return "%d-%d" % (opts.term, num)

def loadDocket (term, number, root = "."):
  if isinstance(number, (str, unicode)):
    if number[0] == "A":
      jd = json.loads(open("%s/OT-%d/dockets/A/%s/docket.json" % (root, term, number[1:]), "rb").read())
    elif number[0:2] == "22O":
      jd = json.loads(open("%s/OT-%d/dockets/Orig/%s/docket.json" % (root, term, number[3:]), "rb").read())
  else:
    jd = json.loads(open("%s/OT-%d/dockets/%d/docket.json" % (root, term, number), "rb").read())

  return DocketStatusInfo(jd)
