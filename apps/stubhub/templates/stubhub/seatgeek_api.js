$(document).ready(function() {
    var events_by_location;
    // code to build url
    $('#event_list').html('');
    events_by_location = 'https://api.seatgeek.com/2/events?client_id=ODI2MjI2OHwxNTAwOTE1NzYzLjYy';
    $.get(events_by_location, function(res) {
        var all_events = res.events;
        for (var i = 0; i<all_events.length; i++){
            $('#events_list').append('<h1>' + all_events[i].title + '</h1>');
            $('#events_list').append('<p>' + all_events[i].title + '<p>');
        }
    }, 'json');
});