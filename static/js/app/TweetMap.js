// Here's where we're calling the google maps API. No API key needed yet, b/c
// we're not using it very much. If we started using it enough that we wanted
// to track our usage, we should get an API key. More info:
// https://developers.google.com/maps/documentation/javascript/tutorial#api_key
//
// And that "async!" is from the async plugin.
// https://github.com/millermedeiros/requirejs-plugins
define(['maplabel'], function () {
    return function (canvas, dataPanel) {
        var latitude = 40.4417, // default pittsburgh downtown center
            longitude = -80.0000;
        var centerMarker;
        //var redDotImg = 'static/images/maps_measle_red.png';
        var queriedUsersMarkers = [];
        var mapOptions = {
            center: {lat: latitude, lng: longitude},
            zoom: 13,
            disableDefaultUI: true,
            zoomControl:true,
            styles:
              [
                {
                  "elementType": "labels",
                  "stylers": [
                    { "visibility": "off" }
                  ]
                },{
                  "featureType": "road",
                  "elementType": "geometry",
                  "stylers": [
                    { "visibility": "simplified" }
                  ]
                },{
                  "featureType": "poi",
                  "stylers": [
                    { "visibility": "off" }
                  ]
                },{
                  "featureType": "landscape",
                  "stylers": [
                    { "visibility": "off" }
                  ]
                }
              ]
        };
        var map = new google.maps.Map(canvas, mapOptions);

        var plotTweet = function (tweet) {
          if(tweet != null && tweet["coordinates"] != null &&
              tweet["coordinates"]["coordinates"] != null) {
            var lat = tweet["coordinates"]["coordinates"][1];
            var lon = tweet["coordinates"]["coordinates"][0];
            var emojis = tweet["emoji"]
            var emojisArray = emojis.split(',')
              var label = new MapLabel({
                text: emojisArray[0], //only prints 1st emoji
                position: new google.maps.LatLng(lat, lon),
                map: map,
                fontFamily: "helvetica",
                fontSize: 12,
                align: 'left'
              });

          }
        };

        var plotBinEmojis = function (dict){
            for (var key in dict) {
                if (dict.hasOwnProperty(key)){
                    var arr = JSON.parse(key);
                    var lat = arr[0];
                    var lon = arr[1];
                    var emoji = dict[key];
                    var label = new MapLabel({
                        text: emoji,
                        position: new google.maps.LatLng(lat,lon),
                        map:map,
                        fontFamily: "helvetica",
                        fontSize: 12,
                        align: 'left'
                    });
                }
            }  
        };

        var plotNghdEmojis = function(dict){
            for (var nghd_coords in dict){
                if (dict.hasOwnProperty(nghd_coords)){
                    var arr = JSON.parse(nghd_coords);
                    var lat = arr[0];
                    var lon = arr[1];
                    //var lat = nghd_coords[0]
                    //var lon = nghd_coords[1]
                    var emojiList = dict[nghd_coords];
                    var label = new MapLabel({
                        text: emojiList[0]+emojiList[1]+emojiList[2],
                        position: new google.maps.LatLng(lat,lon),
                        map:map,
                        fontFamily: "helvetica",
                        fontSize: 20,
                        align: 'left'
                    });
                    
                    var marker = new google.maps.Marker({
                        position: new google.maps.LatLng(lat,lon),
                        map:map,
                        title:"white",
                        //icon:'whiterectangle.png'
                    });

                    var infowindow = new google.maps.InfoWindow({
                        content:emojiList[4] 
                    });
                    google.maps.event.addDomListener(marker,'click',function(){
                        infowindow.open(map,marker);
                        console.log(emojiList[4]);
                    });
                
                }
            }
        };  

        var api =  {
            clearMap: function () {
                // remove previous markers from map and empty queriedUsersMarkers
                if(queriedUsersMarkers.length > 0) {
                    for(var i = 0; i < queriedUsersMarkers.length; i++) {
                        queriedUsersMarkers[i].setMap(null);
                    }
                    queriedUsersMarkers.length = 0;
                }
            },

            drawLine: function(lat0, lon0, lat1, lon1) {
                var line = drawLine(lat0, lon0, lat1, lon1);
                queriedUsersMarkers.push(line);
            },
            plotLabel: function(point, labelText) {
                var lat = point[0];
                var lon = point[1];
                var label = new MapLabel({
                    text: labelText,
                    position: new google.maps.LatLng(lat, lon),
                    map: map,
                    fontSize: 25,
                    align: 'left',
                });

              queriedUsersMarkers.push(label);
            },
            plotTweets: function(tweets) {
              for (var i = 0; i < tweets.length; i++) {
                plotTweet(tweets[i]);
              }
            },
            plotBinEmoji: function(emojis_per_bin){
                plotBinEmojis(emojis_per_bin);
            },
            plotNghdEmoji: function(emojis_per_nghd){
                plotNghdEmojis(emojis_per_nghd);
            },
        };
        return api;
    };
});
