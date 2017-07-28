import django
from random import randint
from autofixture import AutoFixture
from apps.stubhub.models import *

def get_rand_price():
    return randint(15,125)

def get_rand_seat_num():
    return randint(1,200)

def get_rand_seat_letter():
    letters = ["A", "B", "C", "D", "E", "F", "G"]
    num = randint(0, 6)
    return letters[num]

fixture = AutoFixture(Ticket, field_values = {
    'price': get_rand_price, 
    'seat_num': get_rand_seat_num,
    'seat_letter': get_rand_seat_letter,
    'buyer': None, 
})

for x in range (0, 500):
    entry = fixture.create(1)