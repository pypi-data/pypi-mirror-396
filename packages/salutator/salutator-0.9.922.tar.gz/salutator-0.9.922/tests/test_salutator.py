# tests/test_salutator.py

from salutator.greetings import Greeter
from salutator.goodbyes import GoodByer

def test_greeter():
    g = Greeter(name='John')
    g.salute()  # prints greeting

def test_goodbyer():
    gb = GoodByer(name='Diane')
    gb.salute()  # prints goodbye

