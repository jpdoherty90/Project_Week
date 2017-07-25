import django
from random import randint
from autofixture import AutoFixture
from apps.stubhub.models import *

def get_rand_price():
    return randint(15,125)

def get_rand_seat():
    return randint(1,200)



fixture = AutoFixture(Ticket, field_values = {'price': get_rand_price, 'seat': get_rand_seat, 'buyer':None})
for x in range (0, 5000):
    entry = fixture.create(1)