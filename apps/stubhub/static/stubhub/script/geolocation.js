$(document).ready(function () {
    if ("geolocation" in navigator) { 
        navigator.geolocation.getCurrentPosition(success, error);    
    } else {
        console.log("Browser does not support geolocation");
    }

    function success(position) {
        var crd = position.coords;

        var userLatitude = crd.latitude;
        var userLongitude = crd.longitude;

        var url = '/geo/';
        url += userLatitude.toFixed(4);
        url += '/';
        url += userLongitude.toFixed(4);

        $.ajax({
        url: url,
        success: function (data) {
            location.reload();
        }

      });

    };

    function error(err) {
        console.log('ERROR');
    };

});