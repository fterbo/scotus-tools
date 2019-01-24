(function() {
  'use strict';
  $.getJSON("data/conf/20190215.json", function(data){
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
  function GenerateTable(data) {
    for(var i=0; i<data.dockets.length; i++){
      var thisCase = data.dockets[i]
      $("#conf > tbody:last-child").append
      (
        "<tr id=\""+thisCase[docketStr]+"\">"+
          TdTag(docketStr, thisCase[docketStr]) +
          TdTag(lcAbbr,thisCase[lcAbbr]) +
          TdTag(
            caseName+"-td",
            details(
              thisCase[caseName],
              caseName+"-summary",
              thisCase[qp],
              qp
            )
          ) +
          TdTag(
            "dist-td",
            details(
              thisCase[distCount] + "("+thisCase[reschCount] + " Resch)",
              "dist-summary",
              thisCase[distDetails],
              distDetails)
            ) +
        "</tr>"
      );
    }
  }
  function TdTag(id, content){
    return "<td id=\""+ id + "\">" + content + "</td>";
  }
  function details(summary, summaryID, pre, preID) {
      return "<details> <summary id =\""+summaryID+"\">"
      + summary + "</summary> "+
      "<pre id=\""+ preID + "\">" + pre + "</pre> </details>";
  }
}());
