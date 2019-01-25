(function() {
  'use strict';
  $.getJSON("data/conf/20190111.json", function(data){
    GenerateTable(data);
  });
  var caseName = "case-name";
  var qp = "qp";
  var lcInfo = "lc-info";
  var docketUrl = "docket-url";
  var lcAbbr = "lc-abbr";
  var distCount = "dist-count";
  var docketStr = "docket-str";
  var distDetails = "dist-details";
  var reschCount = "resch-count";
  var caseType = "case-type";
  var currentStatus = "current-status";
  var flags = "flags"
  function GenerateTable(data) {
    for(var i=0; i<data.dockets.length; i++){
      var thisCase = data.dockets[i]
      $("#conf > tbody:last-child").append
      (
        "<tr id=\""+thisCase[docketStr]+"\" "+addClass(thisCase[currentStatus])+">"+
          TdTag(docketStr, docketNumberLink(thisCase)) +
          TdTag(caseType, thisCase[caseType]) +
          TdTag(lcAbbr,thisCase[lcAbbr]) +
          TdTag(
            caseName+"-td",
            caseNameTD(thisCase)
          ) +
          TdTag(flags, flagsColumn(thisCase[flags]))+
          TdTag(
            "dist-td",
            details(
              thisCase[distCount] + "(" + thisCase[reschCount] + " Resch)",
              "dist-summary",
              thisCase[distDetails],
              distDetails)
            ) +
            TdTag(currentStatus, thisCase[currentStatus])+
        "</tr>"
      );
    }
  }
  function TdTag(id, content, classes){
    return "<td id=\""+ id + "\""
    + addClass(classes)+" >" + content + "</td>";
  }
  function addClass(classes) {
    if (typeof classes === 'undefined' || classes === null ){
      return "";
    } else {
      return "class=\""+ classes + "\""
    }
  }
  function details(summary, summaryID, pre, preID) {
      return "<details> <summary id =\""+summaryID+"\">"
      + summary + "</summary> "+
      "<pre id=\""+ preID + "\">" + pre + "</pre> </details>";
  }
  function translateTags(thisCaseFlags) {
    var result = "";
    if(thisCaseFlags.capital){
      result += "{CAPITAL}";
    }
    if(thisCaseFlags.related){
      result += "{RELATED}";
    }
    if(thisCaseFlags.cvsg){
      result += "{CVSG}"
    }
    return result.replace("}{", "}</br>{" )
  }
  function flagsExist(thisCaseFlags) {
    return thisCaseFlags.capital || thisCaseFlags.related || thisCaseFlags.cvsg;
  }
  function flagsColumn(thisCaseFlags){
    if(flagsExist(thisCaseFlags)){
      return translateTags(thisCaseFlags);
    } else {
      return "";
    }
  }
  function docketNumberLink(thisCase) {
    return "<a href=\""+thisCase[docketUrl] + "\">"+ thisCase[docketStr] + "</a>";
  }
  function caseNameTD(thisCase){
    var caseQp = thisCase[qp];
    if (typeof caseQp === 'undefined' || caseQp === null ){
      return thisCase[caseName] ;
    } else {
      return details(
        thisCase[caseName],
        caseName+"-summary",
        thisCase[qp],
        qp
      );
    }
  }
}());
