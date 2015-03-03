require.config({
    baseUrl: 'static/js',
    urlArgs: 'bust=' + (new Date()).getTime(),
    // paths for various dependencies; I guess each list is a list of possible options.
    paths: {
        jquery: ['//code.jquery.com/jquery-2.1.1.min', 'libs/jquery/dist/jquery.min'],
        bootstrap: ['//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min', 'libs/bootstrap/dist/js/bootstrap.min'],
        async: 'libs/requirejs-plugins/src/async',
        maplabel: 'libs/google-maps-utility-library-v3/maplabel/src/maplabel'
    },
    shim: {
        'bootstrap': {
            'deps': ['jquery']
        },
    }
});

// This starts the whole shebang going. Requires app/main.js, which in turn
// requires app/TweetMap and jquery and everything else.
require(['app/main']);
