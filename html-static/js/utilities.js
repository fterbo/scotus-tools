var utilities =(function() {
  'use strict';
  return {
      getQP: function (term, caseNumber) {
      return $.getJSON("data/qps/" + term + "/" + caseNumber + ".json)";
      )
    },
    getCaseData:function (term, caseNumber){
      return   $.getJSON("data/cases/"+term"/"+caseNumber+".json?_=" + new Date().getTime(),
    }
  }
}());
