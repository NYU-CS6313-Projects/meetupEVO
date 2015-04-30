var nestByDate, formatMonth, formatDate;

function groupList(div) {
  console.log("groupList(div) got called");
  var groupsByDate = nestByDate.entries(date.top(40));

  div.each(function() {
    console.log("will display list of groups in");
    console.log(this);
    var date = d3.select(this).selectAll(".date")
    .data(groupsByDate, function(d) { return d.key; });

    date.enter().append("div")
    .attr("class", "date")
    .append("div")
    .attr("class", "month")
    .text(function(d) { return formatMonth(d.values[0].date); });

    date.exit().remove();

    var group = date.order().selectAll(".group")
    .data(function(d) { return d.values; }, function(d) { return d.index; });

    var groupEnter = group.enter().append("div").attr("class", "group");

    groupEnter.append("div")
    .attr("class", "name")
    .append("a")
    .attr("href", function(d){return "/group/" + d.id_group;}) 
    .text(function(d) { return d.name; });

    groupEnter.append("div")
    .attr("class", "rating")
    .text(function(d) { return d.rating; });

    groupEnter.append("div")
    .attr("class", "join_mode")
    .text(function(d) { return d.join_mode; });

    groupEnter.append("div")
    .attr("class", "no_members")
    .text(function(d) { return d.no_members; });

    groupEnter.append("div")
    .attr("class", "max_yes_at_one_event")
    .text(function(d) { return d.max_yes_at_one_event; });

    groupEnter.append("div")
    .attr("class", "no_member_who_ever_rsvpd_yes")
    .text(function(d) { return d.no_member_who_ever_rsvpd_yes; });

    groupEnter.append("div")
    .attr("class", "first_event_time")
    .text(function(d) { return formatDate(d.first_event_time) ; });

    groupEnter.append("div")
    .attr("class", "no_events")
    .text(function(d) { return d.number_of_events; });
    
    groupEnter.append("div")
    .attr("class", "last_event_time")
    .text(function(d) { return formatDate(d.last_event_time) ; });

    group.exit().remove();

    group.order();
  });
}

function barChart() {
  if (!barChart.id) barChart.id = 0;

  var margin = {top: 10, right: 10, bottom: 20, left: 10},
  x,
  y = d3.scale.linear().range([75, 0]),
  id = barChart.id++,
  axis = d3.svg.axis().orient("bottom"),
  brush = d3.svg.brush(),
  brushDirty,
  dimension,
  group,
  round;

  console.log("barchart() got called, id=" + barChart.id);
  function chart(div) {
    var width = x.range()[1],
    height = y.range()[0];

    y.domain([0, group.top(1)[0].value]);

    div.each(function() {
      var div = d3.select(this),
      g = div.select("g");

      // Create the skeletal chart.
      if (g.empty()) {
        div.select(".title").append("a")
        .attr("href", "javascript:reset(" + id + ")")
        .attr("class", "reset")
        .text("reset")
        .style("display", "none");

        g = div.append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        g.append("clipPath")
        .attr("id", "clip-" + id)
        .append("rect")
        .attr("width", width)
        .attr("height", height);

        g.selectAll(".bar")
        .data(["background", "foreground"])
        .enter().append("path")
        .attr("class", function(d) { return d + " bar"; })
        .datum(group.all());

        g.selectAll(".foreground.bar")
        .attr("clip-path", "url(#clip-" + id + ")");

        g.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + height + ")")
        .call(axis);

        // Initialize the brush component with pretty resize handles.
        var gBrush = g.append("g").attr("class", "brush").call(brush);
        gBrush.selectAll("rect").attr("height", height);
        gBrush.selectAll(".resize").append("path").attr("d", resizePath);
      }

      // Only redraw the brush if set externally.
      if (brushDirty) {
        brushDirty = false;
        g.selectAll(".brush").call(brush);
        div.select(".title a").style("display", brush.empty() ? "none" : null);
        if (brush.empty()) {
          g.selectAll("#clip-" + id + " rect")
          .attr("x", 0)
          .attr("width", width);
          } else {
          var extent = brush.extent();
          g.selectAll("#clip-" + id + " rect")
          .attr("x", x(extent[0]))
          .attr("width", x(extent[1]) - x(extent[0]));
        }
      }

      g.selectAll(".bar").attr("d", barPath);
    });

    function barPath(groups) {
      var path = [],
      i = -1,
      n = groups.length,
      d;
      while (++i < n) {
        d = groups[i];
        path.push("M", x(d.key), ",", height, "V", y(d.value), "h9V", height);
      }
      return path.join("");
    }

    function resizePath(d) {
      var e = +(d == "e"),
      x = e ? 1 : -1,
      y = height / 3;
      return "M" + (.5 * x) + "," + y
      + "A6,6 0 0 " + e + " " + (6.5 * x) + "," + (y + 6)
      + "V" + (2 * y - 6)
      + "A6,6 0 0 " + e + " " + (.5 * x) + "," + (2 * y)
      + "Z"
      + "M" + (2.5 * x) + "," + (y + 8)
      + "V" + (2 * y - 8)
      + "M" + (4.5 * x) + "," + (y + 8)
      + "V" + (2 * y - 8);
    }
  }

  brush.on("brushstart.chart", function() {
    var div = d3.select(this.parentNode.parentNode.parentNode);
    div.select(".title a").style("display", null);
  });

  brush.on("brush.chart", function() {
    var g = d3.select(this.parentNode),
    extent = brush.extent();
    if (round) g.select(".brush")
    .call(brush.extent(extent = extent.map(round)))
    .selectAll(".resize")
    .style("display", null);
    g.select("#clip-" + id + " rect")
    .attr("x", x(extent[0]))
    .attr("width", x(extent[1]) - x(extent[0]));
    dimension.filterRange(extent);
  });

  brush.on("brushend.chart", function() {
    if (brush.empty()) {
      var div = d3.select(this.parentNode.parentNode.parentNode);
      div.select(".title a").style("display", "none");
      div.select("#clip-" + id + " rect").attr("x", null).attr("width", "100%");
      dimension.filterAll();
    }
  });

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin = _;
    return chart;
  };

  chart.x = function(_) {
    if (!arguments.length) return x;
    x = _;
    axis.scale(x);
    brush.x(x);
    return chart;
  };

  chart.y = function(_) {
    if (!arguments.length) return y;
    y = _;
    return chart;
  };

  chart.dimension = function(_) {
    if (!arguments.length) return dimension;
    dimension = _;
    return chart;
  };

  chart.filter = function(_) {
    if (_) {
      brush.extent(_);
      dimension.filterRange(_);
      } else {
      brush.clear();
      dimension.filterAll();
    }
    brushDirty = true;
    return chart;
  };

  chart.group = function(_) {
    if (!arguments.length) return group;
    group = _;
    return chart;
  };

  chart.round = function(_) {
    if (!arguments.length) return round;
    round = _;
    return chart;
  };

  return d3.rebind(chart, brush, "on");
}

function evolutionChart() {
  if (!evolutionChart.id) evolutionChart.id = 0;


  var margin = {top: 10, right: 10, bottom: 20, left: 10},
  x,
  y = d3.scale.linear().range([75, 0]),
  id = evolutionChart.id++,
  axis = d3.svg.axis().orient("bottom"),
  brush = d3.svg.brush(),
  brushDirty,
  round;

  console.log("evolutionChart() got called, id=" + evolutionChart.id);
  function chart(div) {
    console.log("evolutionChart() is now charted on " + div);
    var width = x.range()[1],
    height = 400; //  y.range()[0];

    y.domain([0, 200]); //  group.top(1)[0].value]);

    div.each(function(f,i) {
      console.log("iterating over all charts, now at i=" + i + ", which has id=" + this.id);
      var div = d3.select(this),
      g = div.select("g");

      // Create the skeletal chart.
      if (g.empty()) {
        div.select(".title").append("a")
        .attr("href", "javascript:evolutionChartReset(" + evolutionChart.id + ")")
        .attr("class", "reset")
        .text("reset")
        .style("display", "none");

        g = div.append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        g.append("clipPath")
        .attr("id", "clip-" + id)
        .append("rect")
        .attr("width", width)
        .attr("height", height);

        lines = g.append("g")
        .attr("class", "lines");


        // Creating a function that will nest our ID groups into; so our json file is clustered by group instead
        // of having just a list of all the information.
        var dataGroup = d3.nest()
            .key(function(d) {
                return d.id_group;
            })
            .entries(datum);

//                var color = function(d, j) {
//                            return "hsl(" + Math.random() * 360 + ",70%,50%)";
//                        }
        // Creating a path function that will load in years as the x values and rsvps as y values. 
        // This will allows the tool to know where to connect the lines
        // The interpolate function allows for curved lines
        var theLine = d3.svg.line()
            .x(function (d, i) {
                return x(d.time_bin);
            })
            .y(function (d) {
                return y(d.sum);
            })
//                    .interpolate("basis"); 
        
        // Creating a function that moves the selected line to the front
        d3.selection.prototype.moveToFront = function() { 
            return this.each(function() { 
                this.parentNode.appendChild(this); 
                }); 
            };

        // Creating the graph
        // Creating a colouring function
        // This function allows us to create random colours for each different group ID
        dataGroup.forEach(function(d, i) {
            lines.append('svg:path')
                .attr('d', theLine(d.values))
//                        .attr('stroke', function(d, j) {
//                            return "hsl(" + Math.random() * 360 + ",70%,50%)";
//                        })
                .attr ('stroke', '#0000FF')
                .attr('stroke-width', 2)
                .attr('opacity', 0.35)
                .attr('fill', 'none')
                .on('mouseover', function(d){
                    d3.select(this)
                    .style('stroke-width', '6px')
                    .attr('opacity', 1)
                    .moveToFront();
            })
                .on('mouseout', function(d){
                    d3.select(this)
                    .style('stroke-width', '2px')
                    .attr('opacity', 0.35)
                    .transition()
                    .duration(750);
            });
        });

        g.append("g")
        .attr("class", "axis")
        .attr("transform", "translate(0," + height + ")")
        .call(axis);

        // Initialize the brush component with pretty resize handles.
        var gBrush = g.append("g").attr("class", "brush").call(brush);
        gBrush.selectAll("rect").attr("height", height);
        gBrush.selectAll(".resize").append("path").attr("d", resizePath);
      }

      // Only redraw the brush if set externally.
      /*
      if (brushDirty) {
        brushDirty = false;
        g.selectAll(".brush").call(brush);
        div.select(".title a").style("display", brush.empty() ? "none" : null);
        if (brush.empty()) {
          g.selectAll("#clip-" + id + " rect")
          .attr("x", 0)
          .attr("width", width);
          } else {
          var extent = brush.extent();
          g.selectAll("#clip-" + id + " rect")
          .attr("x", x(extent[0]))
          .attr("width", x(extent[1]) - x(extent[0]));
        }
      }
      */

      // g.selectAll(".bar").attr("d", barPath);
    });
/*
    function barPath(groups) {
      var path = [],
      i = -1,
      n = groups.length,
      d;
      while (++i < n) {
        d = groups[i];
        path.push("M", x(d.key), ",", height, "V", y(d.value), "h9V", height);
      }
      return path.join("");
    }
*/
    function resizePath(d) {
      var e = +(d == "e"),
      x = e ? 1 : -1,
      y = height / 3;
      return "M" + (.5 * x) + "," + y
      + "A6,6 0 0 " + e + " " + (6.5 * x) + "," + (y + 6)
      + "V" + (2 * y - 6)
      + "A6,6 0 0 " + e + " " + (.5 * x) + "," + (2 * y)
      + "Z"
      + "M" + (2.5 * x) + "," + (y + 8)
      + "V" + (2 * y - 8)
      + "M" + (4.5 * x) + "," + (y + 8)
      + "V" + (2 * y - 8);
    }
  }
/*
  brush.on("brushstart.chart", function() {
    var div = d3.select(this.parentNode.parentNode.parentNode);
    div.select(".title a").style("display", null);
  });

  brush.on("brush.chart", function() {
    var g = d3.select(this.parentNode),
    extent = brush.extent();
    if (round) g.select(".brush")
    .call(brush.extent(extent = extent.map(round)))
    .selectAll(".resize")
    .style("display", null);
    g.select("#clip-" + id + " rect")
    .attr("x", x(extent[0]))
    .attr("width", x(extent[1]) - x(extent[0]));
    dimension.filterRange(extent);
  });

  brush.on("brushend.chart", function() {
    if (brush.empty()) {
      var div = d3.select(this.parentNode.parentNode.parentNode);
      div.select(".title a").style("display", "none");
      div.select("#clip-" + id + " rect").attr("x", null).attr("width", "100%");
      dimension.filterAll();
    }
  });
*/
  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin = _;
    return chart;
  };

  chart.x = function(_) {
    if (!arguments.length) return x;
    x = _;
    axis.scale(x);
    brush.x(x);
    return chart;
  };

  chart.y = function(_) {
    if (!arguments.length) return y;
    y = _;
    return chart;
  };

  chart.datum = function(_) {
    if (!arguments.length) return datum;
    console.log("setting datum to " + _);
    datum = _;
    return chart;
  };

  chart.filter = function(_) {
    if (_) {
      brush.extent(_);
      dimension.filterRange(_);
      } else {
      brush.clear();
      dimension.filterAll();
    }
    brushDirty = true;
    return chart;
  };

  chart.group = function(_) {
    if (!arguments.length) return group;
    group = _;
    return chart;
  };

  chart.round = function(_) {
    if (!arguments.length) return round;
    round = _;
    return chart;
  };

  return d3.rebind(chart, brush, "on");
}

