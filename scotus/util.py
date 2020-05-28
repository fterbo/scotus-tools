# Copyright (c) 2018-2020  Floyd Terbo

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
from . import justices

HEADERS = {"User-Agent" : "SCOTUS Docket Utility (https://github.com/fterbo/scotus-tools)"}
QPURL = "https://www.supremecourt.gov/qp/%d-%05dqp.pdf"
OQPURL = "https://www.supremecourt.gov/qp/%d%%20origqp.pdf"

PETITION_LINKS = set(["Petition", "Appendix", "Jurisdictional Statement"])
PETITION_TYPES = set(["certiorari", "mandamus", "habeas", "jurisdiction", "prohibition", "stay",
                      "bail", "extension", "excess"])

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
    self.oldurl = False
    self.petitioner_title = None
    self.respondent_title = None

    self.petitioner_parties = []
    self.respondent_parties = []

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
    self.remanded = False
    self.abuse = False
    self.ifp_denied = False
    self.ifp_paid = False

    self.vacated = False
    self.affirmed = False
    self.reversed = False

    self.atty_petitioner_prose = None
    self.attys_petitioner_cor = []
    self.attys_respondent_cor = []
    self.attys_petitioner = []
    self.attys_respondent = []
    self.atty_email = []

    self.attys_amici = []
    self.cert_amici = []
    self.merits_amici = []

    self.recusals = set([])

    self._errors = []

    self._docket_data = docket_obj

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
  def docketurl (self):
    if self.oldurl:
      return "https://www.supremecourt.gov/search.aspx?filename=/docketfiles/%s.htm" % (self.docketstr)
    else:
      return "https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/%s.html" % (self.docketstr)

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
    END_TERMS = ["TABLE", "PARTIES", "CORPORATE DISCLOSURE", "LIST OF", "RULE 29.6",
                 "CERT. GRANTED", "INTERESTED PARTIES", "NO.", "Parties to the Proceedings",
                 "PETITION FOR WRIT", "List of all Parties", "List of Parties", "No. ____",
                 "CONSTITUTIONAL PROVISION", "OPINIONS BELOW", "TOPICAL INDEX", "RELIEF SOUGHT",
                 "JURISDICTION"]
    qp_lines = []
    capture = False
    done = False
    for line in sout.split("\n"):
      if not capture:
        for term in START_TERMS:
          if line.strip().count(term):
            capture = True
            continue
      else:
        for term in END_TERMS:
          if line.strip().count(term):
            done = True
            break
        if done:
          break
        qp_lines.append(line)

    with open("%s/qp.txt" % (self.docketdir), "w+") as qpf:
      qpf.write("\n".join(qp_lines))

  def getQPText (self, generate_only = False):
    qptxtpath = "%s/qp.txt" % (self.docketdir)
    if not os.path.exists(qptxtpath):
      self._generateQPText()
    if not generate_only:
      return open(qptxtpath, "r").read()

  def getConfAction (self, rcdate, clist = None):
    nextc = None
    if clist:
      for idx,cdate in enumerate(clist):
        if rcdate == cdate:
          if idx+1 < len(clist):
            nextc = clist[idx+1]
          break

    for (edate, cdate, resch) in self.distributed:
      if cdate == rcdate and resch:
        return "RESCHEDULED"
      if nextc and cdate == nextc:
        return "RELISTED"

    # Go through events after the conference date and see if we find
    # something useful
    post = False
    for event in self.events:
      if event.date < rcdate:
        continue

      if event.distributed and (event.date > rcdate):
        return ""

      # We found events after the conference date
      post = True

      if event.dismissed:
        return "DISMISSED"
      elif event.mooted:
        return "MOOT"
      elif event.remanded:
        return "REMANDED"
      elif event.granted:
        return "GRANTED"
      elif event.removed:
        return "REMOVED"
      elif event.denied:
        return "DENIED"
      elif event.cvsg:
        return "CVSG"
      elif event.ifp_denied:
        return "IFP DENIED"
      elif event.response_requested:
        return "RESPONSE"
      elif event.record_requested:
        return "RECORD"
      elif event.rehearing_denied:
        return "RH DENIED"
      elif event.affirmed:
        return "AFFIRMED"
      elif event.inquorate:
        return "INQUORATE"
      elif event.motion_denied:
        return "MOTION DENY"
      elif event.counsel_granted:
        return "COUNSEL"

    if not post:
      return ""
    else:
      return "UNKNOWN"

  def _build (self, docket_obj):
    if "oldurl" in docket_obj:
      self.oldurl = docket_obj["oldurl"]

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

      try:
        self.casename = buildCasename(docket_obj)
      except exceptions.CasenameError:
        if not exceptions.CasenameError.IGNORE:
          raise

      self.casetype = getCaseType(docket_obj)

      if "PetitionerTitle" in docket_obj:
        self.petitioner_title = docket_obj["PetitionerTitle"]
      if "RespondentTitle" in docket_obj:
        self.respondent_title = docket_obj["RespondentTitle"]

      if "Petitioner" in docket_obj:
        for info in docket_obj["Petitioner"]:
          if info["IsCounselofRecord"]:
            self.attys_petitioner_cor.append(info["Attorney"])
          if (info["Attorney"] == info["PartyName"]) or info["PrisonerId"]:
            self.atty_petitioner_prose = info["Attorney"]
          self.attys_petitioner.append(info["Attorney"])
          self.petitioner_parties.append(info["PartyName"])
          if "Email" in info:
            self.atty_email.append(info["Email"])

      if "Respondent" in docket_obj:
        for info in docket_obj["Respondent"]:
          self.attys_respondent.append(info["Attorney"])
          if info["IsCounselofRecord"]:
            self.attys_respondent_cor.append(info["Attorney"])
          self.respondent_parties.append(info["PartyName"])
          if "Email" in info:
            self.atty_email.append(info["Email"])

      if "Other" in docket_obj:
        for info in docket_obj["Other"]:
          self.attys_amici.append(info["Attorney"])
          if "Email" in info:
            self.atty_email.append(info["Email"])

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

        evtobj = events.DocketEvent(einfo)
        self.events.append(evtobj)

        etxt = einfo["Text"]
        estxt = etxt
        if etxt[-6:] == "VIDED." or etxt[-5:] == "VIDED":
          estxt = " ".join(etxt.split()[:-1])

        if etxt.startswith("DISTRIBUTED"):
          if etxt == "DISTRIBUTED.":
            continue  # Rehearing distribution, probably, not for conference
          if etxt.startswith("DISTRIBUTED."): # Old Event
            confdate = dateutil.parser.parse(etxt.split(".")[-1]).date()
          else:
            confdate = dateutil.parser.parse(etxt.split("of")[-1]).date()
          edate = dateutil.parser.parse(einfo["Date"]).date()
          self.distributed.append((edate, confdate, False))
          evtobj.distributed = True
        elif etxt == "Rescheduled.":
          last_dist = self.distributed[-1]
          self.distributed[-1] = (last_dist[0], last_dist[1], True)
        elif etxt.startswith("Brief amici curiae of") or etxt.startswith("Brief amicus curiae of"):
          evtobj.amicus_brief = True
          if etxt.count("Court-appointed"):
            evtobj.court_appointed = True
          if not self.granted:
            self.cert_amici.append(" ".join(estxt.split()[4:-1]))
          else:
            self.merits_amici.append(" ".join(estxt.split()[4:-1]))
          if self.cvsg:
            if (etxt.lower().startswith("brief amicus curiae of united states filed") or
                etxt.lower().startswith("brief amicus curiae of the united states filed") or
                etxt.startswith("Brief amicus curiae of United States of America filed")):
              self.cvsg_return_date = dateutil.parser.parse(einfo["Date"]).date()
              evtobj.cvsg_return = True
        elif (etxt.startswith("Supplemental brief of")
              or etxt.startswith("Brief of respondent")
              or etxt.startswith("Brief of petitioner")
              or etxt.startswith("Reply of petitioner")
              or etxt.startswith("Reply of respondent")
              or (etxt.startswith("Brief of") and estxt[-6:] == "filed.")
              or (etxt.count("letter brief") and etxt.count("filed."))):
          if self.cvsg and etxt.lower().startswith("brief of federal respondents in opposition filed"):
            self.cvsg_return_date = dateutil.parser.parse(einfo["Date"]).date()
            evtobj.cvsg_return = True
            evtobj.amicus_brief = True
          else:
            evtobj.brief = True
        elif etxt.startswith("The Solicitor General is invited to file a brief"):
          self.cvsg = True
          self.cvsg_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.cvsg = True
        elif etxt == "Petition GRANTED.":
          self.granted = True
          self.grant_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.granted = True
        elif etxt == "CIRCULATED":
          evtobj.circulated = True
        elif etxt.startswith("SET FOR ARGUMENT"):
          evtobj.set_for_argument = True
        elif etxt.startswith("SET FOR REARGUMENT"):
          evtobj.set_for_reargument = True
        elif (etxt.startswith("Record received from")
              or etxt.startswith("Record") and etxt.count("is electronic")):
          evtobj.record_received = True
        elif (etxt.startswith("Motion of the Solicitor General for leave to participate in oral argument")
              and etxt.count("divided argument")):
          if etxt.count("filed"):
            evtobj.sg_motion_divided_argument = True
          elif etxt.count("GRANTED"):
            evtobj.sg_grant_divided_argument = True
        elif etxt.startswith("Motion for divided argument filed"):
          if (etxt.count("by the Solicitor General") or
              etxt.lower().count("by federal respondents")):
            if etxt[-7:] == "DENIED.":
              evtobj.sg_motion_divided_denied = True
            elif etxt[-8:] == "GRANTED.":
              evtobj.sg_motion_divided_granted = True
            else:
              evtobj.sg_motion_divided_argument = True
          else:
            if etxt[-7:] == "DENIED.":
              evtobj.motion_divided_denied = True
            elif etxt[-8:] == "GRANTED.":
              evtobj.motion_divided_granted = True
        elif (etxt.startswith("Motion") and etxt.count("divided argument filed.")):
          evtobj.motion_divided_argument = True
        elif etxt.count("GRANTED"):
          if etxt.count("for leave to file"): continue
          if etxt.count("Motion to substitute"): continue
          if etxt.count("Motion of respondent for leave"): continue
          if etxt.count("Motion to appoint counsel"):
            evtobj.counsel_granted = True
            continue
          statements = etxt.split(".")
          gs = [x for x in statements if x.count("GRANTED")][0]
          if gs.count("expedite consideration"):
            continue
          self.granted = True
          self.grant_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.granted = True
          if etxt.count("REVERSED") and etxt.count("REMANDED"):
            # This is not really a GVR, but we'll throw it in the bucket for now
            self.gvr = True
            self.gvr_date = self.grant_date
            self.remanded = True
            self.reversed = True
            evtobj.remanded = True
          elif etxt.lower().count("vacated") and etxt.lower().count("remanded"):
            self.gvr = True
            self.gvr_date = self.grant_date
            self.remanded = True
            self.vacated = True
            evtobj.vacated = True
            evtobj.remanded = True
        elif etxt.lower().count("is dismissed as moot"):
          evtobj.mooted = True
        elif (etxt.count("petition for certiorari is granted") or
              etxt.count("petition for a writ of certiorari is granted")):
          self.granted = True
          evtobj.granted = True
          self.grant_date = dateutil.parser.parse(einfo["Date"]).date()
          if etxt.count("to dismiss the case as moot"):
            evtobj.mooted = True
          if etxt.count("the case is remanded for further proceedings"):
            self.remanded = True
            evtobj.remanded = True
        elif etxt.startswith("Argued."):
          self.argued = True
          self.argued_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.argued = True
        elif etxt.count("lacks a quorum"):
          self.inquorate = True
          evtobj.inquorate = True
        elif (etxt.startswith("Petition Dismissed") or
              etxt.startswith("Petition DISMISSED") or
              etxt.startswith("Appeal dismissed") or
              etxt.count("petition for a writ of certiorari is DISMISSED")):
          self.dismissed = True
          self.dismiss_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.dismissed = True
        elif (etxt.startswith("Petition DENIED")
              or etxt.count("The petition for a writ of certiorari is denied")
              or etxt.count("before judgment DENIED")):
          self.denied = True
          self.deny_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.denied = True
        elif (etxt.startswith("Rehearing DENIED") or
              (etxt.startswith("Motion for leave to file a petition for rehearing")
               and etxt.count("DENIED"))):
          evtobj.rehearing_denied = True
        elif (etxt.lower().count("petition for rehearing filed")):
          evtobj.rehearing_requested = True
        elif (etxt.startswith("Motion for reconsideration") and etxt.count("DENIED")):
          evtobj.motion_denied = True
        elif (etxt.lower().startswith("judgment issued") or etxt.lower().startswith("mandate issued")):
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.issued = True
        elif (etxt.startswith("Adjudged to be AFFIRMED.")
              or etxt.count("judgment is affirmed under 28 U. S. C.")
              or etxt.count("Judgment is affirmed")
              or etxt.count("Judgment AFFIRMED")):
          self.affirmed = True
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.affirmed = True
          evtobj.issued = True
        elif etxt.startswith("Adjudged to be AFFIRMED IN PART, REVERSED IN PART"):
          self.affirmed = True
          self.reversed = True
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.affirmed = True
          evtobj.reversed = True
          evtobj.issued = True
        elif etxt.startswith("Adjudged to be VACATED IN PART"):
          self.vacated = True
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.vacated = True
          evtobj.issued = True
        elif etxt.startswith("Judgment REVERSED"):
          self.reversed = True
          self.judgment_issued = True
          self.judgment_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.issued = True
        elif (etxt.count("petition for a writ of certiorari is dismissed")
              or etxt.count("petition for a writ of mandamus/prohibition is dismissed")
              or etxt.count("petition for a writ of habeas corpus is dismissed")
              or etxt.count("petition for a writ of prohibition is dismissed")
              or etxt.count("petition for a writ of mandamus is dismissed")
              or etxt.count("petition for a writ of mandamus and/or prohibition is dismissed")):
          self.dismissed = True
          self.dismiss_date = dateutil.parser.parse(einfo["Date"]).date()
          evtobj.dismissed = True
        elif (etxt.count("Case removed from Docket")
              or etxt == "Case considered closed."):
          self.removed = True
          evtobj.removed = True
        elif etxt.count("leave to proceed in forma pauperis is denied"):
          evtobj.ifp_denied = True
          self.ifp_denied = True
        elif etxt.startswith("Response Requested"):
          evtobj.response_requested = True
        elif etxt.lower().startswith("record requested"):
          evtobj.record_requested = True
        elif etxt.startswith("Petitioner complied with order of"):
          odate = dateutil.parser.parse(etxt.split("of")[-1]).date()
          for evt in self.events:
            if evt.date == odate and evt.ifp_denied:
              self.ifp_paid = True
              evtobj.ifp_paid = True
              break
            if evt.date > odate:
              break
        elif etxt.count("time to file"):
          evtobj.time_to_file = True
        elif etxt.count("Judgment VACATED"):
          evtobj.vacated = True
          self.vacated = True
        elif (etxt.count("Letter of petitioner")
              or etxt.count("Letter of respondent")
              or etxt.startswith("Letter from the Solicitor General")
              or etxt.count("Letter in reply")):
          evtobj.letter = True
        elif etxt.lower().startswith("joint motion"):
          evtobj.joint_motion = True
        elif etxt.lower().startswith("joint appendix filed"):
          evtobj.joint_appendix = True
        elif etxt.lower().startswith("blanket consent filed by petitioner"):
          evtobj.petitioner_blanket_consent = True
        elif etxt.lower().startswith("blanket consent filed by respondent"):
          evtobj.respondent_blanket_consent = True
        elif etxt.startswith("Consent to the filing of amicus curiae briefs"):
          if etxt.count(" either party") and etxt.count("neither party"):
            if etxt.count("received from counsel for petitioner"):
              evtobj.petitioner_blanket_consent = True
            elif etxt.count("received from counsel for respondent"):
              evtobj.respondent_blanket_consent = True

        if etxt.lower().count("remanded"):
          self.remanded = True
          evtobj.remanded = True

        if etxt.lower().count("vacated as moot"):
          self.vacated = True
          evtobj.vacated = True
          evtobj.mooted = True

        if etxt.count("not accepted for filing."):
          evtobj.not_accepted = True

        if etxt.count("petitioner has repeatedly abused"):
          self.abuse = True

        if etxt.count("took no part in the consideration"):
          wlist = etxt.split()
          for idx,word in enumerate(wlist):
            if word == "Justice":
              if wlist[idx-1] == "Chief":
                self.recusals.add(TERMS["%02d" % (self.term)]["chief"])
              else:
                self.recusals.add(wlist[idx+1])

    except Exception:
      print "Exception in case: %s" % (docket_obj["CaseNumber"])
      raise

  @property
  def pending (self):
    if self.dismissed or self.denied or self.judgment_issued or self.gvr or self.removed:
      return False
    return True

  def getTagDict (self):
    tags = {"cvsg" : False, "related" : False, "capital" : False, "abuse" : False,
            "ifp" : False, "paid" : False, "rh_requested" : False}

    if self.cvsg: tags["cvsg"] = True
    if self.capital: tags["capital"] = True
    if self.related: tags["related"] = True
    if self.abuse: tags["abuse"] = True
    if not self.original and not self.application:
      if self.docket < 5000: tags["paid"] = True
      if self.docket > 5000: tags["ifp"] = True
      if self.ifp_paid: tags["paid"] = True

    for evt in self.events:
      if evt.rehearing_requested:
        tags["rh_requested"] = True
        break

    return tags

  def getHoldingDict (self):
    hmap = {"vacated" : False, "affirmed" : False, "reversed" : False}

    if self.vacated: hmap["vacated"] = True
    if self.affirmed: hmap["affirmed"] = True
    if self.reversed: hmap["reversed"] = True
    return hmap

  def getFlagDict (self):
    flags = {"granted" : False, "argued" : False, "dismissed" : False, "denied" : False,
             "removed" : False, "issued" : False, "remanded" : False}

    if self.granted: flags["granted"] = True
    if self.remanded: flags["remanded"] = True
    if self.argued: flags["argued"] = True
    if self.dismissed: flags["dismissed"] = True
    if self.denied: flags["denied"] = True
    if self.removed: flags["removed"] = True
    if self.judgment_issued: flags["issued"] = True
    return flags

  @property
  def current_status (self):
    if self.judgment_issued: return "ISSUED"
    if self.argued: return "ARGUED"
    if self.dismissed: return "DISMISSED"
    if self.removed: return "REMOVED"
    if self.denied: return "DENIED"
    if self.gvr: return "GVR"
    if self.remanded: return "REMANDED"
    if self.granted: return "GRANTED"
    return "PENDING"

  def getFlagString (self):
    flags = self.getFlagList()
    if flags:
      return "[%s]" % (", ".join(flags))
    else:
      return ""

  def getFlagList (self):
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
    return flags


def getCaseType (docket_obj):
  if docket_obj["ProceedingsandOrder"]:
    if docket_obj["ProceedingsandOrder"][0]["Text"].startswith("Statement as to jurisdiction"):
      return "mandatory"

  founditem = application = None
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

  if ("PetitionerTitle" in docket_obj) and ("RespondentTitle" in docket_obj):
    # TODO: Yes yes, we'll fix it later
    return "certiorari"

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
        parts = pt.split(",")
        if parts[-1].count("Petitioner") or parts[-1].count("Plaintiff"):
          petitioner = ",".join(parts[:-1])
        else:
          petitioner = pt
        if casetype == "excess":
          casename = "(unrelated-application) %s" % (petitioner)
        else:
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
      droot = "%s/OT-%d/dockets/A/%s" % (root, term, number[1:])
    elif number[0:3] == "22O":
      droot = "%s/Orig/dockets/%s" % (root, number[3:])
  else:
    droot = "%s/OT-%d/dockets/%d" % (root, term, number)

  if not os.path.exists("%s/docket.json" % (droot)):
    raise exceptions.NoDocketError("%s%s" % (term, str(number)))

  jd = json.loads(open("%s/docket.json" % (droot), "rb").read())
  if os.path.exists("%s/patch.json" % (droot)):
    jd.update(json.loads(open("%s/patch.json" % (droot), "rb").read()))

  return DocketStatusInfo(jd)
