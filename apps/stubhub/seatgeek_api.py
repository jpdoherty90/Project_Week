import json, requests
from pprint import pprint

def get_event_venue_performer_data(url):    
    response = requests.get(url)
    return json.loads(response.text)

all_event_data = get_event_venue_performer_data("https://api.seatgeek.com/2/events?client_id=ODI2MjI2OHwxNTAwOTE1NzYzLjYy&geoip=true&per_page=1000&sort=datetime_local.asc&score.gt=0.5")


pprint(all_event_data)
