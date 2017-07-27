


def get_local_venues_data(url):
    response = requests.get(url)
    return json.loads(response.text)

def get_event_performer_category_data(url):    
    response = requests.get(url)
    return json.loads(response.text)

venue_url = "https://api.seatgeek.com/2/venues?lat="
venue_url += str(lat)
venue_url += "&lon="
venue_url += str(lon)
venue_url += "&range=12mi&client_id=ODI2MjI2OHwxNTAwOTE1NzYzLjYy&per_page=100"

all_local_venue_data = get_local_venues_data(venue_url)
all_local_venues = all_local_venue_data['venues']

for venue in all_local_venues:
    name = venue['name']
    address = venue['address']
    extended_address = venue['extended_address']
    try:
        Venue.objects.get(name=name)
    except:
        Venue.objects.create(name=name, address=address, extended_address=extended_address)

event_url = "https://api.seatgeek.com/2/events?client_id=ODI2MjI2OHwxNTAwOTE1NzYzLjYy&lat="
event_url += str(lat)
event_url += "&lon="
event_url += str(lon)
event_url += "&range=12mi&per_page=1000&sort=datetime_local.asc&score.gt=0.5"

all_event_data = get_event_performer_category_data(event_url)
all_events = all_event_data['events']

for event in all_events:
    for performer in event['performers']:
        name = performer['name']
        try:
            Performer.objects.get(name=name)
        except:
            Performer.objects.create(name=name)


for event in all_events:
    tag = event['type']
    try:
        Category.objects.get(tag=tag)
    except:
        Category.objects.create(tag=tag)

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
        Venue.objects.create(name=name, address=address, extended_address=extended_address)
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
    





