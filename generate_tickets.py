import django
from random import randint
from autofixture import AutoFixture

def getRandomPrice():
    return randint(15,125)

def getRandomSeatLetter():
    letters = ["A", "B", "C", "D", "E", "F", "G"]
    num = randint(0, 6)
    return letters[num]

def getRandomSeatNumber():
    num = randint(1,200)
    return str(num)

fixture = AutoFixture(Ticket, field_values = {
    'price': getRandomPrice(), 
    'seat': getRandomSeatLetter() + getRandomSeatNumber(),
    'buyer': None, 
})

for x in range (0, 500):
    entry = fixture.create(1)