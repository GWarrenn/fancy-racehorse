

// set the dimensions and margins of the graph
var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 500 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

// set the ranges
var x = d3.scaleTime().range([0, width]);
var y = d3.scaleLinear().range([height, 0]);

var progress_plot = d3.select("#progress-to-goal").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  	.append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

var formatPercent = d3.format(".0%")

// set the ranges
var x_scatter = d3.scaleLinear().range([0,width]);
var y_scatter = d3.scaleLinear().range([height, 0]);

var speed_distance_plot = d3.select("#speed-distance").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom + 20)
  	.append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");     

var color = d3.scaleOrdinal() // D3 Version 4
  .domain(["True", "False"])
  .range(["#64dbcb", "#2e4744"]);

d3.csv("https://raw.githubusercontent.com/GWarrenn/fancy-racehorse/master/results.csv", function(data){
    
	// converting date-time string to actual date-time object

	all_data = data

	document.getElementById("time-stamp").innerHTML = 'Progress as of: ' + data[0].date_pulled ;

	var strictIsoParse = d3.utcParse("%Y-%m-%d %H:%M:%S%Z");

    data.forEach(function(d,i) {
		d.fmt_date = strictIsoParse(d.start_date);

		var formatDay = d3.timeFormat("%Y-%m-%d")

		d.day = formatDay(d.fmt_date)

		d.distance = +d.distance
		d.moving_time = +d.moving_time
		d.average_speed = +d.average_speed
		d.total_elevation_gain = +d.total_elevation_gain 

	});

	yearly_summary = _(data)
				.groupBy('index')
				.map((index, id) => ({
					index: id,
					total_miles : _.sumBy(index, 'distance'),
					total_time : _.sumBy(index, 'moving_time'),
					total_elevation : _.sumBy(index, 'total_elevation_gain'),
				}))
				.value()

	var formatter = new Intl.NumberFormat('en-US', {
  		minimumFractionDigits: 0,
	});			

	miles = formatter.format(Math.round(yearly_summary[0].total_miles))

	document.getElementById("total-miles").innerHTML = miles ;

	function secondsToHms(d) {
	    d = Number(d);
	    var h = Math.floor(d / 3600);
	    var m = Math.floor(d % 3600 / 60);
	    var s = Math.floor(d % 3600 % 60);

	    var hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
	    var mDisplay = m > 0 ? m + (m == 1 ? " minute, " : " minutes, ") : "";
	    var sDisplay = s > 0 ? s + (s == 1 ? " second" : " seconds") : "";
	    return hDisplay + mDisplay + sDisplay; 
	}

	time = secondsToHms(yearly_summary[0].total_time)

	document.getElementById("total-time").innerHTML = time;

	elevation = formatter.format(Math.round(yearly_summary[0].total_elevation))

	document.getElementById("total-elevation").innerHTML = elevation;	

	daily_summary = _(data)
				.groupBy('day')
				.map((day, id) => ({
					day: id,
					total_miles : _.sumBy(day, 'distance'),
					total_time : _.sumBy(day, 'elapsed_time'),
				}))
				.value()	

	//now create running mileage sum

	previous_day = 0

    daily_summary.forEach(function(d,i) {
    	d.running_sum = daily_summary.reduce(function(prevVal, elem) {
		    return previous_day + d.total_miles;
		    
		}, 0);
	
		previous_day = d.running_sum

		d.pct_to_goal = d.running_sum / 2000

		var formatDay = d3.timeParse("%Y-%m-%d")
		d.day = formatDay(d.day)	

	});

	monthly_goals = [{day:'2019-01-01',pct_to_goal:0.00},{day:'2019-02-01',pct_to_goal:0.0833},{day:'2019-03-01',pct_to_goal:0.1667},
					{day:'2019-04-01',pct_to_goal:0.25},{day:'2019-05-01',pct_to_goal:0.333},{day:'2019-06-01',pct_to_goal:0.4167},
					{day:'2019-07-01',pct_to_goal:0.5},{day:'2019-08-01',pct_to_goal:0.5833},{day:'2019-09-01',pct_to_goal:0.6667},
					{day:'2019-10-01',pct_to_goal:0.75},{day:'2019-11-01',pct_to_goal:0.833},{day:'2019-12-01',pct_to_goal:0.91667},
					{day:'2019-12-31',pct_to_goal:1}]

	monthly_goals.forEach(function(d,i) {

		var formatDay = d3.timeParse("%Y-%m-%d")
		d.day = formatDay(d.day)	
	
	});				

	//line chart -- progress to goal! 	

	valueline = d3.line()
		.x(function(d) { return x(d.day); })
		.y(function(d) { return y(d.pct_to_goal); });

    var formatDay = d3.timeParse("%Y-%m-%d")

    end_point = formatDay("2019-12-31")
    start_point = formatDay("2019-01-01")

	x.domain([start_point,end_point]);
	y.domain([0,1]);

	progress_plot.append("path")
		.data([daily_summary])
		.attr("class", "line")
		.attr("d", valueline);

	progress_plot.append("path")
		.data([monthly_goals])
		.attr("class", "progress-line")
		.attr("d", valueline);	

	progress_plot.append("g")
		.attr("transform", "translate(0," + height + ")")
		.call(d3.axisBottom(x).tickFormat(d3.timeFormat("%b")));

	progress_plot.append("g")
		.call(d3.axisLeft(y).tickFormat(formatPercent));

	// text label for the y axis
  	progress_plot.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x",0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font", "12px arial")
      .text("Percentage to 2000 miles"); 

	var focus = progress_plot.append("g")
        .attr("class", "focus")
        .style("display", "none");

    focus.append("line")
        .attr("class", "x-hover-line hover-line")
        .attr("y1", 0)
        .attr("y2", height);

    focus.append("line")
        .attr("class", "y-hover-line hover-line")
        .attr("x1", width)
        .attr("x2", width);

    focus.append("circle")
        .attr("r", 3);

    focus.append("text")
        .attr("x", 15)
      	.attr("dy", ".31em");

    var bisectDate = d3.bisector(function(d) { return d.day; }).left;  	

    progress_plot
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .attr("class", "overlay")
        .attr("width", width)
        .attr("height", height)
        .on("mouseover", function() { focus.style("display", null); })
        .on("mouseout", function() { focus.style("display", "none"); })
        .on("mousemove", mousemove);

    function mousemove() {
      var x0 = x.invert(d3.mouse(this)[0]),
          i = bisectDate(daily_summary, x0, 1),
          d0 = daily_summary[i - 1],
          d1 = daily_summary[i],
          d = x0 - d0.day > d1.day - x0 ? d1 : d0;
      focus.attr("transform", "translate(" + x(d.day) + "," + y(d.pct_to_goal) + ")");
      focus.select("text").text(function() { return Math.round(d.pct_to_goal * 100) + "% towards goal (" + Math.round(d.running_sum) + " miles)"; });
      focus.style("font", "10px arial")      
      focus.select(".x-hover-line").attr("y2", height - y(d.pct_to_goal));
      focus.select(".y-hover-line").attr("x2", width + width);
    }

	// distance/speed scatter

	x_scatter.domain(d3.extent(data, function(d) { return d.distance; })).nice();
	y_scatter.domain(d3.extent(data, function(d) { return d.average_speed; })).nice();

	speed_distance_plot.selectAll(".dot")
	  .data(data)
	.enter().append("circle")
	  .attr("class", "dot")
	  .attr("stroke","black")
	  .attr("opacity",.7)
	  .attr("r", 3.5)
	  .attr("cx", function(d) { return x_scatter(d.distance); })
	  .attr("cy", function(d) { return y_scatter(d.average_speed); })
	  .style("fill", function(d) { return color(d.commute); });		

	speed_distance_plot.append("g")
		.attr("transform", "translate(0," + height + ")")
		.call(d3.axisBottom(x_scatter));

  	// text label for the x axis
  	speed_distance_plot.append("text")             
      .attr("transform",
            "translate(" + (width/2) + " ," + 
                           (height + margin.top + 10) + ")")
      .style("text-anchor", "middle")
      .style("font", "12px arial")      
      .text("Distance (miles)");

	speed_distance_plot.append("g")
		.call(d3.axisLeft(y_scatter));	  

  	// text label for the y axis
  	speed_distance_plot.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x",0 - (height / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font", "12px arial")      
      .text("Average Speed (mph)");     		

});

