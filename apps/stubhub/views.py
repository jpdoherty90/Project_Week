# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse

from models import User, Ticket #, Event, Performer, Venue

import re

import bcrypt




#-----------------------------------------------------------------
#-----------------------------------------------------------------


def index(request):

    context = {
        "test": "test",
    }

  
    return render(request, 'stubhub/home.html', context)


#-----------------------------------------------------------------
#-----------------------------------------------------------------

def register(request):
    
    errors = User.objects.new_user_validator(request.POST)
    if len(errors):
        for tag, error in errors.iteritems():
            messages.add_message(request, messages.ERROR, errors[tag])
        return redirect("/")
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
            return redirect('/success')

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def success(request):
    
    user = User.objects.get(id=request.session['user_id'])

    context = {

    }
    
    return render(request, 'stubhub/home.html', context)
    

#-----------------------------------------------------------------
#-----------------------------------------------------------------

def login(request):

    try:
        user = User.objects.login_validator(request.POST)
        request.session['name'] = user.name
        request.session['email'] = user.email
        request.session['user_id'] = user.id
        return redirect('/success')
    except:
        messages.add_message(request, messages.ERROR, "Invalid login info.")
        return redirect("/")

#-----------------------------------------------------------------
#----------------------------------------------------------------

def logout(request):
    for sesskey in request.session.keys():
        del request.session[sesskey]
    return redirect("/")

#-----------------------------------------------------------------
#-----------------------------------------------------------------



def post_tickets(request):

    event = request.POST['event']
    seller_id = request.POST['event']
    seat = request.POST['seat']
    price = request.POST['price']

    #new_ticket = 
    

#-----------------------------------------------------------------
#-----------------------------------------------------------------

    
def log_reg(request):
    return render (request,"stubhub/login.html")

