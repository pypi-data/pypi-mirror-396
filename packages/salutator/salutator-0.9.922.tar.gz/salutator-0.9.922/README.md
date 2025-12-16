# Salutator

A small Python package for greetings and goodbyes.

## Installation

```bash

pip install salutator

```

## Example Usage

```python
from salutator import humans as h
from salutator import animals as a
from salutator import plants as p
from salutator import minerals as m


# Humans

hg = h.Greeter("John")
print(hg.name)   # John
hg.salute()      # Hello, John! Wishing you a fantastic day ahead!

hb = h.GoodByer("Penelope")
hb.salute()      # Goodbye, Penelope! Take care and see you soon!


# Animals

ag = a.Greeter("Fido")
ag.salute()      # Fido wags its tail excitedly in greeting!

ab = a.GoodByer("Whiskers")
ab.salute()      # Whiskers trots away happily with a final bark of farewell!


# Plants

pg = p.Greeter("Oak Tree")
pg.salute()      # The Oak Tree rustles its leaves softly in greeting.

pb = p.GoodByer("Pine")
pb.salute()      # The Pine sways gently as a goodbye in the breeze.


# Minerals

mg = m.Greeter("Quartz")
mg.salute()      # The Quartz gleams brightly under the light as if to say hello.

mb = m.GoodByer("Obsidian")
mb.salute()      # The Obsidian fades quietly into the shadows, bidding farewell.
```

