# Copyright (c) 2018  Floyd Terbo

class CourtMatch(object):
  def __init__ (self, *args):
    self.names = args
    self.start = []
    self.partial = None

  def __eq__ (self, val):
    if not val:
      return False
    if val in self.names:
      return True
    if self.start:
      for frag in self.start:
        if val.startswith(frag):
          return True
    if self.partial and val.count(self.partial):
      return True
    return False

  def __ne__ (self, val):
    return not self == val

  def setStart (self, val):
    self.start.append(val)
    return self

  def setPartial (self, val):
    self.partial = val
    return self


NAMEMAP = {
  "None" : None,

  "CA1" : "United States Court of Appeals for the First Circuit",
  "CA2" : "United States Court of Appeals for the Second Circuit",
  "CA3" : "United States Court of Appeals for the Third Circuit",
  "CA4" : "United States Court of Appeals for the Fourth Circuit",
  "CA5" : "United States Court of Appeals for the Fifth Circuit",
  "CA6" : "United States Court of Appeals for the Sixth Circuit",
  "CA7" : "United States Court of Appeals for the Seventh Circuit",
  "CA8" : "United States Court of Appeals for the Eighth Circuit",
  "CA9" : "United States Court of Appeals for the Ninth Circuit",
  "CA10" : "United States Court of Appeals for the Tenth Circuit",
  "CA11" : "United States Court of Appeals for the Eleventh Circuit",
  "CADC" : CourtMatch("United States Court of Appeals for the DC Circuit",
                           "United States Court of Appeals for the District of Columbia Circuit"),
  "CAFC" : "United States Court of Appeals for the Federal Circuit",
  "CAAF" : "United States Court of Appeals for the Armed Forces",

  "caAK" : "Court of Appeals of Alaska",
  "caAL" : CourtMatch("Court of Criminal Appeals of Alabama",
                           "Court of Civil Appeals of Alabama").setStart("Circuit Court of Alabama"),
  "caAZ" : CourtMatch().setStart("Court of Appeals of Arizona"),
  "caCA" : CourtMatch().setStart("Court of Appeal of California"),
  "caCO" : "Court of Appeals of Colorado",
  "caCT" : "Appellate Court of Connecticut",
  "caDC" : "District of Columbia Court of Appeals",
  "caFL" : CourtMatch().setStart("District Court of Appeal of Florida"),
  "caGA" : "Court of Appeals of Georgia",
  "caIA" : "Court of Appeals of Iowa",
  "caID" : "Court of Appeals of Idaho",
  "caIL" : CourtMatch().setStart("Appellate Court of Illinois"),
  "caIN" : CourtMatch().setStart("Court of Appeals of Indiana"),
  "caKS" : "Court of Appeals of Kansas",
  "caKY" : "Court of Appeals of Kentucky",
  "caLA" : CourtMatch().setStart("Court of Appeal of Louisiana"),
  "caMA" : "Appeals Court of Massachusetts",
  "caMD" : CourtMatch("Court of Appeals of Maryland", "Court of Special Appeals of Maryland"),
  "caMI" : CourtMatch().setStart("Court of Appeals of Michigan"),
  "caMN" : "Court of Appeals of Minnesota",
  "caMO" : CourtMatch().setStart("Court of Appeals of Missouri"),
  "caMS" : "Court of Appeals of Mississippi",
  "caNB" : "Court of Appeals of Nebraska",
  "caNC" : "Court of Appeals of North Carolina",
  "caNJ" : "Superior Court of New Jersey, Appellate Division",
  "caNM" : "Court of Appeals of New Mexico",
  "caNV" : "Court of Appeals of Nevada",
  "caNY" : CourtMatch().setStart("Appellate Division, Supreme Court of New York"),
  "caOH" : CourtMatch().setStart("Court of Appeals of Ohio"),
  "caOK" : CourtMatch().setStart("Court of Civil Appeals of Oklahoma")
                            .setStart("Court of Criminal Appeals of Oklahoma"),
  "caOR" : "Court of Appeals of Oregon",
  "caPA" : CourtMatch("Commonwealth Court of Pennsylvania").setStart("Superior Court of Pennsylvania"),
  "caSC" : "Court of Appeals of South Carolina",
  "caTN" : CourtMatch().setStart("Court of Criminal Appeals of Tennessee")
                            .setStart("Court of Appeals of Tennessee"),
  "caTX" : CourtMatch().setStart("Court of Appeals of Texas"),
  "caUT" : "Court of Appeals of Utah",
  "caWA" : CourtMatch().setStart("Court of Appeals of Washington"),
  "caWI" : CourtMatch().setStart("Court of Appeals of Wisconsin"),
  "caWY" : CourtMatch().setStart("District Court of Wyoming"),

  "dcMD" : "United States District Court for the District of Maryland",
  "dcMNC" : "United States District Court for the Middle District of North Carolina",
  "dcEPA" : "United States District Court for the Eastern District of Pennsylvania",
  "dcWTX" : "United States District Court for the Western District of Texas",

  "minAZ" : CourtMatch().setStart("Superior Court of Arizona"),
  "minCA" : CourtMatch().setStart("Appellate Division, Superior Court of California"),
  "minCO" : CourtMatch().setStart("District Court of Colorado"),
  "minGA" : CourtMatch().setStart("Superior Court of Georgia"),
  "minMD" : CourtMatch().setStart("Circuit Court of Maryland"),
  "minNC" : CourtMatch().setStart("Superior Court of North Carolina"),
  "minNM" : CourtMatch().setStart("District Court of New Mexico"),
  "minWV" : CourtMatch().setStart("Circuit Court of West Virginia"),

  "scAK" : "Supreme Court of Alaska",
  "scAL" : "Supreme Court of Alabama",
  "scAR" : "Supreme Court of Arkansas",
  "scAZ" : "Supreme Court of Arizona",
  "scCA" : "Supreme Court of California",
  "scCO" : "Supreme Court of Colorado",
  "scCT" : "Supreme Court of Connecticut",
  "scDE" : "Supreme Court of Delaware",
  "scFL" : "Supreme Court of Florida",
  "scGA" : "Supreme Court of Georgia",
  "scGU" : "Supreme Court of Guam",
  "scHI" : "Supreme Court of Hawaii",
  "scIA" : "Supreme Court of Iowa",
  "scID" : "Supreme Court of Idaho",
  "scIL" : "Supreme Court of Illinois",
  "scIN" : "Supreme Court of Indiana",
  "scKA" : "Supreme Court of Kansas",
  "scKY" : "Supreme Court of Kentucky",
  "scLA" : "Supreme Court of Louisiana",
  "scMA" : "Supreme Judicial Court of Massachusetts",
  "scME" : "Supreme Judicial Court of Maine",
  "scMI" : "Supreme Court of Michigan",
  "scMN" : "Supreme Court of Minnesota",
  "scMO" : "Supreme Court of Missouri",
  "scMS" : "Supreme Court of Mississippi",
  "scMT" : "Supreme Court of Montana",
  "scNB" : "Supreme Court of Nebraska",
  "scNC" : "Supreme Court of North Carolina",
  "scND" : "Supreme Court of North Dakota",
  "scNH" : "Supreme Court of New Hampshire",
  "scNJ" : "Supreme Court of New Jersey",
  "scNM" : "Supreme Court of New Mexico",
  "scNV" : "Supreme Court of Nevada",
  "scNY" : "Court of Appeals of New York",
  "scOH" : "Supreme Court of Ohio",
  "scOK" : "Supreme Court of Oklahoma",
  "scOR" : "Supreme Court of Oregon",
  "scPA" : CourtMatch().setStart("Supreme Court of Pennsylvania"),
  "scPR" : "Supreme Court of Puerto Rico",
  "scRI" : "Supreme Court of Rhode Island",
  "scSC" : "Supreme Court of South Carolina",
  "scSD" : "Supreme Court of South Dakota",
  "scTN" : CourtMatch().setStart("Supreme Court of Tennessee"),
  "scTX" : CourtMatch("Supreme Court of Texas", "Court of Criminal Appeals of Texas"),
  "scUT" : "Supreme Court of Utah",
  "scVT" : "Supreme Court of Vermont",
  "scVA" : "Supreme Court of Virginia",
  "scWA" : "Supreme Court of Washington",
  "scWI" : "Supreme Court of Wisconsin",
  "scWV" : "Supreme Court of Appeals of West Virginia",
  "scWY" : "Supreme Court of Wyoming",
}

