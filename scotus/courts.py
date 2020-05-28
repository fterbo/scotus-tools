# Copyright (c) 2018-2020  Floyd Terbo

class CourtMatch(object):
  def __init__ (self, *args):
    self.names = args
    self.start = []
    self.partial = []

  def __eq__ (self, val):
    if not val:
      return False
    val = val.lower()
    if val in [x.lower() for x in self.names]:
      return True
    if self.start:
      for frag in self.start:
        if val.startswith(frag):
          return True
    if self.partial:
      for part in self.partial:
        if val.count(part):
          return True
    return False

  def __ne__ (self, val):
    return not self == val

  def setStart (self, val):
    self.start.append(val.lower())
    return self

  def setPartial (self, val):
    self.partial.append(val.lower())
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
  "caAR" : "Court of Appeals of Arkansas",
  "caAZ" : CourtMatch().setStart("Court of Appeals of Arizona"),
  "caCA" : CourtMatch().setStart("Court of Appeal of California"),
  "caCO" : "Court of Appeals of Colorado",
  "caCT" : "Appellate Court of Connecticut",
  "caDC" : "District of Columbia Court of Appeals",
  "caFL" : CourtMatch().setStart("District Court of Appeal of Florida"),
  "caGA" : "Court of Appeals of Georgia",
  "caHI" : "Intermediate Court of Appeals of Hawaii",
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
  "caNE" : "Court of Appeals of Nebraska",
  "caNC" : "Court of Appeals of North Carolina",
  "caNJ" : "Superior Court of New Jersey, Appellate Division",
  "caNM" : "Court of Appeals of New Mexico",
  "caNV" : "Court of Appeals of Nevada",
  "caNY" : CourtMatch().setStart("Appellate Division, Supreme Court of New York")
                          .setStart("Appellate Term of the Supreme Court of New York"),
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

  "dcAZ" : "United States District Court for the District of Arizona",
  "dcDC" : "United States District Court for the District of Columbia",
  "dcEAK" : "United States District Court for the Eastern District of Arkansas",
  "dcEMI" : "United States District Court for the Eastern District of Michigan",
  "dcEPA" : "United States District Court for the Eastern District of Pennsylvania",
  "dcEVA" : "United States District Court for the Eastern District of Virginia",
  "dcHI" : "United States District Court for the District of Hawaii",
  "dcMD" : "United States District Court for the District of Maryland",
  "dcMAL" : "United States District Court for the Middle District of Alabama",
  "dcMNC" : "United States District Court for the Middle District of North Carolina",
  "dcNIL" : "United States District Court for the Northern District of Illinois",
  "dcNMS" : "United States District Court for the Northern District of Mississippi",
  "dcNTX" : "United States District Court for the Northern District of Texas",
  "dcSC" : "United States District Court for the District of South Carolina",
  "dcSCA" : "United States District Court for the Southern District of California",
  "dcSGA" : "United States District Court for the Southern District of Georgia",
  "dcSMS" : "United States District Court for the Southern District of Mississippi",
  "dcSOH" : "United States District Court for the Southern District of Ohio",
  "dcSWV" : "United States District Court for the Southern District of West Virginia",
  "dcWWI" : "United States District Court for the Western District of Wisconsin",
  "dcWTX" : "United States District Court for the Western District of Texas",

  "minAZ" : CourtMatch().setStart("Superior Court of Arizona"),
  "minCA" : CourtMatch().setPartial("Superior Court of California"),
  "minCO" : CourtMatch().setStart("District Court of Colorado"),
  "minDE" : "Superior Court of Delaware",
  "minFL" : CourtMatch().setStart("Circuit Court of Florida"),
  "minGA" : CourtMatch().setStart("Superior Court of Georgia"),
  "minIA" : CourtMatch().setStart("District Court of Iowa"),
  "minKY" : CourtMatch().setStart("Circuit Court of Kentucky"),
  "minLA" : CourtMatch().setPartial("Judicial District Court of Louisiana")
                          .setStart("District Court of Louisiana")
                          .setPartial("Criminal District Court of Louisiana"),
  "minMA" : CourtMatch().setStart("Superior Court of Massachusetts"),
  "minMD" : CourtMatch().setStart("Circuit Court of Maryland"),
  "minMI" : CourtMatch().setStart("Circuit Court of Michigan"),
  "minMS" : CourtMatch().setStart("Circuit Court of Mississippi"),
  "minNB" : CourtMatch().setStart("District Court of Nebraska"),
  "minNC" : CourtMatch().setStart("Superior Court of North Carolina"),
  "minNH" : CourtMatch().setStart("Superior Court of New Hampshire"),
  "minNJ" : CourtMatch().setStart("Superior Court of New Jersey"),
  "minNV" : CourtMatch().setStart("District Court of Nevada"),
  "minNY" : CourtMatch().setStart("County Court of New York")
                          .setStart("Supreme Court of New York")
                          .setPartial("Judicial District of New York")
                          .setPartial("City of New York"),
  "minOR" : CourtMatch().setStart("Circuit Court of Oregon"),
  "minPA" : CourtMatch().setStart("Court of Common Pleas of Pennsylvania"),
  "minSC" : CourtMatch().setStart("Court of Common Pleas of South Carolina"),
  "minTX" : CourtMatch().setPartial("District Court of Texas")
                          .setPartial("County, Texas"),
  "minNM" : CourtMatch().setStart("District Court of New Mexico"),
  "minWV" : CourtMatch().setStart("Circuit Court of West Virginia"),
  "minVA" : CourtMatch().setStart("Circuit Court of Virginia"),
  "minWA" : CourtMatch().setStart("Superior Court of Washington"),

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
  "scNMI" : "Supreme Court of the Commonwealth of the Northern Mariana Islands",
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
  "scVI" : "Supreme Court of the Virgin Islands",
  "scWA" : "Supreme Court of Washington",
  "scWI" : "Supreme Court of Wisconsin",
  "scWV" : "Supreme Court of Appeals of West Virginia",
  "scWY" : "Supreme Court of Wyoming",
}

