# salutator/greetings.py

class Greeter:
    def __init__(self, name: str):
        self.name = name

    def salute(self):
        print(f"Hello, {self.name}! Hope you have a wonderful day!")

