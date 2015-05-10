/* Configuration for Charts */
var timeline_start = new Date(2002, 0, 1);
var timeline_end   = new Date(2015, 0, 1);

var max_no_of_groups_to_display_in_timeline_and_table = 800;

var margin_timelines_left = 60;
var margin_timelines_top = 30;

/* Global for reset-buttons */
var categoriesYearChart = dc.seriesChart('#categories-year-chart');
var evolutionYearChart  = dc.seriesChart('#evolution-year-chart');
var noMembersChart      = dc.barChart('#no-members-chart');
var noEventsChart       = dc.barChart('#no-events-chart');
// var eventsVsPeopleChart = dc.scatterPlot("#events-vs-people");
var dateCreatedChart    = dc.barChart('#date-created-chart');
var categoriesChart     = dc.rowChart('#categories-chart');
var countWidget         = dc.dataCount('#status');
var listOfGroups        = dc.dataTable('.dc-data-table');

/* Global for Debugging */
var groups, groups_by_year, categories_by_year;   // raw data coming in
var meetup = {               // namespace for crossfilter 
  'categories': {}, 
  'evolution': {}, 
  'groups': {}
}; 
function log(s) {
  $('#status').text(s);
  console.log("Status:" + s);
}
function coerce_groups_by_year(d, i) {
  d.index    = i;
  d.sum      = +d.sum;
  d.year = formatCreated.parse( d.time_bin ); // time is already binned to 1st of the year
};
function handle_time_csv(error, gm) {
  log("new timeline data has arrived");
  var more_groups_by_year = gm; 
  var loaded_groups = meetup.evolution.id_group.top(Infinity).map(function(d){return d.key });
  console.log("loaded timeline data on " + more_groups_by_year.length + " groups");
  more_groups_by_year = more_groups_by_year.filter(function(d){ return loaded_groups.indexOf( d.id_group ) == -1; });
  console.log("of these only " + more_groups_by_year.length + " are new, will add them");
  more_groups_by_year.forEach(coerce_groups_by_year);
  meetup.evolution.cf.add(more_groups_by_year);
  var selected_groups = meetup.groups.id_dim.top(Infinity).map(function(d){return d.id_group });
  if ( selected_groups.length < max_no_of_groups_to_display_in_timeline_and_table ) {
    log("showing " + selected_groups.length + " groups in timeline");
    $('#evolution-year-chart img').hide();
    $('#evolution-year-chart svg').show();
    meetup.evolution.id_dim.filter(function(d){ return selected_groups.indexOf(d)>=0 })
    evolutionYearChart.render();
  } else {
    log("too many groups selected, not showing timeline");
    $('#evolution-year-chart img').show();
    $('#evolution-year-chart svg').hide();
    meetup.evolution.id_dim.filter(function(d){ return 0 })
    evolutionYearChart.render();
  }
}
function reload_timeline(){
  log("reloading timeline data for groups");
  var selected_groups = meetup.groups.id_dim.top(Infinity).map(function(d){return d.id_group });
  if ( selected_groups.length < max_no_of_groups_to_display_in_timeline_and_table ) {
    log("Should load timeline data on " + selected_groups.length + " new groups");
    url = "/events/time.csv?" + $.param({id_group:selected_groups});
    queue()
    .defer(d3.csv, url)
    .await(handle_time_csv);
  }

}

function handle_csv(error, g, cy, gm) {
  var dataByGroup, date, dates, id_group, id_groups, nestByGroup; // make global for debugging
  log("data loaded");
  // copy over to global variables
  groups = g;
  categories_by_year = cy;
  groups_by_year = gm; 

  // Various formatters.
  formatInt       = d3.format("f");  // turn any number into integer by dropping digits after point
  formatNumber    = d3.format(",d");  // integer with comma to separate thousands: 1,000
  formatCreated   = d3.time.format("%Y-%m-%d %H:%M:%S");  // to parse dates coming in from csv / json
  formatDate      = d3.time.format("%Y-%m-%d");
  formatMonth     = d3.time.format("%Y, %b");
  formatYearMonth = d3.time.format("%Y-%m");
  formatYear      = d3.time.format("%Y");
  formatTime      = d3.time.format("%I:%M %p");

  // A little coercion, since the loaded JSON and CSV is untyped.
  groups_by_year.forEach(coerce_groups_by_year);
  name_category_of = [];
  index = -1;
  categories_by_year.forEach(function(d, i) {
    d.sum      = +d.sum;
    d.year     = formatCreated.parse( d.time_bin ); // time is already binned to 1st of the year
    if ( index >= 0 && name_category_of[index] == d.name_category ) {
      d.index = index;
    } else {
      index++;
      d.index = index;
      name_category_of[index] = d.shortname_category;
    }
  });
  category_for_group = {};
  meetup.groups.data_by_id_group = {}
  groups.forEach(function(d, i) {
    d.index                = i;
    d.rating               = parseFloat(d.rating);
    d.created              = formatCreated.parse( d.created );
    d.first_event_time     = formatCreated.parse( d.first_event_time );
    d.last_event_time      = formatCreated.parse( d.last_event_time );
    d.no_members           = +d.no_members;
    d.number_of_events     = +d.number_of_events;
    d.max_yes_at_one_event = +d.max_yes_at_one_event;
    d.no_member_who_ever_rsvpd_yes = +d.no_member_who_ever_rsvpd_yes;
    d.average_rsvps_per_event  = parseFloat(d.average_rsvps_per_event);
    if (d.rating == 0.0)  d.rating = null;

    category_for_group[ d.id_group ] = d.shortname_category;
    meetup.groups.data_by_id_group[ d.id_group ] = d;
  });
  meetup.groups.by_id = function(id_group) {
    var d = meetup.groups.data_by_id_group[ id_group ];
    return { get: function(key) {
      if(d == undefined) return "no such group";
      if(d[key] == undefined) return "no attribute " + key;
      return d[key];
    } }
  }

  log("creating crossfilter for evolution by year");
  meetup.evolution.cf = crossfilter(groups_by_year);
  
  meetup.evolution.id_dim   = meetup.evolution.cf.dimension(function(d) { return d.id_group });
  meetup.evolution.id_group = meetup.evolution.id_dim.group().reduceCount();

  meetup.evolution.group_and_year_dim   = meetup.evolution.cf.dimension(function(d) { return [d.id_group, d.year]; });
  meetup.evolution.group_and_year_group = meetup.evolution.group_and_year_dim.group().reduceSum(function(d) { return d.sum; })


  log("creating crossfilter for categories by year");

  meetup.categories.cf = crossfilter(categories_by_year);
  
  meetup.categories.id_dim   = meetup.categories.cf.dimension(function(d) { return d.name_group });
  meetup.categories.id_group = meetup.categories.id_dim.group().reduceCount();

  meetup.categories.category_and_year_dim   = meetup.categories.cf.dimension(function(d) { return [d.index, d.year]; });
  meetup.categories.category_and_year_group = meetup.categories.category_and_year_dim.group().reduceSum(function(d) { return d.sum; })


  log("creating chart for evolution by year");
  evolutionYearChart.width(1000).height(300).margins({top: margin_timelines_top, right: 10, bottom: 30, left: margin_timelines_left})
  .chart(function(c) { return dc.lineChart(c).interpolate('linear').renderArea(0).renderDataPoints(1).dotRadius(5); })
  .brushOn(0)
  .dimension(meetup.evolution.group_and_year_dim)
  .group(meetup.evolution.group_and_year_group)
  .x(d3.time.scale().domain([timeline_start, timeline_end]).rangeRound([0, 10 * 90]))
  .y(d3.scale.linear().domain([0, 9000]).range([250,0]))
  .elasticY(true)
  .title(function (d) { 
    return meetup.groups.by_id( d.key[0] ).get("name") + ": " + d.value + " rsvps this year"; 
  })
  .seriesAccessor(function(d) {return +d.key[0];})
  .keyAccessor(   function(d) {return +d.key[1];})
  .valueAccessor( function(d) {return +d.value;})
  .on('postRender', function(chart){
    chart.selectAll("g.stack path").attr("class",        function(d){ return "category " + category_for_group[ d.name ]; });
    chart.selectAll("g.dc-tooltip circle").attr("class", function(d){ return "category " + category_for_group[ d.name ]; });
  })
  
  categoriesYearChart.width(1000).height(210)
  .margins({top: margin_timelines_top, right: 10, bottom: 30, left: margin_timelines_left})
  .chart(function(c) { return dc.lineChart(c).interpolate('linear').renderArea(0).renderDataPoints(1).dotRadius(5); })
  .dimension(meetup.categories.category_and_year_dim)
  .group(meetup.categories.category_and_year_group)
  .brushOn(0)
  .x(d3.time.scale().domain([timeline_start, timeline_end]).rangeRound([0, 10 * 90]))
  .y(d3.scale.linear().domain([0, 250000]).range([200,0]))
  .elasticY(true)
  .title(function (d) { 
    return name_category_of[d.key[0]] + ": " + d.value + " rsvps in " + d.key[1].getFullYear(); 
  })
  .seriesAccessor(function(d) {return +d.key[0];})
  .keyAccessor(   function(d) {return +d.key[1];})
  .valueAccessor( function(d) {return +d.value;})
  .on('postRender', function(chart){
    chart.selectAll("g.stack path").attr("class", function(d){ return "category " + name_category_of[d.name]; });
    chart.selectAll("g.dc-tooltip circle").attr("class", function(d){ 
      console.log("tying to set class for tooltip");
      console.dir(d);
      return "category " + name_category_of[d.data.key[0]]; 
    });
  });

  categoriesYearChart.yAxis().ticks(5);

  // =======  Groups  =========================================== 
  log("creating crossfilter for groups");

  // Create the crossfilter for the relevant dimensions and groups.
  meetup.groups.cf                = crossfilter(groups);

  meetup.groups.all               = meetup.groups.cf.groupAll();
  meetup.groups.id_dim            = meetup.groups.cf.dimension(function(d) { return d.id_group; });

  meetup.groups.created_dim       = meetup.groups.cf.dimension(function(d) { return d.created; });
  meetup.groups.created_groups    = meetup.groups.created_dim.group(d3.time.day);

  meetup.groups.no_member_dim     = meetup.groups.cf.dimension(function(d) { return d.no_member_who_ever_rsvpd_yes })
  meetup.groups.no_member_groups  = meetup.groups.no_member_dim.group(function(d) { return Math.floor(d / 10) * 10; });

  meetup.groups.no_event_dim      = meetup.groups.cf.dimension(function(d) { return d.number_of_events });
  meetup.groups.no_event_groups   = meetup.groups.no_event_dim.group(function(d) { return Math.floor(d / 10) * 10; });

  meetup.groups.no_event_vs_no_people_dim = meetup.groups.cf.dimension(function(d) { return [d.number_of_events, d.average_rsvps_per_event] });
  meetup.groups.no_event_vs_no_people_groups = meetup.groups.no_event_vs_no_people_dim.group().reduceCount();

  meetup.groups.categories_dim    = meetup.groups.cf.dimension(function(d) { return d.shortname_category; });
  meetup.groups.categories_groups = meetup.groups.categories_dim.group();

  log("creating charts for groups:");

  countWidget.dimension(meetup.groups.cf).group(meetup.groups.all).html({
    some: '%filter-count of %total-count meetup groups selected',
    all: 'All meetup groups selected. Click on charts to apply filters'
  });

  noMembersChart
  .dimension(meetup.groups.no_member_dim)
  .group(meetup.groups.no_member_groups)
  .xUnits(dc.units.integers) 
  .width(230).height(100).margins({top: 10, right: 10, bottom: 30, left: 40})
  .filterPrinter(function (filters) {
    var filter = filters[0];
    return "" + formatInt(filter[0]) + "-" + formatInt(filter[1]);
  })
  .on('filtered', reload_timeline)
  .elasticY(true)
  .x(d3.scale.linear().domain([0, 1500]).rangeRound([0, 10 * 21]));

  noMembersChart.xAxis().ticks(5);
  noMembersChart.yAxis().ticks(4);

  noEventsChart
  .dimension(meetup.groups.no_event_dim)
  .group(meetup.groups.no_event_groups)
  .xUnits(dc.units.integers) 
  .gap(1)
  .width(230).height(100).margins({top: 10, right: 10, bottom: 30, left: 40})
  .filterPrinter(function (filters) {
    var filter = filters[0];
    return "" + formatInt(filter[0]) + "-" + formatInt(filter[1]);
  })
  .on('filtered', reload_timeline)
  .elasticY(true)
  .x(d3.scale.linear().domain([1, 200]).rangeRound([0, 10 * 20]));
  noEventsChart.xAxis().ticks(5);
  noEventsChart.yAxis().ticks(4);

  /*
  eventsVsPeopleChart
  .width(230).height(230).margins({top: 10, right: 10, bottom: 30, left: 40})
  .x(d3.scale.linear().domain([0,200]))
  .brushOn(false)
  .symbolSize(8)
  .dimension(meetup.groups.no_event_vs_no_people_dim)
  .group(meetup.groups.no_event_vs_no_people_groups);
  */

  categoriesChart
  .dimension(meetup.groups.categories_dim)
  .group(meetup.groups.categories_groups)
  .ordering(function(d){ return -d.value })
  .width(230).height(700).margins({top: 10, right: 10, bottom: 30, left: 40})
  .label(function (d) {
    return d.key + " (" + d.value + ")";
  })
  .title(function (d) { return d.value; })
  .on('postRender', function(chart){
    chart.selectAll("g.row rect").attr("class", function(d){ return "deselected category " + d.key; })
  })
  .elasticX(true)
  .on('filtered', reload_timeline)
  .xAxis().ticks(4);

  dateCreatedChart
  .dimension(meetup.groups.created_dim)
  .group(meetup.groups.created_groups)
  .width(1000).height(100).margins({top: margin_timelines_top, right: 10, bottom: 30, left: margin_timelines_left})
  .round(d3.time.day.round)
  .filterPrinter(function (filters) {
    var filter = filters[0];
    return "" + formatDate(filter[0]) + " to " + formatDate(filter[1]);
  })
  .on('filtered', reload_timeline)
  .elasticY(true)
  .x(d3.time.scale()
  .domain([timeline_start, timeline_end])
  .rangeRound([0, 10 * 90]));

  
  listOfGroups.dimension(meetup.groups.id_dim)
  .group(function (d) { return meetup.groups.id_dim.top(Infinity).length + " selected groups"; })
  .size(max_no_of_groups_to_display_in_timeline_and_table)
  .columns([
    { 'label': 'Group Name',     'format': function(d)  { return '<a href="/group/'+d.id_group+'">' + d.name + '</a>'   } },
    { 'label': 'Group Created',  'format': function(d)  { return formatYearMonth( d.created )     } },
    { 'label': 'Rating',         'format': function(d)  { return d.rating                         } },
    { 'label': 'Join Mode',      'format': function(d)  { return d.join_mode                      } },
    { 'label': 'Biggest Event',  'format': function(d)  { return d.max_yes_at_one_event           } },
    { 'label': 'Total Rsvps',    'format': function(d)  { return d.no_member_who_ever_rsvpd_yes   } },
    { 'label': 'First Event',    'format': function(d)  { return formatDate( d.first_event_time ) } },
    { 'label': '# Events',       'format': function(d)  { return d.number_of_events               } },
    { 'label': 'Last Event',     'format': function(d)  { return formatDate( d.last_event_time  ) } }
  ])
  .sortBy(function (d){ return - d.no_member_who_ever_rsvpd_yes; });

  log("rendering all");
  dc.renderAll();
  $('#loading').hide();
  $('#evolution-year-chart svg').hide();
  // log("filtering from url");
  // url_to_status();

}
log("start loading data");
$('#loading').show();
queue()
.defer(d3.csv,   "/static/groups.csv")
.defer(d3.csv,   "/events/categories.csv")
.defer(d3.csv,   "/events/time.csv?id_group[]=176399")
.await(handle_csv);
