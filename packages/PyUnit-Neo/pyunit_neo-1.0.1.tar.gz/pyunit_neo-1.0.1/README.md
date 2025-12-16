# PyUnit

**PyUnit** is a lightweight Python library for creating, manipulating, and comparing units in a readable and performant way.  
It provides trigonometric, geometric, and arithmetic utilities, enabling clean and understandable code for unit-based calculations.

---

## Features

- Create unit types like `Distance`, `Weight`, `Angle`, `Time`, `Temperature`, etc.
- Perform arithmetic operations and comparisons on units.
- Access trigonometric and geometric functions for calculations.
- Lightweight and readable syntax without heavy dependencies.
- Supports Python 3.10+ on Windows.

---

## Installation

```bash
pip install PyUnit
```
*(Note: This package is currently in early development. Some features may be unstable.)*

---

## Usage Example

```python
from pyunit import Distance, Angle, Char, new_char

# Create a distance unit
d1 = Distance(10)
d2 = Distance(5)

# Perform arithmetic
total = d1 + d2

# Create a character
a = new_char("A")  # type: Char["A"]

# Angle calculation
from pyunit import UnitMath as um
angle = um.alpha(3, 4)  # returns angle in radians
```

---

## Licence

This project is licensed under the **MIT License** – see the [LICENCE](./LICENSE) file for details.

---

## Contributing

Contributions, bug reports, and feature requests are welcome!
Visit the repository: [PyUnit on GitHub](https://github.com/NeoZett-School/PyUnit)