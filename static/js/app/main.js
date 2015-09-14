var SCRIPT_ROOT = window.location.href;
console.log(SCRIPT_ROOT);
define(['jquery', 'app/TweetMap'], function ($, TweetMap) {
    $(document).ready(function () {
        var tweetMap = new TweetMap(document.getElementById('map-canvas'), document.getElementById("data-panel"));

       $.ajaxSetup({
            beforeSend: function () {
                $("body").addClass("loading");
            },
            complete: function () {
                $("body").removeClass("loading");
            }
        });

        //on page load
        $("#get-nghd-names-btn").addClass('active');
        console.log(SCRIPT_ROOT + "get-nghd-names");
       $.ajax({
            type: "get",
            url: "https://emojimap.herokuapp.com/get-nghd-names",
            success: function (response) {
                tweetMap.plotNghdNames(response["nghds_to_centralPoint"]);
            },
            error: function () {
                console.log("ajax request failed for " + this.url);
            }
        });

        function clearActiveButtons(){
            $("#get-nghd-names-btn").removeClass('active');
            $("#get-emojis-per-nghd-btn").removeClass('active'); 
            $("#get-words-per-nghd-btn").removeClass('active'); 
        }
             
        $("#get-nghd-names-btn").on("click",function () {
            clearActiveButtons();
            $("#get-nghd-names-btn").addClass('active');
            $.ajax({
                type: "get",
                url: SCRIPT_ROOT + "/get-nghd-names",
                success: function (response) {
                    tweetMap.plotNghdNames(response["nghds_to_centralPoint"]);
                    document.getElementById("instructions").innerHTML =
                    "Click on a neighborhood to see its top tweeted words and emojis.";
                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });

        $("#get-words-per-nghd-btn").on("click",function () {
            clearActiveButtons();
            $("#get-words-per-nghd-btn").addClass('active');
            $.ajax({
                type: "get",
                url: SCRIPT_ROOT + "/get-words-per-nghd",
                success: function (response) {
                    tweetMap.plotNghdWords(response["top_words_per_nghd"]);
                    document.getElementById("instructions").innerHTML =
                    "Click on a list of words to see the tweets they came from.";

                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });

        $("#get-emojis-per-nghd-btn").on("click",function () {
            clearActiveButtons();
            $("#get-emojis-per-nghd-btn").addClass('active');
            $.ajax({
                type: "get",
                url: SCRIPT_ROOT + "/get-emojis-per-nghd",
                success: function (response) {
                    tweetMap.plotNghdEmoji(response["top_emojis_per_nghd"]);
                    document.getElementById("instructions").innerHTML =
                    "Click on a set of emojis to see the tweets they came from.";
                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });
        
        $("#clear-map-btn").on("click",function () {
            clearActiveButtons();
            tweetMap.clearWholeMap();
            document.getElementById("show-nghd-bounds-btn").innerHTML = 
                                          "Show Neighborhood Boundaries";
            document.getElementById("instructions").innerHTML = "";
        });
        
        var loaded_bounds_already = false;
        $("#show-nghd-bounds-btn").on("click",function () {
            if (document.getElementById("show-nghd-bounds-btn").innerHTML 
                == "Show Neighborhood Boundaries"){
                if (loaded_bounds_already){
                    tweetMap.drawNghdBounds([]);
                    document.getElementById("show-nghd-bounds-btn").innerHTML 
                                                 = "Hide Neighborhood Boundaries";
                }
                else{
                    $.ajax({
                        type: "get",
                        url: SCRIPT_ROOT + "/get-nghd-bounds",
                        success: function(response) {
                          loaded_bounds_already = true;
                          tweetMap.drawNghdBounds(response["bounds"]);
                          //replace with hide nghd bounds btn
                          document.getElementById("show-nghd-bounds-btn").innerHTML 
                                                 = "Hide Neighborhood Boundaries";
                        },
                        error: function () {
                            console.log("ajax request failed for " + this.url);
                        }
                    });
                }
            }
            else{
                tweetMap.hideNghdBounds();
                document.getElementById("show-nghd-bounds-btn").innerHTML 
                                            = "Show Neighborhood Boundaries";
            }
        });


    });
});
