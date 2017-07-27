
$(document).ready(function () {

    var curr_lat;
    var curr_lon;

    if ("geolocation" in navigator) { 
        navigator.geolocation.getCurrentPosition(success, error);
            
    } else {
        console.log("-----------------------------------------------");
        console.log("Browser doesn't support geolocation!");
        console.log("-----------------------------------------------");
    }

    function success(position) {
        var crd = position.coords;

        curr_lat = crd.latitude;
        curr_lon = crd.longitude;
        console.log(curr_lat)
        console.log(curr_lon)

        var url = '/geo/';
        url += curr_lat.toFixed(4);
        url += '/';
        url += curr_lon.toFixed(4);

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