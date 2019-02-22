var confJSONNames = (function() {
  'use strict';
  return {
    caseName: "case-name",
    qp: "qp",
    lcInfo: "lc-info",
    docketUrl: "docket-url",
    lcAbbr: "lc-abbr",
    distCount: "dist-count",
    docketStr: "docket-str",
    distDetails: "dist-details",
    reschCount: "resch-count",
    caseType: "case-type",
    currentStatus: "current-status",
    confAction: "conf-action",
    flags: "flags",
    tags: "tags"
  }
}());


(function() {
  'use strict';
  var term = "term";
  var conferences = "confdates";
  var termID = "confyears";
  var currentStatusIndex = 6;
  GetConfData(PopulateTerms);
  $(document).ready(function() {
    var table = $('#conf').DataTable({
      ordering: true,
      paging: false,
      "autoWidth": false,
      createdRow: function(row, data, dataIndex) {
        $(row).addClass(data[confJSONNames.currentStatus].display)
      },
      search: {
        "caseInsensitive": true
      },
      columns: [{
          title: "Docket",
          data: confJSONNames.docketStr,
          width:50,
          render: function(data, type, row) {
            if (type === "sort") {
              return data.caseNum;
            } else if (type == "filter") {
              return data.docketNumber;
            } else {
              return "<a href=\"" + data.link + "\" target=\"_blank\">" + data.docketNumber + "</a>";
            }
          },
          className: "dt-body-right"
        },
        {
          title: "Type",
          data: confJSONNames.caseType,
          width:50,
          render: {
            "_": "value",
            "display": "display"
          }
        },
        {
          title: "Tags",
          data: confJSONNames.tags,
          width:50,
          render: {
            "_": "value",
            "display": "display"
          }
        },
        {
          title: "LC",
          width:50,
          data: confJSONNames.lcAbbr
        },
        {
          title: "Case",
          data: confJSONNames.caseName
        },
        {
          title: "Dist",
          width:100,
          data: confJSONNames.distCount
        },
        {
          title: "Conference <br/>Action",
          data: confJSONNames.confAction,
          width:100,
          render: {
            "_": "value"
          }
        },
        {
          title: "Current <br/>Status",
          width:100,
          data: confJSONNames.currentStatus,
          render: {
            "_": "value",
            "display": "display"
          }
        }
      ]
    });
    createSearchBoxes(table);
    $("#" + termID).change(
      function() {
        PopulateConferences();
      });
    $("#" + conferences).change(
      function() {
        PopulateReport(table);
      });
  });

  function createSearchBoxes(table) {
    $('#conf thead th').each( function () {
      var title = $(this).text();
      var width = "50px";
      var lastColumnsList = ["Dist","Conference Action","Current Status"];
      if (title == "Case") {
        width="100%";
      } else if (lastColumnsList.indexOf(title) >-1 ) {
        width="85px"
      }
      $(this).html( $(this).html() + '<br /> <input type="text" placeholder="Search" style="width:'+width+'"/>' );
    } );
    table.columns().every( function () {
        var that = this;

        $( 'input', this.header() ).on( 'keyup change', function () {
            if ( that.search() !== this.value ) {
                that
                    .search( this.value )
                    .draw();
            }
        } );
    } );
  }

  function GetConfData(action) {
    $.getJSON("data/confdates.json?_=" + new Date().getTime(),
      function(data) {
        action(data);
      }
    )
  }

  function PopulateReport(table) {
    ConfTable.PopulateTable($("#" + conferences).find(":selected").val());
  }

  function PopulateTerms(data) {
    var currentTerm = "";
    //this operates on the assumption that the dates are already sorted in descending order.
    for (var termIndex = 0; termIndex < data.terms.length; termIndex++) {
      var thisTerm = data.terms[termIndex];
      currentTerm = ChangeCurrentTermIfHigher(thisTerm, currentTerm);
      AddNewOption(termID, thisTerm[term], "OT" + thisTerm[term]);
    }
    $("#" + termID).val(currentTerm);
    PopulateConferences();
  }

  function PopulateConferences() {
    GetConfData(PopulateConferencesWith);
  }

  function addLeadingZero(number) {
    return ("0" + number).slice(-2)
  }

  function PopulateConferencesWith(data) {
    $("#" + conferences).empty();
    var thisTerm = $.grep(data["terms"], function(n, i) {
      return n[term] == $("#" + termID).find(":selected").val();
    });
    var thisTermConferences = thisTerm[0][conferences];
    for (var i = 0; i < thisTermConferences.length; i++) {
      var thisConf = thisTermConferences[i];
      var thisConfDate = new Date(thisConf["y"], thisConf["m"] - 1, thisConf["d"]);
      AddNewOption(conferences, "" + thisConfDate.getFullYear() + addLeadingZero(thisConfDate.getMonth() + 1) + addLeadingZero(thisConf["d"]), thisConf["y"] + "-" + thisConf["m"] + "-" + thisConf["d"])
    }
    PopulateReport();
  }

  function AddNewOption(selectID, optionValue, optionDescription) {
    $("#" + selectID).append("<option value=\"" + optionValue + "\" id=\"" + selectID + optionValue + "\">" + optionDescription + "</option>")
  }

  function ChangeCurrentTermIfHigher(thisTerm, currentTerm) {
    if (thisTerm[term] > currentTerm) {
      return thisTerm[term];
    } else {
      return currentTerm;
    }
  }
}());

var ConfTable = (function() {
  'use strict';
  var caseName = confJSONNames.caseName;
  var qp = confJSONNames.qp;
  var lcInfo = confJSONNames.lcInfo;
  var docketUrl = confJSONNames.docketUrl;
  var lcAbbr = confJSONNames.lcAbbr;
  var distCount = confJSONNames.distCount;
  var docketStr = confJSONNames.docketStr;
  var distDetails = confJSONNames.distDetails;
  var reschCount = confJSONNames.reschCount;
  var caseType = confJSONNames.caseType;
  var currentStatus = confJSONNames.currentStatus;
  var tags = confJSONNames.tags;
  var tableData = []
  return {
    PopulateTable: function(date) {
      $.getJSON("data/conf/" + date + ".json?_=" + new Date().getTime(),
        function(data, tableParam) {
          $('#conf').DataTable().clear();
          GenerateTable(data);
          $('#conf').DataTable().draw();
        });
    }
  }
  $(document).ready(function() {
    SetIcons();
  });

  function SetIcons() {
    $("." + lcAbbr).each(function() {
      $(this).qtip({
        content: {
          text: $(this).next('.tooltiptext')
        }
      });
    });
  }

  function GenerateTable(data) {
    //  table.clear();
    for (var i = 0; i < data.dockets.length; i++) {
      addRow(data.dockets[i]);
    }
    //  table.rows.add(tableData);
  }

  function addRow(thisCase) {
    $('#conf').DataTable().row.add({
      [docketStr]: {
        "docketNumber": thisCase[docketStr],
        "link": thisCase[docketUrl],
        "caseNum": getSortableDocketNumber(thisCase[docketStr])
      },
      [caseType]: {
        display: TdTag(caseType, translateType(thisCase[caseType])),
        value: thisCase[caseType]
      },
      [tags]: {
        display: TdTag(confJSONNames.tags, tagsColumn(thisCase[confJSONNames.tags], translateTagsToIcons)),
        value: tagsColumn(thisCase[confJSONNames.tags], translateTagsToText)
      },
      [lcAbbr]: TdTag(lcAbbr, thisCase[lcAbbr], "", thisCase[lcInfo]),
      [caseName]: TdTag(caseName + "-td", caseNameTD(thisCase)),
      [distCount]: TdTag(
        "dist-td",
        details(
          thisCase[distCount] + "(" + thisCase[reschCount] + " Resch)",
          "dist-summary",
          thisCase[distDetails],
          distDetails)
      ),
      [confJSONNames.confAction]: {
        value: thisCase[confJSONNames.confAction]
      },
      [currentStatus]: {
        display: thisCase[currentStatus],
        value: translateFlagsToText(thisCase[confJSONNames.flags])
      }
    });
  }

  function TdTag(id, content, classes, title) {
    return "<div id=\"" + id + "\"" + addClass(classes) + ">" + content + "</div>" + addTitle(title);
  }

  function addTitle(title) {
    if (!(typeof title === 'undefined' || title === null)) {
      return " <div class=\"tooltiptext\">" + title + "</div>";
    } else {
      return "";
    }
  }

  function addClass(classes) {
    if (typeof classes === 'undefined' || classes === null) {
      return "";
    } else {
      return "class=\"" + classes + "\""
    }
  }

  function details(summary, summaryID, pre, preID) {
    return "<details> <summary id =\"" + summaryID + "\">" +
      summary + "</summary> " +
      "<pre id=\"" + preID + "\">" + pre + "</pre> </details>";
  }

  function translateTagsToIcons(thisCaseFlags) {
    var result = "";
    if (thisCaseFlags.capital) {
      result += "<i class=\"fas fa-exclamation-triangle\" title=\"Capital\"></i>";
    }
    if (thisCaseFlags.related) {
      result += "<i class=\"fas fa-arrows-alt-h\" title=\"Related\"></i>";
    }
    if (thisCaseFlags.cvsg) {
      result += "<a href=\"/reports/cvsg.html\"><i class=\"fas fa-question-circle\" title=\"CVSG\"></i></a>";
    }
    if (thisCaseFlags.abuse) {
      result += "<i class=\"far fa-angry\" title=\"abuse\"></i>"
    }
    return result;
  }

  function translateFlagsToText(thisCaseFlags) {
    var result = "";
    if (thisCaseFlags.issued) {
      result += "issued"
    }
    if (thisCaseFlags.granted) {
      result += "granted"
    }
    if (thisCaseFlags.dismissed) {
      result += "dismissed"
    }
    if (thisCaseFlags.remanded) {
      result += "remanded"
    }
    if (thisCaseFlags.denied) {
      result += "denied"
    }
    if (thisCaseFlags.argued) {
      result += "argued"
    }
    if (thisCaseFlags.removed) {
      result += "removed"
    }
    return result;
  }

  function translateTagsToText(thisCaseFlags) {
    var result = "";
    if (thisCaseFlags.capital) {
      result += "capital";
    }
    if (thisCaseFlags.related) {
      result += "related";
    }
    if (thisCaseFlags.cvsg) {
      result += "cvsg";
    }
    if (thisCaseFlags.abuse) {
      result += "abuse"
    }
    return result;
  }

  function translateType(thisCaseType) {
    var className;
    if (thisCaseType == "certiorari") {
      className = "fas fa-microscope";
    } else if (thisCaseType == "habeas") {
      className = "fas fa-hands";
    } else if (thisCaseType == "original") {
      className = "fas fa-balance-scale";
    } else if (thisCaseType == "prohibition") {
      className = "fas fa-ban";
    } else if (thisCaseType == "mandamus") {
      className = "fas fa-hand-point-right";
    } else {
      className = "fas fa-question";
    }
    return "<i class=\"" + className + " \" title=\"" + thisCaseType + "\"></i>";
  }

  function tagsExist(thisCaseFlags) {

    return thisCaseFlags.capital || thisCaseFlags.related || thisCaseFlags.cvsg || thisCaseFlags.abuse;
  }

  function tagsColumn(thisCaseFlags, action) {
    if (tagsExist(thisCaseFlags)) {
      return action(thisCaseFlags);
    } else {
      return "";
    }
  }

  function pad(num, size) {
    var s = num + "";
    while (s.length < size) s = "0" + s;
    return s;
  }

  function getSortableDocketNumber(docketNumber) {

    var caseNumber = docketNumber.split("-");
    var caseYear = caseNumber[0]
    var caseID = pad(caseNumber[1], 5)
    return parseFloat(caseYear + "." + caseID);
  }

  function docketNumberLink(thisCase) {
    return "<a href=\"" + thisCase[docketUrl] + "\>" + thisCase[docketStr] + "</a>";
  }

  function caseNameTD(thisCase) {
    var caseQp = thisCase[qp];
    if (typeof caseQp === 'undefined' || caseQp === null) {
      return thisCase[caseName];
    } else {
      return details(
        thisCase[caseName],
        caseName + "-summary",
        thisCase[qp],
        qp
      );
    }
  }
}());
