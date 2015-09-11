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
        $.ajax({
            type: "get",
            url: $SCRIPT_ROOT + "/get-nghd-names",
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
                url: $SCRIPT_ROOT + "/get-nghd-names",
                success: function (response) {
                    tweetMap.plotNghdNames(response["nghds_to_centralPoint"]);
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
                url: $SCRIPT_ROOT + "/get-emojis-per-nghd",
                success: function (response) {
                    tweetMap.plotNghdEmoji(response["top_emojis_per_nghd"]);
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
                url: $SCRIPT_ROOT + "/get-words-per-nghd",
                success: function (response) {
                    tweetMap.plotNghdWords(response["top_words_per_nghd"]);
                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });
       
        $("#clear-map-btn").on("click",function () {
            clearActiveButtons();
            tweetMap.clearWholeMap();
            $("#show-nghd-bounds-btn").show();
        });

        $("#show-nghd-bounds-btn").on("click",function () {
            $.ajax({
                type: "get",
                url: $SCRIPT_ROOT + "/get-nghd-bounds",
                success: function(response) {
                    tweetMap.drawNghdBounds(response["bounds"]);
                    //replace with hide nghd bounds btn
                    $("#show-nghd-bounds-btn").hide();
                    $("#hide-nghd-bounds-btn").show();
                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });


    });
});
