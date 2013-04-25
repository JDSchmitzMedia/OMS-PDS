var redheatmap;
var map;
var personalData;
var groupData;
var ismarkerdropped = false;
function changedata(data, i){
    d3.selectAll("div#contacts div.contact div.username")
        .style("background-color", "white");
    i.style.backgroundColor = "rgb(216,216,216)";
    redheatmap.toggle();
    redheatmap.setDataSet(data);
    x = redheatmap.getMap();
    google.maps.event.addListenerOnce(x, "idle", function(){
        redheatmap.toggle();
    });
    var newcenter = x.center
    newcenter.kb += 0.0001;
    x.setCenter(newcenter);
    return i;
}

function toggleBounce() {
  swap('#radial_chart');
//  if (marker.getAnimation() != null) {
//    marker.setAnimation(null);
//  } else {
//    marker.setAnimation(google.maps.Animation.BOUNCE);
//  }
}

function markCurrentLocation(){
  if(!ismarkerdropped)
  {
    var mycurrentlocation = new google.maps.LatLng(42.5363, -71.044);
    var markerArray = [
      new google.maps.LatLng(personalData[1].locations[0].lat, personalData[1].locations[0].lng),
      new google.maps.LatLng(personalData[1].locations[1].lat, personalData[1].locations[1].lng),
      new google.maps.LatLng(personalData[1].locations[2].lat, personalData[1].locations[2].lng),
      new google.maps.LatLng(personalData[1].locations[3].lat, personalData[1].locations[3].lng),
      new google.maps.LatLng(personalData[1].locations[4].lat, personalData[1].locations[4].lng)
    ];
    var flightPath = new google.maps.Polyline({
      path: markerArray,
      strokeColor: "#FF0000",
      strokeOpacity: 0.5,
      strokeWeight: 7 
    });

    flightPath.setMap(redheatmap.getMap());
    
    var mymap = redheatmap.getMap();
    var iterator = 0;

    for (var i =0; i < markerArray.length; i++) {
      setTimeout(function() {
        addMarker();
      }, i * 600);
    }
    ismarkerdropped = true;
  }

  function addMarker(){
    marker = new google.maps.Marker({
      map:mymap,
      draggable:false,
      animation: google.maps.Animation.DROP,
      position: markerArray[iterator] 
    });
    google.maps.event.addListener(marker, 'click', toggleBounce);
    iterator++;
  }

}


window.onload = function(){
    // standard gmaps initialization
    var myLatlng = new google.maps.LatLng(35.5363, -41.044);
    // define map properties
    var myOptions = {
      zoom: 4,
      center: myLatlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      disableDefaultUI: false,
      scrollwheel: true,
      draggable: true,
      navigationControl: true,
      mapTypeControl: false,
      scaleControl: true,
      disableDoubleClickZoom: false
    };
    // we'll use the heatmapArea 
    var map = new google.maps.Map($("#heatmapArea")[0], myOptions);
    
    // let's create a heatmap-overlay
    // with heatmap config properties

    //simple file read from current directory
    var heatmapData = [];
    d3.json("/static/data/users.json", function(data) {
        console.log("reading json data");
        console.log(data);
        personalData = data;

        //populate user column from static data file
        //d3.selectAll("div.username div")
        //    .html(data.user);
        // important: a datapoint now contains lat, lng and count property!
        var testData={
                max: 3,
                data: personalData[0].locations
        };
        d3.select("div#contacts").selectAll("div")
            .data(data).enter().append("div")
                .attr("class","contact")
                .html(function(d) { 
			return "<div class='contact-triangle "+d.color+"'></div><div class='contact-icon'><img style='width:80px;height:70px;' src='"+d.photo+"'></div>"
		})
//                .on("click", function(d) { alert(d.user); testData.data= d.locations; redheatmap.setDataSet(testData);})// Append div elements
                .append("div")
                    .attr("class","username")
                    .text(function(d) { return d.user; })
                    .on("click", function(d){
                                                if(d.issharing == false)
                                                {
                                                  alert("this user is not sharing");
                                                }
                                                else
                                                {

						  //handle GPS: This is where we show the selected contact's heatmap, and filter by time window(from select box in upper right).
//                                                  testData.data=d.locations;
						  var newLocations = [];
						  var earliest = 0;
						  var latest = 999999999999999999;
						  var early_datestring = $('#start_time').val();
						  var early_date = new Date(early_datestring);
						  earliest =isNaN(early_date.getTime())?earliest:early_date.getTime();
						  var late_datestring = $('#end_time').val();
						  var late_date = new Date(late_datestring);
						  latest =isNaN(late_date.getTime())?latest:late_date.getTime();

						  for(var i=0;i<d.locations.length;i++)
						  {
						    if((d.locations[i].timestamp >= earliest)&&(d.locations[i].timestamp <= latest))
						    {
						      newLocations.push(d.locations[i]);  
					            } 
						  }
						  testData.data = newLocations;
                                                  changedata(testData,this);
						  $("path.layer").hide();
						  if(d.user == personalData[1].user)
						  {
						    $("#User").show();
						  }
						  else
						  {
						    $("#"+d.user).show();
						  }
						  $("#averageHigh").show();
						  
                                                  
                                                }
                                            });// Append div elements
//                    .on("click", function(d) { alert(d.user); testData.data= d.locations; redheatmap.setDataSet(testData);}); // Append div elements
        heatmapData = data[0].locations;

        // now we can set the data
        google.maps.event.addListenerOnce(map, "idle", function(){
            // this is important, because if you set the data set too early, the latlng/pixel projection doesn't work
            
           // heatmap.setDataSet(testData);
           if( $("#heatmapArea")[0].style.display == "none")
           {
               console.log("heatmap invisible");
           }
           else
           {
               redheatmap.setDataSet(testData);
               //greenheatmap.setDataSet(greentestData);
               //yellowheatmap.setDataSet(yellowtestData);
           }
        });
    });


    redheatmap = new HeatmapOverlay(map, {
        "radius":20,
        "visible":true, 
        "opacity":60
//        "gradient": { 1.0: "rgb(255,0,0)", 0.0: "rgb(240,248,255)" }
    });
    var greenheatmap = new HeatmapOverlay(map, {
        "radius":20,
        "visible":true, 
        "opacity":60
//        "gradient": { 1.0: "rgb(0,128,0)", 0.0: "rgb(240,248,255)" }
    });
    var yellowheatmap = new HeatmapOverlay(map, {
        "radius":20,
        "visible":true, 
        "opacity":60
//        "gradient": { 0.0: "rgb(0,255,0)", 1.0: "rgb(255,255,0)" }
    });
 
    // here is our dataset

    var redtestData={
            max: 2,
            data: [{lat: 42.5363, lng:-70.044, count: 1},{lat: 42.5608, lng:-70.24, count: 1},{lat: 42, lng:-70, count: 1},{lat: 42.9358, lng:-70.1621, count: 1}]
    };

    var greentestData={
            max: 2,
            data: [{lat: 42.5363, lng:-71.044, count: 1},{lat: 42.5608, lng:-71.24, count: 1},{lat: 42, lng:-71, count: 1},{lat: 42.9358, lng:-71.1621, count: 1}]
    };

    var yellowtestData={
            max: 2,
            data: [{lat: 40.5363, lng:-71.044, count: 1},{lat: 40.5608, lng:-71.24, count: 1},{lat: 40, lng:-71, count: 1},{lat: 40.9358, lng:-71.1621, count: 1}]
    };
 

};
