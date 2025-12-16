"""
This module provides tools for creating and manipulating unit types in a
readable and performant manner. It enables comparisons, arithmetic
operations, and access to trigonometric and geometric utilities.

Properties serve as aliases and are generally not intended
to be explicitly reassigned. In most cases these values are immutable,
ensuring predictable behavior and reducing the potential for unintended
state changes.

The module emphasizes clarity and structure while remaining lightweight.
If your use case requires a more comprehensive unit-handling ecosystem,
consider evaluating external libraries such as `pint`. This module focuses
on fundamental, understandable abstractions without introducing
unnecessary complexity.

Compatibility
-------------
Operating Systems:
    - Windows

Python Versions:
    - Python 3.10 and above

Although we do not enforce hard constraints, we strongly recommend
following these guidelines. Your feedback and reports help us maintain
compatibility across systems. To contribute or read more, see:
[https://github.com/NeoZett-School/PyUnit]

We welcome community contributions to this project.

Copyright (c) 2025–2026 Neo Zetterberg
"""
from ._internal import (
    Unit, Measurement, Temperature, Time, 
    Distance, Weight, Volume, Angle, Bytes, 
    Score, Value, RandomValue, ConstantValue, Text, 
    Char, char_type, new_char, to_text, to_str, as_base_unit, 
    base_unit, is_unit, not_initialized, initialized, extract, 
    new, copy, generate_pi, generate_e, generate_root2, 
    generate_dummy, pi, e, root2, dummy
)
from . import math as UnitMath
Length = Distance
Stretch = Distance
Mass = Weight
Rotation = Angle
Points = Score

import os, sys
from ._about import __name__, __version__, __author__, __link__

# NOTE: We have barely tested this package yet.
MIN_VERSION = (3, 10)
COMPATABILITY = ("nt",)

class Status:
    name = "Unstable"
    compatible = False
    sys_version = tuple(sys.version_info)[:2]
    os_name = os.name
    info = "Welcome to PyUnit. This package was provided by {} and many others. "\
    "Please follow us on github: {}\nPyUnit Version {}, Python {}"
    @classmethod
    def update(cls):
        cls.compatible = cls.check_version() and cls.check_os()
        cls.name = "Stable" if cls.compatible else "Unstable"
    @classmethod
    def welcome(cls):
        cls.update()
        return cls.info.format(
            __author__, 
            __link__, 
            __version__, 
            sys.version
        )
    @staticmethod
    def check_version():
        return Status.sys_version >= MIN_VERSION
    @staticmethod
    def check_os():
        return Status.os_name in COMPATABILITY

print(Status.welcome())
if not Status.compatible:
    print("Warning: Some features may be buggy or glitchy, consider upgrading your python environment.")

#if Status.sys_version >= (0, 0): ... # We may do version/platform specific improvements here