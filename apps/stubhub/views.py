# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect, HttpResponse

from models import User #, Event, Performer, Venue



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
        first_name =  request.POST['first_name']
        last_name =  request.POST['last_name']
        email = request.POST['email']
        hash1 = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
 
        user = User.objects.create(first_name=name, last_name=last_name, email=email, password_hash=hash1)

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
    


    
def log_reg(request):
    return render (request,"stubhub/login.html")

