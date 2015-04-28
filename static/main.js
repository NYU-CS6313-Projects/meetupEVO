  var margin = {top: 10, right: 0, bottom: 10, left: 10}
  , available_width = parseInt(d3.select('div#panel2').style('width'), 10)
  , width_timeseries = available_width - margin.left - margin.right

  var padding = 50;
  var height_timeseries = 450;
    var svg2 = d3.select("div#panel2").append("svg").attr("width", width_timeseries).attr("height", height_timeseries);
    var color = 'steelblue';
    // Load the line.json file
    function handle_new_json_data(error, data) {
        if(error) {
            return console.warn(error);
        }

        // Calculate the extents of the data (i.e. min and max)
        // extents along the horizontal line
        var extentX = d3.extent(data['data'], function(d) {
            return parseFloat(d.year);
        })
        
        // extents along the vertica line
        var extentY = d3.extent(data['data'], function(d) {
            return parseInt(d.sum);
        })
        
        // Creating the main SVG

        // Creating the Scales
        // x scale
        var xStretch = width_timeseries - 40;
        var x = d3.scale.linear().domain(extentX).range([padding,xStretch]);
        
        // Inverted y scale
        var yStretch = height_timeseries - 30;
        var y = d3.scale.linear().domain(extentY).range([yStretch,20]);

        
        // Creating and draw the axis
        // xAxis variable
        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .tickFormat(d3.format("d"));
        
        // yAxis variable
        var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");
        
        
        // Putting the axeses into the diagram by calling the variable up there (xAxis and yAxis)
        // Drawing the x-axis
        svg2.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(0," + (yStretch) + ")")
//                    .attr("transform", "translate(0," + (yStretch + padding) + ")")
            .call(xAxis);
        
        // Drawing the y-axis
        svg2.append("g")
            .attr("class", "axis")
            .attr("transform", "translate(" + padding + ",0)")
            .call(yAxis);
        
        // Labelling x-axis
        svg2.append("text")
            .attr("class", "label")
            .attr("text-anchor", "end")
            .attr("x", xStretch)
            .attr("y", yStretch + 100)
            .attr("y", yStretch + 50)
            .text("Year");
        
        // Labelling the y-axis
        svg2.append("text")
            .attr("class", "label")
            .attr("text-anchor", "end")
            .attr("y", padding+10)
            .attr("x", -padding)
            .attr("dy", ".75em")
            .attr("transform", "rotate(-90)")
            .text("Sum of RSVPs");
        
        // Creating a function that will nest our ID groups into; so our json file is clustered by group instead
        // of having just a list of all the information.
        var dataGroup = d3.nest()
            .key(function(d) {
                return d.id_group;
            })
            .entries(data['data']);
        
//                var color = function(d, j) {
//                            return "hsl(" + Math.random() * 360 + ",70%,50%)";
//                        }
        // Creating a path function that will load in years as the x values and rsvps as y values. 
        // This will allows the tool to know where to connect the lines
        // The interpolate function allows for curved lines
        var theLine = d3.svg.line()
            .x(function (d, i) {
                return x(d.year);
            })
            .y(function (d) {
                return y(d.sum);
            })
            .interpolate("basis"); 
        
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
            svg2.append('svg:path')
                .attr('d', theLine(d.values))
//                        .attr('stroke', function(d, j) {
//                            return "hsl(" + Math.random() * 360 + ",70%,50%)";
//                        })
                .attr ('stroke', color)
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
        
    }

    d3.json('/events/group_evolution_timeseries.json', handle_new_json_data);

    $('.category_button').click(function() {
        if ($(this).is(':checked')) {
            svg2.selectAll("*").remove();
            console.log("make a new query looking for category " + this.id);
            color = this.name;  
            d3.json('/events/group_evolution_timeseries.json?category=' + this.id, handle_new_json_data);
        } else {
            color = 'steelblue';  
            svg2.selectAll("*").remove();
            d3.json('/events/group_evolution_timeseries.json', handle_new_json_data);
        }
});


