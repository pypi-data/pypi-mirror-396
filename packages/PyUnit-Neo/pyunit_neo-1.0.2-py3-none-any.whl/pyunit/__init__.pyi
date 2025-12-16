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
    Pixels: TypeAlias = Distance
    Magnitude: TypeAlias = Distance
    Span: TypeAlias = Distance
    Range: TypeAlias = Distance
    Offset: TypeAlias = Distance
    Delta: TypeAlias = Distance
    Width: TypeAlias = Distance
    Height: TypeAlias = Distance
    Depth: TypeAlias = Distance
    Scale: TypeAlias = Distance
    Extent: TypeAlias = Distance
    Bounds: TypeAlias = Distance
    Radius: TypeAlias = Distance
    Diameter: TypeAlias = Distance
    Units: TypeAlias = Distance

    Mass: TypeAlias = Weight
    Load: TypeAlias = Weight

    Rotation: TypeAlias = Angle
    Orientation: TypeAlias = Angle
    Heading: TypeAlias = Angle
    Bearing: TypeAlias = Angle
    Direction: TypeAlias = Angle
    Spin: TypeAlias = Angle
    Turn: TypeAlias = Angle
    Yaw: TypeAlias = Angle
    Pitch: TypeAlias = Angle
    Roll: TypeAlias = Angle

    Points: TypeAlias = Score
    Tally: TypeAlias = Score
    Rating: TypeAlias = Score

    Health: TypeAlias = int
    HP: TypeAlias = Health
    Vitality: TypeAlias = Health
    Life: TypeAlias = Health
    Stamina: TypeAlias = Health

    Currency: TypeAlias = Score
    Coins: TypeAlias = Currency
    Money: TypeAlias = Currency
    Credits: TypeAlias = Currency
    Gems: TypeAlias = Currency
    Tokens: TypeAlias = Currency

    Rank: TypeAlias = Value
    Data: TypeAlias = Value
    Item: TypeAlias = Value

    Duration: TypeAlias = Time
    Interval: TypeAlias = Time
    Elapsed: TypeAlias = Time

    Name: TypeAlias = Text
    Key: TypeAlias = Text
    Id: TypeAlias = Text
    Tag: TypeAlias = Text
__all__ = (
    # Modules
    "UnitMath",

    # Main
    "Unit", "Measurement", "Temperature", "Time", 
    "Distance", "Weight", 
    "Volume", "Angle", "Bytes", "Score", 
    "Value", "RandomValue", "ConstantValue", "Text", "Char", 
    "char_type", "new_char", "to_text", "to_str", "base_unit", 
    "as_base_unit", "is_unit", "not_initialized", "initialized", 
    "extract", "new", "copy", "generate_pi", "generate_e", 
    "generate_root2", "generate_dummy", "pi", "e", 
    "root2", "dummy"

    # Distance aliases
    "Length", "Stretch", "Pixels", "Magnitude", "Span", "Range", 
    "Offset", "Delta", "Width", "Height", "Depth", "Scale", 
    "Extent", "Bounds", "Radius", "Diameter", "Units",

    # Weight aliases
    "Mass", "Load",

    # Angle aliases
    "Rotation", "Orientation", "Heading", "Bearing", "Direction",
    "Spin", "Turn", "Yaw", "Pitch", "Roll",

    # Score / Points aliases
    "Points", "Tally", "Rating",

    # Health aliases
    "Health", "HP", "Vitality", "Life", "Stamina",

    # Currency aliases
    "Currency", "Coins", "Money", "Credits", "Gems", "Tokens",

    # Value aliases
    "Rank", "Data", "Item",

    # Time aliases
    "Duration", "Interval", "Elapsed",

    # Text aliases
    "Name", "Key", "Id", "Tag"
)