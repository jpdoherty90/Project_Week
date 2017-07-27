# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Avg

from models import User, Ticket, Event, Performer, Venue, Category, Purchase

from django.contrib import messages

import re

import bcrypt


#-----------------------------------------------------------------
#-----------------------------------------------------------------


def index(request):
    try: 
        user = User.objects.get(id=request.session['user_id'])
    except:
        user = None
    all_events = Event.objects.order_by('event_date_time', 'popularity_score')
    categories = Category.objects.order_by('tag')
    context = {
        'selected_events': all_events,
        'categories': categories,
        'user': user
    }

    return render(request, 'stubhub/home.html', context)


#-----------------------------------------------------------------
#-----------------------------------------------------------------

def register(request):
    
    errors = User.objects.new_user_validator(request.POST)
    if len(errors):
        for tag, error in errors.iteritems():
            messages.add_message(request, messages.ERROR, errors[tag])
        return redirect("/log_reg")
    else:
        first =  request.POST['first_name']
        last =  request.POST['last_name']
        mail = request.POST['email']
        hash1 = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
 
        user = User.objects.create(first_name=first, last_name=last, email=mail, password_hash=hash1)

        if not user:
            messages.add_message(request, messages.ERROR, "User email already exists.")
            return redirect("/")
        else:
            request.session['user_id'] = user.id
            request.session['user_name'] = user.first_name
            if request.session['nli_source']=='sell':
                return redirect('/sell/{}'.format(request.session['nli_event_id']))
            elif request.session['nli_source']=='cart':
                return redirect('/buy/{}'.format(request.session['nli_event_id']))
            else:
                return redirect('/')

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def login(request):
    errors = User.objects.login_validator(request.POST)
    email = request.POST['email']
    if len(errors):
        messages.add_message(request, messages.ERROR, "Invalid email or password.")
        return redirect("/log_reg")
    else:
        user = User.objects.get(email=email)
        request.session['user_id'] = user.id
        request.session['user_name'] = user.first_name
        if request.session['nli_source']=='sell':
            return redirect('/sell/{}'.format(request.session['nli_event_id']))
        elif request.session['nli_source']=='cart':
            return redirect('/buy/{}'.format(request.session['nli_event_id']))
        else:
            return redirect('/')

#-----------------------------------------------------------------
#----------------------------------------------------------------

def log_out(request):
    request.session.clear()
    return redirect("/")

#-----------------------------------------------------------------
#-----------------------------------------------------------------


def init_sale(request, parameter):
    
    # Overwriting the sell attribute of request.session now that we've reached the end of the sell-search-path
    request.session['sell_path'] = False
    request.session.modified = True
    # Make sure user is logged in, if not, force them to log-in first
    try: 
        request.session['user_id']
    except:
        request.session['nli_source'] = 'sell'
        request.session['nli_event_id'] = parameter
        return redirect('/log_reg')

    event_id = parameter
    event = Event.objects.get(id=event_id)

    context = {
        "event": event,
    }

    if request.method == "POST":

        num_tix = request.POST['num_tix']

        tix = []

        for i in range(1, int(num_tix) + 1):
            tix.append(i)
            
        context['tix'] = tix
        context['num_tix'] = num_tix

    return render(request, 'stubhub/init_sale.html', context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def post_tickets(request, parameter):
    
    event_id = parameter
    event = Event.objects.get(id=event_id)

    seller_id = request.session['user_id']
    seller = User.objects.get(id=seller_id)

    num_tix = request.POST['num_tix']
    price = request.POST['price']

    for i in range(int(num_tix)):
        
        seat = "seat_" + str(i+1) 
        seat = request.POST[seat]
        
        reg = re.compile(r'(?P<numbers>\d*)(?P<letters>.*)')
        result = reg.search(seat)
        if result:
            numbers = result.group('numbers')
            letters = result.group('letters')
        
        Ticket.objects.create(event=event, seller=seller, seat_num=numbers, seat_letter=letters, price=price)

    url = '/ticket_posted/'
    url += str(parameter)

    return redirect(url)

#-----------------------------------------------------------------
#-----------------------------------------------------------------


def ticket_posted(request, parameter):
    
    event_id = parameter
    event = Event.objects.get(id=event_id)
    
    context = {
        "event": event,
    }

    return render(request, 'stubhub/sell_success.html', context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def log_reg(request):
    return render (request,"stubhub/login.html")

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def acc_info(request, parameter):
    
    user = User.objects.get(id=parameter)

    tickets_for_sale = Ticket.objects.filter(seller=user, available=True)

    tickets_sold = Ticket.objects.filter(seller=user, available=False)

    tickets_bought = Ticket.objects.filter(buyer=user, available=False)
    
    context = { 
        'user': user,
        'tickets_for_sale': tickets_for_sale,
        'tickets_sold': tickets_sold,
        'tickets_bought': tickets_bought,
    }

    if 'user_id' in request.session and request.session['user_id'] == user.id:
        return render(request,"stubhub/acc_info.html",context)
    else:
        return render(request,"stubhub/show_user.html",context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def cart(request):
    request.session.modified = True
    if 'cart' not in request.session:
        request.session['cart']=[]
    item_ids = request.session['cart']
    print request.session['cart']
    items = []
    total=0
    for item_id in item_ids:
        ticket=Ticket.objects.get(id=item_id)
        items.append(ticket)
    for ticket in items:
        total+=int(ticket.price)
        print ticket.available
    
    context = { 'user': User.objects.get(id=request.session['user_id']),
                'items': items,
                'total':total,
    }
    

    return render (request,"stubhub/cart.html",context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def add_to_cart(request):
    # Make sure user is logged in, if not, force them to log-in first
    try: 
        request.session['user_id']
    except:
        request.session['nli_source'] = 'cart'
        return redirect('/log_reg')

    if 'cart' not in request.session:
        request.session['cart']=[]
    request.session.modified = True
    ticket_id= request.POST['ticket_id']
    ticket = Ticket.objects.get(id=ticket_id)
    Ticket.objects.filter(id=ticket_id).update(available=False)
   
    request.session['cart'].append(ticket_id)
    x="/"+str(ticket.event.id)
    
    return redirect('/buy'+ x)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def remove_from_cart(request,parameter):
    request.session.modified = True
    ticket_id=parameter
    request.session['cart'].remove(ticket_id)
    items=request.session['cart']
    Ticket.objects.filter(id=ticket_id).update(available=True)
    ticket = Ticket.objects.get(id=ticket_id)
    return redirect('/cart')
#-----------------------------------------------------------------
#-----------------------------------------------------------------

def check_out(request):
    request.session.modified = True
    if 'cart' not in request.session:
        request.session['cart']=[]
    item_ids = request.session['cart']
    print request.session['cart']
    items = []
    total=0
    for item_id in item_ids:
        ticket=Ticket.objects.get(id=item_id)
        items.append(ticket)
    for ticket in items:
        total+=int(ticket.price)
        print ticket.available

    request.session['total']= total
    
    context = { 'user': User.objects.get(id=request.session['user_id']),
                'items': items,
                'total':total,
    }
    return render(request,'stubhub/check_out.html',context)
#-----------------------------------------------------------------
#-----------------------------------------------------------------
def payment_shipping (request):
    
    return render(request,'stubhub/payment_shipping.html')
#-----------------------------------------------------------------
#-----------------------------------------------------------------
def order_review(request):
    request.session['card']={
        'first_name': request.POST['first_name'],
        'last_name': request.POST['last_name'],
        'card_number': request.POST['card_number'],
        'exp_month':request.POST['month'],
        'exp_year': request.POST['year']
    }
    card = request.session['card']

    request.session['address']={
        'full_name': request.POST['full_name'],
        'address': request.POST['address'],
        'zip': request.POST['card_number'],
        'city':request.POST['city'],
        'state': request.POST['state'],
        'country':request.POST['country']
    }
    address= request.session['address']

    items = []
    item_ids = request.session['cart']
    for item_id in item_ids:
        ticket=Ticket.objects.get(id=item_id)
        items.append(ticket)
    total = request.session['total']
    context = { 'user': User.objects.get(id=request.session['user_id']),
                'items': items,
                'total':total,
                'card':card,
                'address':address
    }
    return render(request,'stubhub/order_review.html',context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------
def purchase(request):
    


    return redirect('/confirmation.html')
#-----------------------------------------------------------------
#-----------------------------------------------------------------

def order_confirmation(request):
    request.session['total'] = 0
    request.session['cart']=[]
    
    return render(request,'stubhub/confirmation.html')

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def search_results(request):
    search_field = request.session['search_field']
    search_info = request.session['search_info']
    if search_field == 'text':
        selected_events = Event.objects.filter(title__contains=search_info)|Event.objects.filter(venue__name__contains=search_info)|Event.objects.filter(performers__name__contains=search_info)
    elif search_field == 'category':
        category = Category.objects.get(display_tag=search_info)
        category_ref = category.seatgeek_ref
        selected_events = Event.objects.filter(category=category)|Event.objects.filter(category__parent_ref=category_ref)
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

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def process_search(request):
    if request.method == 'POST':
        if len(request.POST['text_search'])>0:
            search_info=request.POST['text_search']
            request.session['search_field']='text'
        elif len(request.POST['event_date'])>0:
            search_info = request.POST['event_date']
            request.session['search_field']= 'date'
        elif len(request.POST['category'])>0:
            search_info = request.POST['category']
            request.session['search_field'] = 'category'
        else:
            return redirect('/')
        request.session['search_info'] = search_info
        return redirect('/search')
    else:
        return redirect('/')


#-----------------------------------------------------------------
#-----------------------------------------------------------------


def show_event(request, parameter):
    
    event = Event.objects.get(id=parameter)

    context = {
        "event": event,
    }

    return render(request, 'stubhub/show_event.html', context)


#-----------------------------------------------------------------
#-----------------------------------------------------------------

def buy_tix(request, parameter):
    
    event = Event.objects.get(id=parameter)
    # Used to exclude tickets the logged in user has posted from the display of available tickets for the event
    try: 
        curr_user_id = request.session['user_id']
    except:
        request.session['nli_event_id'] = parameter
        curr_user_id = -1

    if request.method == "GET":
        available_tix = Ticket.objects.filter(available=True, event=event).exclude(seller=curr_user_id).order_by("seat_letter").order_by("seat_num")

    elif request.method == "POST":
        if request.POST['filter_by'] == "seat":
            available_tix = Ticket.objects.filter(available=True, event=event).order_by("seat_letter").order_by("seat_num")
        elif request.POST['filter_by'] == "price_asc":
            available_tix = Ticket.objects.filter(available=True, event=event).order_by("price")
        elif request.POST['filter_by'] == "price_desc":
            available_tix = Ticket.objects.filter(available=True, event=event).order_by("-price")
        elif request.POST['filter_by'] == "best_value":
            average_price_dict = Ticket.objects.filter(available=True, event=event).aggregate(Avg('price'))
            average_price = average_price_dict['price__avg']
            available_tix = Ticket.objects.filter(available=True, event=event)
            for ticket in available_tix:
                ticket.value = (1/float(ticket.seat_num))/(float(average_price)/float(ticket.price))
            available_tix = sorted(available_tix, key=lambda ticket: ticket.value, reverse=True)

    context = {
        "event": event,
        "available_tix": available_tix,
    }

    return render(request, 'stubhub/buy_tix.html', context)


#-----------------------------------------------------------------
#-----------------------------------------------------------------

def sell_search(request):
    request.session['sell_path'] = True
    categories = Category.objects.order_by('tag')
    context = {
        'categories': categories,
    }
    return render(request, 'stubhub/sell_search.html', context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

