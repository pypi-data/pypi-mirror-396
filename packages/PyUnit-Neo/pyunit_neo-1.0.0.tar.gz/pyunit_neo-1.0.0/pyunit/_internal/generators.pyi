from .core import MathematicalValue, DummyUnit

__all__ = (
    # Generators
    "generate_pi", 
    "generate_e", 
    "generate_root2",
    "generate_dummy",

    # Defaults
    "pi",
    "e",
    "root2",
    "dummy"
)

# Generators
def generate_pi() -> MathematicalValue: ...
def generate_e() -> MathematicalValue: ...
def generate_root2() -> MathematicalValue: ...
def generate_dummy() -> DummyUnit: ...

# Defaults
pi: MathematicalValue
e: MathematicalValue
root2: MathematicalValue
dummy: DummyUnit