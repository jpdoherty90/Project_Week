# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse


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
        return redirect ('/')

#-----------------------------------------------------------------
#----------------------------------------------------------------

def log_out(request):
    request.session.clear()
    return redirect("/")

#-----------------------------------------------------------------
#-----------------------------------------------------------------


def init_sale(request, parameter):
    
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
        
        seat_num = "seat_" + str(i+1) 
        seat = request.POST[seat_num]

        Ticket.objects.create(event=event, seller=seller, seat=seat, price=price)

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

def acc_info(request):
    context = { 'user': User.objects.get(id=request.session['user_id']),
                'bought_tickets': Ticket.objects.filter(buyer_id=request.session['user_id'])
    }
    
    return render (request,"stubhub/acc_info.html",context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def sell_tickets(request):
    context = { 'user': User.objects.get(id=request.session['user_id'])
    }

    return render (request,"stubhub/sell_tickets.html",context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def cart(request):
    item_ids = request.session['cart']
    items = []
    total=0
    for item_id in item_ids:
        ticket=Ticket.objects.get(id=item_id)
        items.append(ticket)
    for ticket in items:
        total+=int(ticket.price)
    
    print total
    context = { 'user': User.objects.get(id=request.session['user_id']),
                'items': items,
                'total':total,
    }
    

    return render (request,"stubhub/cart.html",context)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def add_to_cart(request):
    print'added to cart'
    request.session.modified = True
    ticket_id= request.POST['ticket_id']
    ticket= Ticket.objects.get(id=ticket_id)
    request.session['cart'].append(ticket_id)

    print request.session['cart']
    x="/"+str(ticket.event.id)
    
    return redirect('/buy'+ x)

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def purchase(request):
    
    return redirect('/confrimation')
#-----------------------------------------------------------------
#-----------------------------------------------------------------

def confirmation(request):
    
    return render(request,'stubhub/confrimation')

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def search_results(request):
    search_field = request.session['search_field']
    search_info = request.session['search_info']
    print '*'*50
    print search_field
    print search_info
    print '*'*50
    if search_field == 'text':
        selected_events = Event.objects.filter(title__contains=search_info)|Event.objects.filter(venue__name__contains=search_info)|Event.objects.filter(performers__name__contains=search_info)
    elif search_field == 'category':
        selected_events = Event.objects.filter(category__tag=search_info)
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

    if request.method == "GET":
        available_tix = Ticket.objects.filter(available=True, event=event).order_by("seat")

    elif request.method == "POST":
        if request.POST['filter_by'] == "seat":
            available_tix = Ticket.objects.filter(available=True, event=event).order_by("seat")
        elif request.POST['filter_by'] == "price_asc":
            available_tix = Ticket.objects.filter(available=True, event=event).order_by("price")
        elif request.POST['filter_by'] == "price_desc":
            available_tix = Ticket.objects.filter(available=True, event=event).order_by("-price")
        elif request.POST['filter_by'] == "best_value":
            available_tix = Ticket.objects.filter(available=True, event=event).order_by("price")


    context = {
        "event": event,
        "available_tix": available_tix,
    }

    return render(request, 'stubhub/buy_tix.html', context)


#-----------------------------------------------------------------
#-----------------------------------------------------------------

