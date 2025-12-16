"""As we gain generators, they will all gather here."""

from .core import Unit, Value
import math

# Generators
def generate_pi():
    """Return a value of pi."""
    return Value(math.pi)

def generate_e():
    """Return a value of e."""
    return Value(math.e)

def generate_root2():
    """Return a value of the root of 2."""
    return Value(math.sqrt(2))

def generate_dummy():
    """The dummy comes practical for a unit without no value."""
    return Unit()

# Defaults
pi = generate_pi()
e = generate_e()
root2 = generate_root2()
dummy = generate_dummy()