

(function () {
  'use strict';
  var term = "term";
  var conferences = "confdates";
  var termID = "confyears";
  var currentStatusIndex = 6;
  GetConfData(PopulateTerms);
  $(document).ready(function(){
    var table = $('#conf').DataTable({
      ordering:true,
      paging:false,
      "autoWidth": false,
      createdRow:function( row, data, dataIndex){
        $(row).addClass(data[currentStatusIndex])
      },
      columns:
        [
          {
            title:"Docket"
          },
          {title:"Type"},
          {title:"Tags"},
          {title:"LC"},
          {title:"Case"},
          {title:"Dist"},
          {title:"Current<br/>Status"}
        ]
    });
    $("#"+termID).change(
      function(){
        PopulateConferences();
      });
    $("#"+conferences).change(
      function() {
        PopulateReport(table);
      });
    }
  );


  function GetConfData(action){
    $.getJSON("data/confdates.json?_=" + new Date().getTime(),
      function(data){
        action(data);
      }
    )
  }

  function PopulateReport(table) {
    ConfTable.PopulateTable($("#"+conferences).find(":selected").val());
  }

  function PopulateTerms(data){
    var currentTerm = "";
    //this operates on the assumption that the dates are already sorted in descending order.
    for(var termIndex=0; termIndex<data.terms.length; termIndex++){
      var thisTerm = data.terms[termIndex];
        currentTerm=ChangeCurrentTermIfHigher(thisTerm, currentTerm);
        AddNewOption(termID, thisTerm[term], "OT"+thisTerm[term]);
      }
      $("#"+termID).val(currentTerm);
      PopulateConferences();
    }

  function PopulateConferences(){
    GetConfData(PopulateConferencesWith);
  }

  function addLeadingZero(number) {
     return ("0" + number).slice(-2)
  }

  function PopulateConferencesWith(data){
    $("#"+conferences).empty();
    var thisTerm = $.grep(data["terms"], function (n, i){
      return n[term] == $("#"+termID).find(":selected").val();
      }
    );
    var thisTermConferences =  thisTerm[0][conferences];
    for (var i = 0; i< thisTermConferences.length; i++){
      var thisConf=thisTermConferences[i];
      var thisConfDate = new Date(thisConf["y"], thisConf["m"]-1, thisConf["d"]);
      AddNewOption(conferences, ""+thisConfDate.getFullYear()+addLeadingZero(thisConfDate.getMonth()+1)+addLeadingZero(thisConf["d"]), thisConf["y"]+"-"+thisConf["m"]+"-"+thisConf["d"] )
    }
    PopulateReport();
  }
  function AddNewOption(selectID, optionValue, optionDescription){
    $("#"+ selectID).append("<option value=\""+ optionValue +"\" id=\"" +selectID + optionValue + "\">"+ optionDescription +"</option>" )
  }

  function ChangeCurrentTermIfHigher(thisTerm, currentTerm) {
    if(thisTerm[term]>currentTerm){
      return thisTerm[term];
    } else {
      return currentTerm;
    }
  }
}());

var ConfTable = (function() {
  'use strict';
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

//  function table(){
//    return;
//  }

  var tableData = []
  return{
     PopulateTable:function(date){
      $.getJSON("data/conf/"+date+".json?_=" + new Date().getTime(),
      function(data, tableParam){
         $('#conf').DataTable().clear();
        GenerateTable(data);
         $('#conf').DataTable().draw();
      });
    }
  }
  $(document).ready(function(){
    SetIcons();
  });
  function SetIcons() {
    $("."+lcAbbr).each(function() {
      $(this).qtip({
          content: {
              text: $(this).next('.tooltiptext')
          }
      });
    });
  }
  function GenerateTable(data) {
  //  table.clear();
    for(var i=0; i<data.dockets.length; i++){
      addRow(data.dockets[i]);
    }
  //  table.rows.add(tableData);
  }
  function addRow(thisCase) {
     $('#conf').DataTable().row.add(
      [
        TdTag(docketStr, docketNumberLink(thisCase)) ,
        TdTag(caseType, translateType(thisCase[caseType])),
        TdTag(flags, flagsColumn(thisCase[flags])),
        TdTag(lcAbbr,thisCase[lcAbbr], "", thisCase[lcInfo]) ,
        TdTag(caseName+"-td", caseNameTD(thisCase)),
        TdTag(
          "dist-td",
          details(
            thisCase[distCount] + "(" + thisCase[reschCount] + " Resch)",
            "dist-summary",
            thisCase[distDetails],
            distDetails)
          ),
         thisCase[currentStatus]
      ]
    );
  }
  function TdTag(id, content, classes, title){
    return "<div id=\""+ id + "\""+ addClass(classes) + ">" + content  + "</div>"+ addTitle(title);
  }
  function addTitle(title) {
    if (!(typeof title === 'undefined' || title === null )){
      return " <div class=\"tooltiptext\">" + title + "</div>";
    } else {
      return "";
    }
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
      result += "<i class=\"fas fa-exclamation-triangle\" title=\"Capital\"></i>";
    }
    if(thisCaseFlags.related){
      result += "<i class=\"fas fa-arrows-alt-h\" title=\"Related\"></i>";
    }
    if(thisCaseFlags.cvsg){
      result += "<a href=\"/reports/cvsg.html\"><i class=\"fas fa-question-circle\" title=\"CVSG\"></i></a>";
    }
    return result;
  }
  function translateType(thisCaseType){
    var className;
    if (thisCaseType == "certiorari"){
      className = "fas fa-microscope";
    } else if (thisCaseType == "habeas") {
      className = "fas fa-hands";
    } else if (thisCaseType == "original"){
      className = "fas fa-balance-scale";
    } else if (thisCaseType == "prohibition"){
      className = "fas fa-ban";
    } else if (thisCaseType == "mandamus"){
      className = "fas fa-hand-point-right";
    } else {
      className = "fas fa-question";
    }
    return "<i class=\"" + className + " \" title=\""+thisCaseType+"\"></i>";
  }
  function flagsExist(thisCaseFlags) {;
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
