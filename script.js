

// set the dimensions and margins of the graph
var margin = {top: 20, right: 20, bottom: 30, left: 50},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

// set the ranges
var x = d3.scaleTime().range([0, width]);
var y = d3.scaleLinear().range([height, 0]);

var plot = d3.select("#progress-to-goal").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  	.append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

d3.csv("https://raw.githubusercontent.com/GWarrenn/fancy-racehorse/master/results.csv", function(data){
    
	// converting date-time string to actual date-time object

	all_data = data

	var strictIsoParse = d3.utcParse("%Y-%m-%d %H:%M:%S%Z");

    data.forEach(function(d,i) {
		d.fmt_date = strictIsoParse(d.start_date);

		var formatDay = d3.timeFormat("%Y-%m-%d")

		d.day = formatDay(d.fmt_date)

		d.distance = +d.distance
		d.elapsed_time = +d.elapsed_time

	});

	yearly_summary = _(data)
				.groupBy('index')
				.map((index, id) => ({
					index: id,
					total_miles : _.sumBy(index, 'distance'),
					total_time : _.sumBy(index, 'elapsed_time'),
				}))
				.value()


	document.getElementById("total-miles").innerHTML = yearly_summary[0].total_miles;
	document.getElementById("total-time").innerHTML = yearly_summary[0].total_time;

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

	//line chart -- progress to goal! 	

	valueline = d3.line()
		.x(function(d) { return x(d.day); })
		.y(function(d) { return y(d.pct_to_goal); });

    var formatDay = d3.timeParse("%Y-%m-%d")

    end_point = formatDay("2019-12-31")
    start_point = formatDay("2019-01-01")

	x.domain([start_point,end_point]);
	y.domain([0,1]);

	plot.append("path")
		.data([daily_summary])
		.attr("class", "line")
		.attr("d", valueline);

	plot.append("g")
		.attr("transform", "translate(0," + height + ")")
		.call(d3.axisBottom(x));

	plot.append("g")
		.call(d3.axisLeft(y));

});

