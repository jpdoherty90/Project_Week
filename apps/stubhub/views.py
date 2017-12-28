from __future__ import unicode_literals
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Avg
from models import User, Ticket, Event, Performer, Venue, Category, Purchase
from django.contrib import messages
import re, bcrypt, json, requests
from pprint import pprint
from datetime import datetime



def index(request):
    request.session['nli_source'] = 'None'
    today = datetime.now()
    all_events = Event.objects.filter(visible_until__gte=today).order_by('event_date_time', 'popularity_score')
    categories = Category.objects.order_by('tag')
    context = {
        'selected_events': all_events,
        'categories': categories,
    }
    return render(request, 'stubhub/home.html', context)


def register(request):
    errors = User.objects.newUserValidator(request.POST)
    if len(errors):
        for tag, error in errors.iteritems():
            messages.add_message(request, messages.ERROR, errors[tag])
        return redirect("/log_reg")
    else:
        user = generateNewUser(request)
        if not user:
            messages.add_message(request, messages.ERROR, "User email already exists.")
            return redirect("/")
        else:
            setSession(request, user)
            return handleNliSource(request)


def generateNewUser(request):
    first =  request.POST['first_name']
    last =  request.POST['last_name']
    mail = request.POST['email']
    hash1 = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
    user = User.objects.create(first_name=first, last_name=last, email=mail, password_hash=hash1)
    return user


def setSession(request, user):
    request.session['user_id'] = user.id
    request.session['user_name'] = user.first_name
    request.session['cart']=[]


def handleNliSource(request):
    if 'nli_source' in request.session and request.session['nli_source'] == 'sell':
        return redirect('/sell/{}'.format(request.session['nli_event_id']))
    elif 'nli_source' in request.session and request.session['nli_source'] == 'cart':
        return redirect('/buy/{}'.format(request.session['nli_event_id']))
    else:
        return redirect('/')


def login(request):
    errors = User.objects.loginValidator(request.POST)
    if len(errors):
        return invalidLogin(request)
    else:
        email = request.POST['email']
        user = User.objects.get(email=email)
        setSession(request, user)
        return handleNliSource(request)


def invalidLogin(request):
    messages.add_message(request, messages.ERROR, "Invalid email or password.")
    return redirect("/log_reg")


def log_out(request):
    if 'cart' in request.session and len(request.session['cart']) > 0:
        return redirect('/log_out/confirm')
    else:
        request.session.clear()
        return redirect("/")


def log_out_confirm(request):
    return render(request, 'stubhub/log_out_confirm.html')


def removeAllFromCart(request):
    for ticket_id in request.session['cart']:
        Ticket.objects.filter(id=ticket_id).update(available=True)
    request.session['cart']=[]
    return redirect('/log_out')


def init_sale(request, parameter):
    request.session['sell_path'] = False
    if not userLoggedIn(request):
        request.session['nli_source'] = 'sell'
        request.session['nli_event_id'] = parameter
        return redirect('/log_reg')
    event = getEvent(parameter)
    num_tix = request.POST.get('num_tix', False)
    tix = []
    for i in range(1, int(num_tix) + 1):
        tix.append(i)
    context = {
        "event": event,
        "tix": tix,
        "num_tix": num_tix
    }
    return render(request, 'stubhub/init_sale.html', context)


def userLoggedIn(request):
    if request.session['user_id']:
        return True
    return False


def getEvent(eventId):
    event = Event.objects.get(id=eventId)
    return event


def log_reg(request):
    return render (request,"stubhub/login.html")


def post_tickets(request, parameter):
    event = getEvent(parameter)
    createTickets(request, event)
    url = '/ticket_posted/'
    url += str(parameter)
    return redirect(url)


def createTickets(request, event):
    seller = getCurrentuser(request)
    num_tix = request.POST['num_tix']
    price = request.POST['price']
    for i in range(int(num_tix)):
        seat = "seat_" + str(i+1) 
        seat = request.POST[seat]
        Ticket.objects.create(event=event, seller=seller, seat=seat, price=price)


def getCurrentuser(request):
    userId = request.session['user_id']
    user = User.objects.get(id=userId)
    return user


def ticket_posted(request, parameter):
    event = getEvent(parameter)
    context = {
        "event": event,
    }
    return render(request, 'stubhub/sell_success.html', context)


def acc_info(request, parameter):
    user = User.objects.get(id=parameter)
    tickets_for_sale = Ticket.objects.filter(seller=user, available=True)
    tickets_sold = Ticket.objects.filter(seller=user, available=False)
    tickets_bought = Ticket.objects.filter(buyer=user, available=False)
    context = { 
        'user': user,
        'tickets_for_sale': tickets_for_sale,
        'tickets_sold': tickets_sold,
        'tickets_bought': tickets_bought
    }
    if userLoggedIn(request) and request.session['user_id'] == user.id:
        return render(request,"stubhub/acc_info.html",context)
    else:
        return render(request,"stubhub/show_user.html",context)


def cart(request):
    context = getCartContext(request)
    return render (request,"stubhub/cart.html",context)


def getCartContext(request):
    item_ids = request.session['cart']
    items = []
    total=0
    for item_id in item_ids:
        ticket = Ticket.objects.get(id=item_id)
        items.append(ticket)
    for ticket in items:
        total += int(ticket.price)
    request.session['total'] = total
    context = { 
        'user': getCurrentuser(request),
        'items': items,
        'total':total,
    }
    return context


def add_to_cart(request):
    if not userLoggedIn(request):
        return goToLogRegFromCart()
    if 'cart' not in request.session:
        initializeCart(request)
    ticketId = request.POST['ticket_id']
    string = updateTicketAvailability(request, ticketId)
    request.session['cart'].append(ticketId)
    x = "/" + str(string)
    return redirect('/buy'+ x)


def add_to_cart_from(request, parameter):
    if not userLoggedIn(request):
        return goToLogRegFromCart()
    if 'cart' not in request.session:
        initializeCart(request)
    ticketId = request.POST['ticket_id']
    updateTicketAvailability(request, ticketId)
    request.session['cart'].append(ticketId)
    x = "/" + str(parameter)
    return redirect('/acc_info'+ x)


def updateTicketAvailability(request, ticketId):
    ticket = Ticket.objects.get(id=ticketId)
    Ticket.objects.filter(id=ticketId).update(available=False)
    request.session['cart'].append(ticketId)
    return ticket.event.id


def goToLogRegFromCart():
    request.session['nli_source'] = 'cart'
    return redirect('/log_reg')


def initializeCart(request):
    request.session['cart']=[]


def remove_from_cart(request,parameter):
    ticket_id = parameter
    request.session['cart'].remove(ticket_id)
    Ticket.objects.filter(id=ticket_id).update(available=True)
    return redirect('/cart')


def check_out(request):
    if cartIsEmpty():
        return displayEmptyCartMsg(request)
    context = getCartContext(request)
    return render(request,'stubhub/check_out.html',context)


def cartIsEmpty():
    return request.session['cart'] == []


def displayEmptyCartMsg(request):
    messages.add_message(request, messages.ERROR, "Your Cart is Empty",extra_tags='CE')
    return redirect("/cart")


def payment_shipping(request):
    return render(request,'stubhub/payment_shipping.html')


def order_review(request):
    cardNumber = request.POST['card_number']
    creditCard = getCreditCard(request)
    addrress = getAddress(request)
    request.session['card'] = creditCard
    request.session['address'] = address
    context = { 
        'user': User.objects.get(id=request.session['user_id']),
        'items': getItems(request),
        'total': request.session['total'],
        'card': card,
        'address': address,
        'last_four': cardNumber[-4:]
    }
    return render(request,'stubhub/order_review.html',context)


def getCreditCard(request):
    creditCard = {
        'first_name': request.POST['first_name'],
        'last_name': request.POST['last_name'],
        'card_number': cardNumber,
        'exp_month':request.POST['month'],
        'exp_year': request.POST['year']
    }
    return creditCard


def getAddress(request):
    addrress = {
        'full_name': request.POST['full_name'],
        'address': request.POST['address'],
        'zip': request.POST['zip'],
        'city':request.POST['city'],
        'state': request.POST['state'],
        'country':request.POST['country']
    }
    return address


def getItems(request):
    items = []
    item_ids = request.session['cart']
    for item_id in item_ids:
        ticket = Ticket.objects.get(id=item_id)
        items.append(ticket)
    return items


def purchase(request):
    return redirect('/confirmation.html')


def order_confirmation(request):
    user = getCurrentuser(request)
    items = getItems(request)
    for ticket in items:
        Ticket.objects.filter(id=ticket.id).update(buyer=user)
    request.session['total'] = 0
    request.session['cart'] = []
    return render(request,'stubhub/confirmation.html')
    

def process_search(request):
    if len(request.POST['text_search']) > 0:
        search_info = request.POST['text_search']
        request.session['search_field'] = 'text'
    elif len(request.POST['event_date']) > 0:
        search_info = request.POST['event_date']
        request.session['search_field'] = 'date'
    elif len(request.POST['category']) > 0:
        search_info = request.POST['category']
        request.session['search_field'] = 'category'
    else:
        return redirect('/')
    request.session['search_info'] = search_info
    return redirect('/search')


def search_results(request):
    search_field = request.session['search_field']
    search_info = request.session['search_info']
    today = datetime.now()
    if search_field == 'text':
        selected_events = processTextSearch(search_info)
    elif search_field == 'category':
        selected_events = processCategorySearch(search_info)
    elif search_field == 'date':
        selected_events = Event.objects.filter(event_date_time__contains=search_info)    
    num_results = len(selected_events)
    categories = Category.objects.order_by('tag')
    context = {
        'num_results' : num_results,
        'selected_events': selected_events,
        'query': search_info,
        'categories': categories
    }
    return render(request, 'stubhub/search_results.html', context)


def processTextSearch(text):
    titleMatches = Event.objects.filter(visible_until__gte=today).filter(title__contains=text)
    venueMatches = Event.objects.filter(visible_until__gte=today).filter(venue__name__contains=text)
    performerMatches = Event.objects.filter(visible_until__gte=today).filter(performers__name__contains=text)
    return titleMatches|venueMatches|performerMatches


def processCategorySearch(searchedCategory):
    category = Category.objects.get(display_tag=searchedCategory)
    category_ref = category.seatgeek_ref
    categoryMatches = Event.objects.filter(visible_until__gte=today).filter(category=category)
    categoryParentMatches = Event.objects.filter(visible_until__gte=today).filter(category__parent_ref=category_ref)
    return categoryMatches|categoryParentMatches


def show_event(request, parameter):
    event = Event.objects.get(id=parameter)
    context = { "event": event }
    return render(request, 'stubhub/show_event.html', context)


def buy_tix(request, parameter):
    event = getEvent(parameter)
    if userLoggedIn(request):
        currentUserId = request.session['user_id']
    else:
        request.session['nli_event_id'] = parameter
        currentUserId = -1
    if request.method == "GET":
        available_tix = Ticket.objects.filter(available=True, event=event).exclude(seller=currentUserId).order_by("seat")
    elif request.method == "POST":
        available_tix = putAvailableTicketsInOrder(request, event)
    context = {
        "event": event,
        "available_tix": available_tix,
    }
    return render(request, 'stubhub/buy_tix.html', context)


def putAvailableTicketsInOrder(request, event):
    availableTickets = Ticket.objects.filter(available=True, event=event)
    filterBy = request.POST['filter_by']
    if filterBy == "seat":
        availableTickets = availableTickets.order_by("seat")
    elif filterBy == "price_asc":
        availableTickets = availableTickets.order_by("price")
    elif filterBy == "price_desc":
        availableTickets = availableTickets.order_by("-price")
    return availableTickets


def geo(request, lat, lon):
    event_url = "https://api.seatgeek.com/2/events?client_id=ODI2MjI2OHwxNTAwOTE1NzYzLjYy&lat=" + str(lat)
    event_url += "&lon=" + str(lon) + "&range=5mi&per_page=1000&sort=datetime_local.asc&score.gt=0.5"
    allEventData = getData(event_url)
    allEvents = allEventData['events']
    addCategoriesToDatabaseIfNecessary(allEvents)
    addEventsToDatabaseIfNecessary(allEvents)
    request.session['geo'] = True
    return redirect('/');


def getData(url):
    response = requests.get(url)
    return json.loads(response.text)


def addCategoriesToDatabaseIfNecessary(events):
    for event in events:
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


def addEventsToDatabaseIfNecessary(events):
    for event in events:
        title =  event['title']
        short_title = event['short_title']
        event_date_time = datetime.strptime(event['datetime_local'], "%Y-%m-%dT%H:%M:%S")
        visible_until = datetime.strptime(event['visible_until_utc'], "%Y-%m-%dT%H:%M:%S")
        popularity_score = event['score']
        image = event['performers'][0]['image']
        category = Category.objects.get(tag = event['type'])
        event_venue=event['venue']['name']
        try:
            venue = Venue.objects.get(name=event_venue)
        except:
            name = event['venue']['name']
            address = event['venue']['address']
            extended_address = event['venue']['extended_address']
            venue = Venue.objects.create(name=name, address=address, extended_address=extended_address)
        try:
            Event.objects.get(title=title)
        except:
            thisEvent = Event.objects.create(title=title, short_title=short_title, event_date_time=event_date_time, 
                                                visible_until=visible_until, popularity_score=popularity_score, 
                                                category=category, venue=venue, image=image)
            for performer in event['performers']:
                try:
                    performer = Performer.objects.get(name=name)
                except:
                    performer = Performer.objects.create(name=name)
                thisEvent.performers.add(performer)


def sell_search(request):
    request.session['sell_path'] = True
    categories = Category.objects.order_by('tag')
    context = { 'categories': categories }
    return render(request, 'stubhub/sell_search.html', context)