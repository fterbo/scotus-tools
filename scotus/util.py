# Copyright (c) 2018  Floyd Terbo

PETITION_LINKS = set(["Petition", "Appendix", "Jurisdictional Statement"])
PETITION_TYPES = set(["certiorari", "mandamus", "habeas", "jurisdiction"])

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

def getCaseType (docket_obj):
  if ("PetitionerTitle" in docket_obj) and ("RespondentTitle" in docket_obj):
    # TODO: Yes yes, we'll fix it later
    return "certiorari"

  founditem = None
  for item in docket_obj["ProceedingsandOrder"]:
    try:
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
      casename = docket_obj["PetitionerTitle"]
    else:
      petitioner = docket_obj["PetitionerTitle"][:-12]  # Remove ", Petitioner" from metadata
      casename = "%s v. %s" % (petitioner, docket_obj["RespondentTitle"])
  except Exception:
    raise CasenameError(docket_obj["CaseNumber"].strip())

  return casename
