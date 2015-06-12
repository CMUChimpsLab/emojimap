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
        var markers = [];
        var infowindows = [];
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

        var createEmojiMarker = function(pos,nghd,displayString,first,second,third){
            var marker = new MarkerWithLabel({
                position: pos,
                map: map,
                title: nghd,
                icon:'http://maps.gstatic.com/mapfiles/transparent.png', 
                    //only label is showing 
                labelContent: displayString,
                labelAnchor: new google.maps.Point(25,0)
            });
            var infobubble = new InfoBubble({
                maxWidth:600,
                maxHeight:300
            });
            infobubble.addTab('first', first);
            infobubble.addTab('second', second);
            infobubble.addTab('third', third);
            google.maps.event.addListener(marker,'click',function(){
                infobubble.open(map,marker);
            });
            infowindows.push(infobubble);
            return marker;
        };

        var plotNghdEmojis = function(dict){
            for (var nghd_info in dict){
                if (dict.hasOwnProperty(nghd_info)){
                    var coords = JSON.parse(nghd_info);
                    var lat = coords[0];
                    var lon = coords[1];
                    var emojiData = dict[nghd_info]; 
                      //[nghd,1st,1st tweets,2nd,2nd tweets,3rd,3rd tweets]
                    var nghd = emojiData[0];
                    var first_string = "";
                    for (var index in emojiData[2]){
                        first_string = first_string.concat("<br>",emojiData[2][index]);
                    }
                    var second_string = "";
                    for (var index in emojiData[4]){
                        second_string = second_string.concat("<br>",emojiData[4][index]);
                    }
                    var third_string = "";
                    for (var index in emojiData[6]){
                        third_string = third_string.concat("<br>",emojiData[6][index]);
                    }
                    var marker = createEmojiMarker(new google.maps.LatLng(lat,lon), nghd,
                                             emojiData[1]+emojiData[3]+emojiData[5],
                                             first_string,second_string,third_string);
                    markers.push(marker);
                }
            }
        };  
        
        var createWordMarker = function(pos,nghd,displayString,infoString){
            var marker = new MarkerWithLabel({
                position: pos,
                map: map,
                title: nghd,
                icon:'http://maps.gstatic.com/mapfiles/transparent.png', 
                    //only label is showing 
                labelContent: displayString,
                labelAnchor: new google.maps.Point(25,0)
            });
            var infowindow = new google.maps.InfoWindow({
                content: infoString 
            });
            google.maps.event.addListener(marker,'click',function(){
                infowindow.open(map,marker);
            });
            infowindows.push(infowindow);
            return marker;
        };

        var plotNghdWords = function(dict){
            for (var nghd_info in dict){
                if (dict.hasOwnProperty(nghd_info)){
                    var coords = JSON.parse(nghd_info);
                    var lat = coords[0];
                    var lon = coords[1];
                    var wordData = dict[nghd_info];
                    var nghd = wordData[0]
                    var topWords = wordData[1]
                    var TFIDFdata = wordData[2]
                    var topWordsString = ""
                    for (var i=0;i<topWords.length;i++){
                        topWordsString = topWordsString + topWords[i] + "<br>"
                    }
                    var infoString = ""
                    for (var i=0;i<TFIDFdata.length;i++){
                        infoString = infoString + TFIDFdata[i][0]+ " - count: " + TFIDFdata[i][1]["count"]
                        + ", TF: " + TFIDFdata[i][1]["TF"] + ", IDF: " + TFIDFdata[i][1]["IDF"]
                        + ", TFIDF: " + TFIDFdata[i][1]["TFIDF"] + "<br>"
                    }
                    var marker = createWordMarker(new google.maps.LatLng(lat,lon),nghd,
                                                    topWordsString,infoString)
                    markers.push(marker);
                } 
            }
        };

        var drawPolygon = function(coords){
            //Define the LatLng coordinates for the polygon's path.
            //coords in form [[[#,#],[#,#],[#,#]]]                
            coords = coords[0];
            var polygonCoords = [];
            for (var i = 0; i < coords.length; i++){
                polygonCoords.push(new google.maps.LatLng(coords[i][1],coords[i][0]));
            }
            //Construct the polygon.
            poly = new google.maps.Polygon({
                paths: polygonCoords,
                strokeColor: '#000000',
                strokeOpacity: 0.3,
                strokeWeight: 2,
                fillColor: '#FFFFFF',
                fillOpacity: 0.05
             });
             poly.setMap(map);
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
            plotNghdWord: function(words_per_nghd){
                plotNghdWords(words_per_nghd);
            },
            drawNghdBounds: function(nghd_bounds){
                for (var nghd in nghd_bounds) {
                    if (nghd_bounds.hasOwnProperty(nghd)){
                        drawPolygon(nghd_bounds[nghd]);
                    }
                }
            },
                    
        };
        return api;
    };
});
