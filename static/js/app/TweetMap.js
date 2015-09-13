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
        var infowindows_names = {};
        var infobubbles_words = {};
        var infobubbles_emojis = {};
        var polygons = [];
        var mapOptions = {
            center: {lat: latitude, lng: longitude},
            zoom: 13,
            disableDefaultUI: true,
            zoomControl:true,
            styles:
              [{"elementType": "labels","stylers": [{ "visibility": "off" }]},
              {"featureType": "road","elementType": "geometry",
                                "stylers": [{ "visibility": "simplified" }]},
              {"featureType": "poi","stylers": [{ "visibility": "off" }]},
              {"featureType": "landscape","stylers": [{ "visibility": "off"}]}]
        };
        var map = new google.maps.Map(canvas, mapOptions);
       
        var createNameMarker = function(pos,nghd){
            var marker = new MarkerWithLabel({
                position: pos,
                map: map,
                icon:'http://maps.gstatic.com/mapfiles/transparent.png', 
                    //only label is showing 
                labelContent: nghd,
                labelAnchor: new google.maps.Point(25,0)
            });
            google.maps.event.addListener(marker,'click',function(){
                if (infowindows_names[nghd] != undefined) {
                    infowindows_names[nghd].open(map,marker);
                } else {
                    $.ajax({
                        type: "get",
                        data: {nghd:nghd},
                        url: SCRIPT_ROOT + "/get-words-emojis-for-nghd",
                        success: function(response) {
                            top_words_and_emojis = response["top_words_and_emojis"];
                            topWords = top_words_and_emojis["top words"];
                            topEmojis = top_words_and_emojis["top emojis"];
                            var topWordsString = "";
                            for (var i=0;i<topWords.length;i++){
                                topWordsString = topWordsString + topWords[i] + "<br>"
                            }
                             var topEmojisString = "";
                            for (var i=0;i<topEmojis.length;i++){
                                topEmojisString = topEmojisString + topEmojis[i];
                            }
                            var infowindow = new google.maps.InfoWindow({
                                content:topWordsString + "<br>" + topEmojisString 
                            });
                            infowindow.open(map,marker);
                            infowindows_names[nghd] = infowindow;
                        },
                        error: function () {
                            console.log("ajax request failed for " + this.url);
                        }
                    });
                }
            });
            return marker;
        };

        var plotNghdNames = function(nghd_names){
            for (var nghd in nghd_names){
                coords = nghd_names[nghd];
                lat = coords[0];
                lon = coords[1];
                var marker = createNameMarker(new google.maps.LatLng(lat,lon),nghd)
                markers.push(marker);
            }
        } 

        var createEmojiMarker = function(pos,nghd,topEmojis){
            var topEmojisString = "";
            for (var i=0;i<topEmojis.length;i++){
                topEmojisString = topEmojisString + topEmojis[i];
            }
            var marker = new MarkerWithLabel({
                position: pos,
                map: map,
                title: nghd,
                icon:'http://maps.gstatic.com/mapfiles/transparent.png', 
                    //only label is showing 
                labelContent: topEmojisString,
                labelAnchor: new google.maps.Point(25,0),
                labelStyle: {"font-size":"130%"}
            });
            google.maps.event.addListener(marker,'click',function(){
                if (infobubbles_emojis[nghd] != undefined) {
                    infobubbles_emojis[nghd].open(map,marker);
                } else {
                    $.ajax({
                        type: "get",
                        data:{nghd: nghd},
                        url: SCRIPT_ROOT + "/get-tweets-per-emoji",
                        success: function(response) {
                            tweets_per_emoji = response["tweets_per_emoji"];
                            var infobubble = new InfoBubble({
                                maxWidth:600,
                                maxHeight:300
                            });
                            for (var i=0;i<topEmojis.length;i++){
                                emoji = topEmojis[i];
                                var tweets = "";
                                for (var j=0;j<tweets_per_emoji[emoji].length;j++){ 
                                    tweets = tweets + tweets_per_emoji[emoji][j] + "<br>";
                                }
                                infobubble.addTab(emoji,tweets);
                            }
                            infobubble.open(map,marker);
                            infobubbles_emojis[nghd] = infobubble;
                        },
                        error: function () {
                            console.log("ajax request failed for " + this.url);
                        }
                    });
                }
            });
            return marker;
        };

        var plotNghdEmojis = function(top_emojis_per_nghd){
            for (var nghd_info in top_emojis_per_nghd){
                if (top_emojis_per_nghd.hasOwnProperty(nghd_info)){
                    var coords = JSON.parse(nghd_info);
                    var lat = coords[0];
                    var lon = coords[1];
                    var nghd = coords[2]; //nghd looks like 'nghd' right now
                    nghd = nghd.substring(1,nghd.length-1);
                    var marker = createEmojiMarker(new google.maps.LatLng(lat,lon), 
                                                nghd,top_emojis_per_nghd[nghd_info]);
                    markers.push(marker);
                }
            }
        };  
        
        var createWordMarker = function(pos,nghd,topWords){
            var topWordsString = "";
            for (var i=0;i<topWords.length;i++){
                topWordsString = topWordsString + topWords[i] + "<br>"
            }
            var marker = new MarkerWithLabel({
                position: pos,
                map: map,
                title: nghd,
                icon:'http://maps.gstatic.com/mapfiles/transparent.png', 
                    //only label is showing 
                labelContent: topWordsString,
                labelAnchor: new google.maps.Point(25,0)
             });
            
            /*google.maps.event.addListener(marker, 'mouseover', function() {
                marker.set("labelStyle",{"font-weight":700,"font-size":"120%"});
            });
            google.maps.event.addListener(marker, 'mouseout', function() {
                marker.set("labelStyle",{"font-weight": 400,"font-size":"100%"});
            });*/

            google.maps.event.addListener(marker,'click',function(){
                if (infobubbles_words[nghd] != undefined) {
                    infobubbles_words[nghd].open(map,marker);
                } else {
                    $.ajax({
                        type: "get",
                        data:{nghd: nghd},
                        url: SCRIPT_ROOT + "/get-tweets-per-word",
                        success: function(response) {
                            tweets_per_word = response["tweets_per_word"];
                            var infobubble = new InfoBubble({
                                maxWidth:600,
                                maxHeight:300
                            });
                            for (var i=0;i<topWords.length;i++){
                                word = topWords[i];
                                var tweets = "";
                                for (var j=0;j<tweets_per_word[word].length;j++){ 
                                    tweets = tweets + tweets_per_word[word][j] + "<br>";
                                }
                                infobubble.addTab(word,tweets);
                            }
                            infobubble.open(map,marker);
                            infobubbles_words[nghd] = infobubble;
                        },
                        error: function () {
                            console.log("ajax request failed for " + this.url);
                        }
                    });
                }
            });
            return marker;
        };

        var plotWords = function(top_words_per_nghd){
            for (var nghd_info in top_words_per_nghd){
                if (top_words_per_nghd.hasOwnProperty(nghd_info)){
                    var coords = JSON.parse(nghd_info);
                    var lat = coords[0];
                    var lon = coords[1];
                    var nghd = coords[2]; //nghd looks like 'nghd' right now
                    nghd = nghd.substring(1,nghd.length-1);
                    var marker = createWordMarker(new google.maps.LatLng(lat,lon),
                                               nghd,top_words_per_nghd[nghd_info]);
                    markers.push(marker);
                } 
            }
        };

        var drawPolygon = function(coords){
            //coords currently in form [[[#,#],[#,#],[#,#]]]                
            coords = coords[0];
            var polygonCoords = [];
            for (var i = 0; i < coords.length; i++){
                polygonCoords.push(new google.maps.LatLng(coords[i][1],coords[i][0]));
            }
            //Construct the polygon.
            poly = new google.maps.Polygon({
                paths: polygonCoords,
                strokeColor: '#000066',
                strokeOpacity: 0.3,
                strokeWeight: 2,
                fillColor: '#000066',
                fillOpacity: 0.05
             });
             poly.setMap(map);
             polygons.push(poly);
        };

        var api =  {
            clearMap: function () {
                for(var i = 0; i < markers.length; i++) {
                    markers[i].setMap(null);
                }
                for(var nghd in infobubbles_words) {
                    infobubbles_words[nghd].close();
                }
                for(var nghd in infobubbles_emojis) {
                    infobubbles_emojis[nghd].close();
                }
            },
            clearWholeMap: function (){
                api.clearMap();
                for(var i = 0; i < polygons.length; i++) {
                    polygons[i].setMap(null);
                }
            },
            plotNghdNames: function(nghd_names){
                map.setZoom(13);
                api.clearMap();
                plotNghdNames(nghd_names); 
            },  
            plotNghdEmoji: function(top_emojis_per_nghd){
                map.setZoom(13);
                api.clearMap();
                plotNghdEmojis(top_emojis_per_nghd);
            },
            plotNghdWords: function(top_words_per_nghd){
                map.setZoom(14);
                api.clearMap();
                plotWords(top_words_per_nghd);
            },
            drawNghdBounds: function(nghd_bounds){
                if (polygons.length==0){
                    for (var nghd in nghd_bounds) {
                        if (nghd_bounds.hasOwnProperty(nghd)){
                            drawPolygon(nghd_bounds[nghd]);
                        }
                    }
                }
                else{
                    for(var i = 0; i < polygons.length; i++) {
                        polygons[i].setMap(map);
                    }
                }
            },
            hideNghdBounds: function(){
                for(var i = 0; i < polygons.length; i++) {
                    polygons[i].setMap(null);
                }
            },
        };
        return api;
    };
});
