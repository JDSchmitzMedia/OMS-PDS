var stockholm = new google.maps.LatLng(59.32522, 18.07002);
var parliament = new google.maps.LatLng(59.327383, 18.06747);
var marker;
//var pathmap;

function changedata(data, i){
    d3.selectAll("div#contacts div.contact div.username")
        .style("background-color", "white");
    i.style.backgroundColor = "rgb(0,0,0)";
//    redheatmap.toggle();
//    redheatmap.setDataSet(data);
//    x = redheatmap.getMap();
//    google.maps.event.addListenerOnce(x, "idle", function(){
//        redheatmap.toggle();
//    });
//    var newcenter = x.center
//    newcenter.kb += 0.0001;
//    x.setCenter(newcenter);
    return i;
}

function initialize() {
  var mapOptions = {
    zoom: 13,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    center: stockholm,
    zoom: 4,
    disableDefaultUI: false,
    scrollwheel: true,
    draggable: true,
    navigationControl: true,
    mapTypeControl: false,
    scaleControl: true,
    disableDoubleClickZoom: false
  };

//  pathmap = new google.maps.Map($("#pathmapArea")[0], mapOptions);

  marker = new google.maps.Marker({
    map:map,
    draggable:true,
    animation: google.maps.Animation.DROP,
    position: parliament
  });
  google.maps.event.addListener(marker, 'click', toggleBounce);
}

function toggleBounce() {

  if (marker.getAnimation() != null) {
    marker.setAnimation(null);
  } else {
    marker.setAnimation(google.maps.Animation.BOUNCE);
  }
}

google.maps.event.addDomListener(window, 'load', initialize);


