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
       
        $("#get-emojis-per-bin-btn").on("click",function () {
            $.ajax({
                type: "get",
                url: $SCRIPT_ROOT + "/get-emojis-per-bin",
                success: function (response) {
                    tweetMap.plotBinEmoji(response["emojis_per_bin"]);
                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });

        $("#get-emojis-per-nghd-btn").on("click",function () {
            $.ajax({
                type: "get",
                url: $SCRIPT_ROOT + "/get-emojis-per-nghd",
                success: function (response) {
                    tweetMap.plotNghdEmoji(response["emojis_per_nghd"]);
                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });

        $("#get-words-per-nghd-btn").on("click",function () {
            $.ajax({
                type: "get",
                url: $SCRIPT_ROOT + "/get-words-per-nghd",
                success: function (response) {
                    tweetMap.plotNghdWord(response["top_words_per_nghd"]);
                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });


        $("#show-nghd-bounds-btn").on("click",function () {
            $.ajax({
                type: "get",
                url: $SCRIPT_ROOT + "/get-nghd-bounds",
                success: function(response) {
                    tweetMap.drawNghdBounds(response["nghd_bounds"]);
                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });


    });
});
