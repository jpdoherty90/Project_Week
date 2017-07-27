# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import bcrypt
import re

# Regex models:
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^[a-zA-Z]+$')

class UserManager(models.Manager):
    # Validations for a registration
    def new_user_validator(self, post_data):
        errors = {}
        # See if the e-mail address is already registered - Prompt them to log-in
        try:
            User.objects.get(email = post_data['email'])
            errors['already_user'] = 'Looks like you already have an account.  Try logging in!'
        except:
            pass
        # Check name length
        if len(post_data['first_name']) < 1 or len(post_data['last_name']) < 1:
            errors['name_length'] = 'Names must both be at least 3 characters'    
        # Check e-mail format
        if not EMAIL_REGEX.match(post_data['email']):
            errors['invalid_email'] = 'Email address is invalid'
            return errors
        # Check password length
        if len(post_data['password']) < 8:
            errors['password_length'] = 'Password should be at least 8 characters'
        # Check password against password confirm
        if post_data['password'] != post_data['confirm']:
            errors['password_match'] = 'Passwords do not match'
        return errors

    def login_validator(self, post_data):
        errors = {}
        # See if the e-mail address is already registered - If not, prompt them to create an account
        try:
            print 'email check'
            user = User.objects.get(email=post_data['email'])
            print 'email not found'
        except:
            errors['user_not_registered'] = "Sorry, we can't find that e-mail in our system.  Please create an account."
            return errors
        entered_pw = post_data['password']
        user_hash = user.password_hash
        # Authenticate the password
        if not bcrypt.checkpw(entered_pw.encode(), user_hash.encode()):
            errors['incorrect_password'] = 'Password incorrect.  Please try again!'
        return errors


class TicketManager(models.Manager):
    def post_ticket_validator(self, postData):
        errors = { }
        return errors

class User(models.Model):
    first_name = models.CharField(max_length = 128)
    last_name = models.CharField(max_length = 128)
    email = models.CharField(max_length = 256, unique=True)
    password_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

class Venue(models.Model):
    name = models.CharField(max_length = 256)
    address = models.CharField(max_length = 256)
    extended_address = models.CharField(max_length = 256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Performer(models.Model):
    name = models.CharField(max_length = 256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Category(models.Model):
    tag = models.CharField(max_length = 64)
    display_tag = models.CharField(max_length = 64)
    seatgeek_ref = models.IntegerField(blank=True, null=True)
    parent_ref = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Event(models.Model):
    title = models.CharField(max_length = 256)
    short_title = models.CharField(max_length = 256)
    event_date_time = models.DateTimeField()
    visible_until = models.DateTimeField(default='0000-00-00 00:00[:00[.000000]][PM]')
    popularity_score = models.FloatField()
    image = models.CharField(max_length = 512, blank=True, null=True)
    venue = models.ForeignKey(Venue, related_name='events')
    performers = models.ManyToManyField(Performer, related_name='events')
    category = models.ForeignKey(Category, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Ticket(models.Model):
    event = models.ForeignKey(Event, related_name="tickets")
    seller = models.ForeignKey(User, related_name="sellers")
    buyer = models.ForeignKey(User, related_name="buyers", blank=True, null=True)
    available = models.BooleanField(default=True)
    seat_num = models.IntegerField(default=0)
    seat_letter = models.CharField(max_length=4)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = TicketManager()

class Purchase(models.Model):
    shopper = models.ForeignKey(User, related_name="shopper")
    items = models.ForeignKey(Ticket,related_name="items")
    payment= models.CharField(max_length = 256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    


    
