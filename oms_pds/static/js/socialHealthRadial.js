
window.handleTabChange = function (dimension, tabNum) {
	if (typeof android !== "undefined" && android.handleTabChange) {
		return android.handleTabChange(dimension, tabNum);
	}
	
	return true;
};

function select_circle(s){
    
    var categories = ["social","activity","focus"];

    for(var i = 0; i<categories.length; i++)
    {
        if(s == categories[i])
        {
            d3.selectAll("#"+categories[i]+"_circle")
                .attr("xlink:href", "/static/img/bbc_demo/"+categories[i]+"_circle_orange.png");
            d3.selectAll(".score div#"+categories[i])
                .style("color", "white");
            d3.selectAll(".score div#"+categories[i]+" div#user")
                .style("background-color", "#fffff");
        }
        else
        {
            d3.selectAll("#"+categories[i]+"_circle")
                .attr("xlink:href", "/static/img/bbc_demo/"+categories[i]+"_circle.png");
            d3.selectAll(".score div#"+categories[i])
                .style("color", "gray")
                .style("background-color", "#F5F5F5");
        }
    }
};

function update_scores(userData, averageData){
    // get averages from the high low data passed in, and store it locally.  This is a total hack for a demo.
    var averages = { "activity" : 0, "social" : 0, "focus" : 0 };
    for(var i = 0; i<averageData.length; i++)
    {
        averages[averageData[i].key] += averageData[i].value;
    }
    averages["activity"]=averages["activity"]/2;
    averages["focus"]=averages["focus"]/2;
    averages["social"]=averages["social"]/2;
    for(var i = 0; i<userData.length; i++)
    {
        d3.selectAll(".score div#"+userData[i].key+" div#user")
            .html(Math.round(userData[i].value));

        d3.selectAll(".score div#"+userData[i].key+" div#group")
            .html(Math.round(averages[userData[i].key]));
    }
}

function click(d){
    select_circle(d);
    if(d == "social")
    {
        d3.selectAll("#social")
            .style("background", "#ff9f37");
        d3.selectAll(".axis")
   	    .style("opacity", function(d,i) {
		if(i == 2)
		{return "1.0";} 
		else
		{return "0.0";}
       	});
    }
    else if(d == "activity")
    {
        d3.selectAll("#activity")
            .style("background", "#ff9f37");
        d3.selectAll(".axis")
   	    .style("opacity", function(d,i) {
		if(i == 0)
		{return "1.0";} 
		else
		{return "0.0";}
	});
    }
    else if(d == "focus")
    {
        d3.selectAll("#focus")
            .style("background", "#ff9f37");
        d3.selectAll(".axis")
   	    .style("opacity", function(d,i) {
		if(i == 1)
		{return "1.0";} 
		else
		{return "0.0";}
	});
    }
};

window.SocialHealthRadialView = Backbone.View.extend({
	el: "#triangle",
	
	initialize: function (height, width, chartElement, heightPadding, widthPadding, iconSize, iconFactor) {
		_.bindAll(this, "render");
		this.answerLists = new AnswerListCollection();
		this.height = height;
		this.width = width;
		this.heightPadding = heightPadding;
		this.widthPadding = widthPadding;
		this.chartElement = chartElement;
		this.iconFactor = iconFactor;
		this.iconSize = iconSize;
		this.answerLists.bind("reset", this.render);
		this.answerLists.fetch();
	},
	
	render: function () {
		if (this.graph) {
			this.graph.remove();
		}
	
 		//populate data variable with data from server	
		var data = this.answerLists.models[0].attributes["value"];
                
		// Note: we're subtracting an extra 48 from height to allow for the voting stars below it
//		var viewHeight = window.innerHeight - 48;
//		var width = window.innerWidth - 5,
		var viewHeight = this.height - 48;
		var width = this.width - 5,
		height = viewHeight - 200,
		maxRadius = Math.min(height, width) / 2 - 10;
		
		var z = d3.scale.category20();
		var whiteColor = d3.rgb(255,255,255);
		var redColor = d3.rgb(200,100,50);
		var newColor = d3.rgb(100,100,100);
//		var pink = d3.rgb(255,99,71);
		var pink = d3.rgb(255,204,0);
		var lightblue = d3.rgb(74,172,204);
		
		// Warning: the code below assumes that both average and user-specific sets are returned. If the user is not sharing, 
		// this will not be the case, and will need to be handled eventually.
		
		var averageData = _.filter(data, function (d) { return d.layer.indexOf("average") != -1; });
		var userData = _.filter(data, function (d) { return d.layer == "User";});
		console.log(userData);
                update_scores(userData, averageData);


		// Handle the fact that our data is in different layers (ie; "User", "AverageLow", "AverageHigh")		
		// nest - essentially a "group by": gets us a mapping from a layer to the associated objects with that layer 
		var nest = d3.nest()
			.key(function(d) { return d.layer; });
		
		// stack essentially just computes the inner radius for consecutive layers such as the average low and high layers we have
		var stack = d3.layout.stack()
			.offset("zero")//.offset(function(d) { return d.y0; })
			.values(function(layer) { return layer.values; })
			.x(function(d, i) { return d.key; })
			.y(function(d) { return d.value; });
		
		var layers = (averageData != null && averageData.length > 0)? stack(nest.entries(averageData)):[];
		
		// Now that we got the stacking out of the way, we know the inner and outer radius for the average layer
		// To simplify things (and optimize a bit), let's throw out the averageLow and replace it with the user data
		layers[0] = {key: "User", color: personalData[1].color_fill, values: userData };
//		layers[1] = {key: "User 2", values: userData };
		layers[2] = {key: "Sandy", color: "9ACD32", values: [{"key": "activity", "layer": "Sandy", "value": 4.643278996311979}, {"key": "social", "layer": "Sandy", "value": 6.257010307884192}, {"key": "focus", "layer": "Sandy", "value": 6.375039431346925}] };
		layers[3] = {key: "Todd", color: "FF0000", values: [{"key": "activity", "layer": "Todd", "value": 7.303142231732503}, {"key": "social", "layer": "Todd", "value": 5.81604961450666}, {"key": "focus", "layer": "Todd", "value": 4.134426320220927}] };
		layers[4] = {key: "Henrik", color: "9ACD32", values: [{"key": "activity", "layer": "Henrik", "value": 6.126601235157298}, {"key": "social", "layer": "Henrik", "value": 7.434995850439565}, {"key": "focus", "layer": "Henrik", "value": 8.005624549193879}] };
		layers[5] = {key: "Brian", color: "9ACD32", values: [{"key": "activity", "layer": "Brian", "value": 6.025471814621179}, {"key": "social", "layer": "Brian", "value": 6.272033444796837}, {"key": "focus", "layer": "Brian", "value": 7.330916878114618}] };
		layers[6] = {key: "Yves-Alexandre", color: "9ACD32", values: [{"key": "activity", "layer": "Yves-Alexandre", "value": 5.816343705284859}, {"key": "social", "layer": "Yves-Alexandre", "value": 4.767257149820975}, {"key": "focus", "layer": "Yves-Alexandre", "value": 8.693486957499326}] };
		layers[7] = {key: "Xeno", color: "9ACD32", values: [{"key": "activity", "layer": "Xeno", "value": 4.703211467391147}, {"key": "social", "layer": "Xeno", "value": 5.201585777356515}, {"key": "focus", "layer": "Xeno", "value": 6.459431618637298}] };
		
		//layers = layers.splice(1,1);

		// Since all layers have the same dimensions, using the first one to pull the dimension names is fine
		var dimensions = _.pluck(layers[0].values, "key");
		var angle = d3.scale.ordinal().domain(dimensions).range([0,120,240])
		var radius = d3.scale.linear().domain([0,10]).range([0, maxRadius]);
		
		var line = d3.svg.line.radial()
			.interpolate("cardinal-closed")
			.angle(function(d,i) { return angle(d.key) * (Math.PI / 180.0); })
			.radius(function(d) { return radius(d.value); });

		// Setting up the radial area graph used by both the user and group values
		var area = d3.svg.area.radial()
			.interpolate("cardinal-closed")
			.angle(function(d, i) { return angle(d.key) * (Math.PI / 180.0); })
			.innerRadius(function(d) { return radius((d.y0)? d.y0: 0); })
			.outerRadius(function(d) { return radius(d.value); });

		//var heightPadding = 200;
		//var widthPadding = -300;
		var heightPadding = this.heightPadding;
		var widthPadding = this.widthPadding;
		var chartCenter = [ ((width / 2) + widthPadding), ((height / 2) + heightPadding)];
		// Adjusted height is essentially the center plus the height of the graph below the center (lines at 30 degree angles = 0.5 height)
		var adjustedHeight = chartCenter[1] * 1.5 + heightPadding;

		var chartSvg = d3.select(this.chartElement).append("svg")
			.attr("width", width)
			.attr("height", adjustedHeight);
		
		this.graph = chartSvg;

		// Draw the legend first - putting it up top and off to the side allows us to make the chart iteself - important on smallers screens
		
		var arrayOfTypes = ["User","Average"];
		var legendOffset = 35;
		var legendMarginLeft = 20;
		
		// Plot the bullet circles...
		var legend = chartSvg.append("g").attr("id", "legend");
			
		legend.selectAll("circle")
			.data(arrayOfTypes).enter().append("svg:circle") // Append circle elements
			.attr("cx", legendMarginLeft)// barsWidthTotal + legendBulletOffset)
			.attr("cy", function(d, i) { return legendOffset + i*25; } )
			.attr("stroke-width", ".5")
			.style("fill", function(d, i) { 
				if (i == 0)
					return pink;
				else
					return lightblue 
			}) // Bar fill color
			.attr("r", 10);

		// Create hyper linked text at right that acts as label key...
		legend.selectAll("a.legend_link")
			.data(arrayOfTypes) // Instruct to bind dataSet to text elements
			.enter().append("svg:a") // Append legend elements
			.append("text")
			.attr("text-anchor", "left")
			.attr("x", legendMarginLeft+15)
			.attr("y", function(d, i) { return legendOffset + i*24 - 10; })
			.attr("dx", 5)
			.attr("dy", "1em") // Controls padding to place text above bars
			.text(function(d, i) { return arrayOfTypes[i];})
			.style("color","white");
		
		// Center the chart itself on the page
		chartSvg = chartSvg.append("g")
			.attr("transform", "translate("+chartCenter[0]+","+chartCenter[1]+")");

                // Draw the background triangle 
                var backgroundWidth=height/1.75;
                chartSvg.append('path')
                        .attr('d', function(d) { 
                             var x = 0, y = -height/1.5;
                             return 'M ' + x +' '+ y + ' l '+backgroundWidth+' '+height+' l -'+backgroundWidth*2+' 0 z';
                        })
                        .style("stroke","white")
                        .style("opacity","0.5")
                        .style("fill","white");
	
		// Draw the layers
		chartSvg.selectAll(".layer")
			.data(layers)
			.enter().append("path")
//			.attr("class", "layer")
                        .attr("class", function(d){ return "layer "+d.key;})
			.attr("d", function(d) { return area(d.values); })
			.style("fill",
		        function(d, i) { if(d.key =="averageHigh"){return lightblue;}else{return d.color;} })
			.style("display",
		        function(d, i) { if(d.key =="User"){return; }else if(d.key =="averageHigh"){return;}else{return "none";} })
			.style("opacity", 0.5);
			
                var backgroundWidth=height/3.5;
                // Draw the upper left background prism
                chartSvg.append('path')
                        .attr('d', function(d) { 
                             var x = 0, y = -height/1.5;
                             return 'M ' + x +' '+ y + ' l 0 '+height/1.5+' l -'+backgroundWidth*2+' '+height/3+' z';
                        }) .style("stroke","None")
                        .style("opacity","0.4")
                        .style("fill","white");
                
                // Draw the upper right background prism
                chartSvg.append('path')
                        .attr('d', function(d) { 
                             var x = 0, y = -height/1.5;
                             return 'M ' + x +' '+ y + ' l 0 '+height/1.5+' l '+backgroundWidth*2+' '+height/3+' z';
                        })
                        .style("stroke","None")
                        .style("opacity","0.2")
                        .style("fill","white");
	
                // Draw the lower background prism
                chartSvg.append('path')
                        .attr('d', function(d) { 
                             var x = 0, y = 0;
                             return 'M ' + x +' '+ y + ' l -'+backgroundWidth*2+' '+height/3+' l '+backgroundWidth*4+' 0 z';
                        })
                        .style("stroke","None")
                        .style("opacity","0.0")
                        .style("fill","white");

                var dataset = [ "activity", "focus", "social" ];

                var circles = chartSvg.selectAll("circle")
                 .data(dataset)
                 .enter();

		var x_coords = [-(this.iconSize/2), (2*backgroundWidth)*(this.iconFactor), -(backgroundWidth*2 + this.iconSize) * this.iconFactor];
		var y_coords = [-(height/1.5+this.iconSize)*this.iconFactor, backgroundWidth*1.125*this.iconFactor, backgroundWidth*1.125*this.iconFactor];

		// Create activity circle label
                circles.append("svg:image")
                         .attr("xlink:href", "/static/img/bbc_demo/activity_circle.png")
                         .attr("id", "activity_circle")
                         .attr("width", this.iconSize+"px")
                         .attr("height", this.iconSize+"px")
                         .attr("x",x_coords[dimensions.indexOf("activity")])
//                         .attr("y",-backgroundWidth*2.7)
                         .attr("y",y_coords[dimensions.indexOf("activity")])
			 .on("mouseover", function(d){ return click("activity");});
	
		// Create focus circle label
                circles.append("svg:image")
                         .attr("xlink:href", "/static/img/bbc_demo/focus_circle.png")
                         .attr("id", "focus_circle")
                         .attr("width", this.iconSize+"px")
                         .attr("height", this.iconSize+"px")
                         .attr("x",x_coords[dimensions.indexOf("focus")])
                         .attr("y",y_coords[dimensions.indexOf("focus")])
			 .on("mouseover", function(d){ return click("focus");});

		// Create social circle label
                circles.append("svg:image")
                         .attr("xlink:href", "/static/img/bbc_demo/social_circle.png")
                         .attr("id", "social_circle")
                         .attr("width", this.iconSize+"px")
                         .attr("height", this.iconSize+"px")
                         .attr("x",x_coords[dimensions.indexOf("social")])
                         .attr("y",y_coords[dimensions.indexOf("social")])
			 .on("mouseover", function(d){ return click("social");});
	
		// create Axis		
		chartSvg.selectAll(".axis")
			.data(dimensions) .enter().append("g") .attr("class", "axis")
 			.attr("transform", function(d, i) { return "rotate(" + angle(d) + ")"; })
			.on("click", function (d,i) { return handleTabChange(d,i); })
			.call(d3.svg.axis()
				.scale(radius.copy().range([-10, -maxRadius]))
				.ticks(5)
				.orient("left"))
//				.append("text")
//				.attr("y", -maxRadius - 10)
//				.attr("text-anchor", "middle")
//				.text(function(d) { return d; })
//				.attr("style","font-size:16px;")
//				.style("fill", function(d,i) {
//					return "black"; // Insert means of determining unhealthy value here
//				})
				;

	
	}

//close call to local .json file
//                });	
});
