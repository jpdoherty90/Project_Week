import django
import json, requests
from datetime import datetime
from pprint import pprint
from apps.stubhub.models import Venue, Performer, Event, Category

def get_data(url):
    response = requests.get(url)
    return json.loads(response.text)

# ******TO UPDATE EVENTS, PERFORMERS, VENUES, or CATEGORIES******
# ******Go to the python shell and execfile('THISFILE')******
# ******If you don't need all the models, just comment out what you don't need******

# ******VENUES******

all_Chicago_venue_data = get_data("https://api.seatgeek.com/2/venues?geoip=true&client_id=ODI2MjI2OHwxNTAwOTE1NzYzLjYy&per_page=100")
all_Chi_venues = all_Chicago_venue_data['venues']

# # write venue data to our models
for venue in all_Chi_venues:
    name = venue['name']
    address = venue['address']
    extended_address = venue['extended_address']
    try:
        Venue.objects.get(name=name)
    except:
        Venue.objects.create(name=name, address=address, extended_address=extended_address)

# ******EVENTS, PERFORMERS, AND CATEGORIES******

all_event_data = get_data("https://api.seatgeek.com/2/events?client_id=ODI2MjI2OHwxNTAwOTE1NzYzLjYy&geoip=true&per_page=1000&sort=datetime_local.asc&score.gt=0.5")
all_events = all_event_data['events']

#  ******PERFORMERS******

# # write performer data to our models
for event in all_events:
    for performer in event['performers']:
        name = performer['name']
        try:
            Performer.objects.get(name=name)
        except:
            Performer.objects.create(name=name)

#  ******CATEGORIES******

# write category data to our models
for event in all_events:
    taxonomies = event['taxonomies']
    for category in taxonomies:
      tag = category['name']
      formatted_tag = tag.replace('_', ' ')
      display_tag = formatted_tag.title()
      seatgeek_ref = category['id']
      parent_ref = category['parent_id']
    try:
        Category.objects.get(tag=tag)
    except:
        Category.objects.create(tag=tag, seatgeek_ref=seatgeek_ref,parent_ref=parent_ref, display_tag=display_tag)

#  ******EVENTS******

# write event data to our models
for event in all_events:
    title =  event['title']
    short_title = event['short_title']
    event_date_time = datetime.strptime(event['datetime_local'], "%Y-%m-%dT%H:%M:%S")
    visible_until = datetime.strptime(event['visible_until_utc'], "%Y-%m-%dT%H:%M:%S")
    popularity_score = event['score']
    image = event['performers'][0]['image']
    category = Category.objects.get(tag = event['type'])
    event_venue=event['venue']['name']
    try:
        venue = Venue.objects.get(name = event_venue)
    except:
        name = event['venue']['name']
        address = event['venue']['address']
        extended_address = event['venue']['extended_address']
        venue = Venue.objects.create(name=name, address=address, extended_address=extended_address)
    try:
        Event.objects.get(title=title)
    except:
        this_event = Event.objects.create(title=title, short_title=short_title, event_date_time=event_date_time, visible_until=visible_until, popularity_score=popularity_score, category=category, venue=venue, image=image)
        for performer in event['performers']:
            try:
                performer = Performer.objects.get(name=name)
            except:
                performer = Performer.objects.create(name=name)
            this_event.performers.add(performer)
