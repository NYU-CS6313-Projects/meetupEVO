/*
 *   Adapted from https://github.com/Edouard-Legoupil/3W-Dashboard/blob/gh-pages/index.html
 *   and https://stackoverflow.com/questions/20853794/dc-js-permalink-or-href-to-share-the-visualisation-filter-state
 */

function status_to_url() {
  var filters = [
    { name: 'no-members'   , value: noMembersChart.filters()   } ,
    { name: 'no-events'    , value: noEventsChart.filters()    } ,
    { name: 'date-created' , value: dateCreatedChart.filters() } ,
    { name: 'categories'   , value: categoriesChart.filters()  } 
  ];
  var recursiveEncoded = $.param( filters );
  location.hash = recursiveEncoded;
}

function url_to_status() {
  // Get hash values
  var parseHash = /^#no-members=([A-Za-z0-9,_\.\-\/\s]*)&no-events=([A-Za-z0-9,_\.\-\/\s]*)&date-created=([A-Za-z0-9,_\.\-\/\s]*)&categories=([A-Za-z0-9,_\-\/\s]*)$/;
  var parsed = parseHash.exec(decodeURIComponent(location.hash));
  function filter(chart, rank) {  // for instance chart = sector_chart and rank in URL hash = 1
    // sector chart
    if (parsed[rank] == "") {
      chart.filter(null);
    }
    else {
      var filterValues = parsed[rank].split(",");
      if (rank < 4) {
        for (var i = 0; i < filterValues.length; i++ ) {
          filterValues[i] = parseFloat( filterValues[i] );
        }
      }
      chart.filter(filterValues);
    }
  }
  if (parsed) {
    filter(noMembersChart, 1);
    filter(noEventsChart, 2);
    filter(dateCreatedChart, 3);
    filter(categoriesChart, 4);
  } else {
    console.log("could not parse " + decodeURIComponent(location.hash));
  }
  console.log(".");
}
