from typing import TYPE_CHECKING, TypeAlias
from ._internal import (
    Unit, Measurement, Temperature, Time, 
    Distance, Weight, Volume, Angle, Bytes, 
    Score, Value, RandomValue, ConstantValue, Text, 
    Char, char_type, new_char, to_text, to_str, base_unit, 
    as_base_unit, is_unit, not_initialized, initialized, 
    extract, new, copy, generate_pi, generate_e, generate_root2, 
    generate_dummy, pi, e, root2, dummy
)
from . import math as UnitMath
if TYPE_CHECKING: # We specify. If we don't type-check, then it is best to use the default type checking.
    Length: TypeAlias = Distance
    Stretch: TypeAlias = Distance
    Mass: TypeAlias = Weight
    Rotation: TypeAlias = Angle
    Points: TypeAlias = Score
__all__ = (
    # Modules
    "UnitMath",

    # Main
    "Unit", "Measurement", "Temperature", "Time", 
    "Distance", "Length", "Stretch", "Weight", "Mass", 
    "Volume", "Angle", "Rotation", "Bytes", "Score", "Points", 
    "Value", "RandomValue", "ConstantValue", "Text", "Char", 
    "char_type", "new_char", "to_text", "to_str", "base_unit", 
    "as_base_unit", "is_unit", "not_initialized", "initialized", 
    "extract", "new", "copy", "generate_pi", "generate_e", 
    "generate_root2", "generate_dummy", "pi", "e", 
    "root2", "dummy"
)