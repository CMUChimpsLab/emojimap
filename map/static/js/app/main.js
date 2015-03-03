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

        $("#get-user-tweets-btn").on("click", function () {
            console.log($("#last-n-days").val());
            console.log($("input[name='tweet-time']:checked").val());
            $.ajax({
                type: "get",
                data: {
                  user_screen_name: $("#user-screen-name-input").val(),
                  last_n_days: $("#last-n-days").val(),
                  tweet_time: $("input[name='tweet-time']:checked").val(),
                  all_tweets: $("#all-tweets").prop("checked"),
                },
                url: $SCRIPT_ROOT + "/get-user-tweets",
                success: function (response) {
                    tweetMap.clearMap();
                    tweetMap.plotTweets(response["tweets"]);
                    // tweetMap.drawLine(pred0[0], pred0[1], home[0], home[1]);
                },
                error: function () {
                    console.log("ajax request failed for " + this.url);
                }
            });
        });

    });
});
