from typing import Generic, TypeVar, Literal
import random
import math

from .arithmetics import Arithmetics

# Fix generic classes
T = TypeVar("T", bound="Unit", default="Unit")
T3 = TypeVar("T3", bound=str)

class UninitializedUnit(Generic[T]):
    """When the unit isn't initialized."""

    def __init__(self, unit):
        self._unit = unit
    
    @property
    def unit(self):
        return self._unit
    
    def extract(self):
        """Extract the unit from the uninitialized unit."""
        return self._unit

class Unit(Arithmetics):
    """A unit is any core unit."""

    def __init__(self, *args, **kwargs): 
        # The unit itself will not have any value, although takes one parameter. 
        # To initalize this would come practical for simple type checking. 
        # Then this becomes more as a state dummy.
        pass

    @classmethod
    def new(cls, unit = None, *args, **kwargs):
        """Create a new unit of the given type."""
        unit = unit if unit else Unit
        return unit(*args, **kwargs)
    
    def configure(self, name, measurement):
        """
        Configure a measurement descriptor on this unit's *class*.

        `measurement` may be either a Measurement subclass (type) or an already-
        instantiated descriptor. Examples:

            time = Time()
            time.configure("minutes", Minutes)          # pass class
            time.configure("minutes", Minutes())        # pass instance

        This will set the descriptor on the class so it works for all instances,
        and also calls __set_name__ so the descriptor can compute a backing name.
        """
        # allow passing the descriptor class or an instance
        desc = measurement() if isinstance(measurement, type) else measurement

        cls = self.__class__

        # Remove any existing attribute on the class (not on the instance)
        if hasattr(cls, name):
            try:
                delattr(cls, name)
            except Exception:
                # in weird cases we still try to overwrite
                pass

        # Attach descriptor to the class
        setattr(cls, name, desc)

        # If descriptor implements __set_name__, call it so it can compute a backing slot.
        # __set_name__ signature is (owner, name)
        if hasattr(desc, "__set_name__"):
            # call explicitly because Python only does that automatically at class creation
            desc.__set_name__(cls, name)
    
    def copy(self):
        """Copy this unit exactly."""
        value = base_unit(self)
        return Unit.new(self.__class__, value)
    
    # Abstractions
    def base_unit(self): # For clear internals, we use the global base_unit directly.
        """This is an abstraction of the `base_unit` function directly in the unit itself."""
        return base_unit(self)
    
    def to_text(self):
        """This is an abstraction of the `to_text` function directly in the unit itself."""
        return to_text(self)
    
    def to_str(self):
        """This is an abstraction of the `to_str` function directly in the unit itself."""
        return to_str(self)
    
    def lock(self):
        """When you lock a unit, you will only be able to access the base unit when trying to access this from a class."""
        self._locked = True
    
    def __set_name__(self, owner, name):
        self._name = name
    
    def __get__(self, instance, owner):
        """Retrieve the unit, the float if locked, or the uninitialized unit if 
        the class where it resides isn't initialized. If it is uninitialized, you 
        should extract the unit from that uninitialized unit."""
        if instance is None:
            return UninitializedUnit(self)
        if getattr(self, "_locked", False):
            return self.__float__()
        return self
    
    def __set__(self, instance, value):
        if getattr(self, "_locked", False) or not getattr(self, "_name", False):
            raise RuntimeError("You cannot set this unit.")
        instance.__dict__[self._name] = value
    
    def __int__(self):
        return 0
    
    def __float__(self):
        return 0.0
    
    def __str__(self):
        return ""
    
    def __repr__(self):
        return f"<Unit {self.__class__.__name__}(base_value={self.__str__()})>"

class Measurement:
    """Create your own descriptor. Define backing and factor.
    The real value is divided by the factor."""
    backing = "_value"
    factor = 1

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = getattr(instance, self.backing)
        return value / self.factor

    def __set__(self, instance, value):
        instance.__dict__[self.backing] = float(value) * self.factor

    def __delete__(self, instance):
        instance.__dict__.pop(self.backing, None)

class Celsius(Measurement):
    """Descriptor that read/write celsius and save the value in a separate
    fahrenheit-backing-attribute at the instanse."""
    backing = "_fahrenheit"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        f = getattr(instance, self.backing)
        return 5 * (f - 32) / 9

    def __set__(self, instance, value):
        instance.__dict__[self.backing] = 32 + 9 * float(value) / 5

class Temperature(Unit):
    """Temperature provides features for temperature arithmetics."""
    celsius = Celsius()

    def __init__(self, value = 0.0, *, unit = "F"):
        """
        Create a new temperature.
        :param value: temperature value
        :param unit: "F" for Fahrenheit (standard), "C" for Celsius
        """
        if unit.upper() == "F":
            self._fahrenheit = float(value)
        elif unit.upper() == "C":
            # Använd descriptorens __set__ för att sätta celsius
            self.celsius = float(value)
        else:
            raise ValueError("Unit must be 'F' or 'C'")
    
    @classmethod
    def new(cls, value):
        return Unit.new(Temperature, value)
    
    @property
    def c(self):
        return self.celsius
    
    @property
    def f(self):
        return self.fahrenheit

    @property
    def fahrenheit(self):
        return self._fahrenheit

    @fahrenheit.setter
    def fahrenheit(self, value):
        self._fahrenheit = float(value)
    
    def __int__(self):
        return int(self._fahrenheit)
    
    def __float__(self):
        return float(self._fahrenheit)
    
    def __str__(self):
        return str(self._fahrenheit)

class TimeMeasurement(Measurement):
    """Generic descriptor for time units. 'factor' is the apparent seconds per unit.
    Example: Minutes.factor = 60 (1 minute == 60 seconds).
    For nanoseconds we use factor = 1e-9 (1 ns == 1e-9 s)."""
    backing = "_seconds"
    factor = 1.0

class Nanoseconds(TimeMeasurement):
    factor = 1e-9

class Microseconds(TimeMeasurement):
    factor = 1e-6

class Milliseconds(TimeMeasurement):
    factor = 1e-3

class Minutes(TimeMeasurement):
    factor = 60.0

class Hours(TimeMeasurement):
    factor = 3600.0

class Days(TimeMeasurement):
    factor = 86400.0

class Time(Unit):
    """Time provide features for calculating time arithmetics."""

    nanoseconds = Nanoseconds()
    microseconds = Microseconds()
    milliseconds = Milliseconds()
    minutes = Minutes()
    hours = Hours()
    days = Days()

    def __init__(self, seconds = 0.0):
        self._seconds = float(seconds)
    
    @classmethod
    def new(cls, seconds):
        return Unit.new(Time, seconds)
    
    @property
    def ns(self):
        return self.nanoseconds
    
    @property
    def ms(self):
        return self.milliseconds
    
    @property
    def s(self):
        return self.seconds

    @property
    def seconds(self):
        return self._seconds

    @seconds.setter
    def seconds(self, value):
        self._seconds = float(value)
    
    def __int__(self):
        return int(self._seconds)
    
    def __float__(self):
        return float(self._seconds)
    
    def __str__(self):
        return str(self._seconds)

class LengthMeasurement(Measurement):
    """Generic descriptor for length units. 'factor' is the apparent meters per unit."""
    backing = "_meters"
    factor = 1.0

class Millimeters(LengthMeasurement):
    factor = 1E-3

class Centimeters(LengthMeasurement):
    factor = 1E-2

class Decimeters(LengthMeasurement):
    factor = 1E-1

class Kilometers(LengthMeasurement):
    factor = 1000.0

class Distance(Unit):
    """Distance provide features for calculating distance arithmetics."""

    millimeters = Millimeters()
    centimeters = Centimeters()
    decimeters = Decimeters()
    kilometers = Kilometers()

    def __init__(self, meters = 0.0):
        self._meters = float(meters)
    
    @classmethod
    def new(cls, meters):
        return Unit.new(Distance, meters)
    
    @property
    def mm(self):
        return self.millimeters
    
    @property
    def cm(self):
        return self.centimeters
    
    @property
    def dm(self):
        return self.decimeters
    
    @property
    def km(self):
        return self.kilometers
    
    @property
    def m(self):
        return self.meters

    @property
    def meters(self):
        return self._meters

    @meters.setter
    def meters(self, value):
        self._meters = float(value)
    
    def __int__(self):
        return int(self._meters)
    
    def __float__(self):
        return float(self._meters)
    
    def __str__(self):
        return str(self._meters)

class MassMeasurement(Measurement):
    """Generic descriptor for weight units. 'factor' is the apparent grams per unit."""
    backing = "_grams"
    factor = 1.0

class Milligrams(MassMeasurement):
    factor = 1E-3

class Centigrams(MassMeasurement):
    factor = 1E-2

class Decigrams(MassMeasurement):
    factor = 1E-1

class Kilograms(MassMeasurement):
    factor = 1000.0

class Weight(Unit):
    """Weight provide features for calculating weight arithmetics."""

    milligrams = Milligrams()
    centigrams = Centigrams()
    decigrams = Decigrams()
    kilograms = Kilograms()

    def __init__(self, grams = 0.0):
        self._grams = float(grams)
    
    @classmethod
    def new(cls, grams):
        return Unit.new(Weight, grams)
    
    @property
    def mg(self):
        return self.milligrams
    
    @property
    def cg(self):
        return self.centigrams
    
    @property
    def dg(self):
        return self.decigrams
    
    @property
    def kg(self):
        return self.kilograms
    
    @property
    def g(self):
        return self.grams

    @property
    def grams(self):
        return self._grams

    @grams.setter
    def grams(self, value):
        self._grams = float(value)
    
    def __int__(self):
        return int(self._grams)
    
    def __float__(self):
        return float(self._grams)
    
    def __str__(self):
        return str(self._grams)

class VolumeMeasurement(Measurement):
    """Generic descriptor for weight units. 'factor' is the apparent grams per unit."""
    backing = "_liters"
    factor = 1.0

class Milliliters(VolumeMeasurement):
    factor = 1E-3

class Centiliters(VolumeMeasurement):
    factor = 1E-2

class Deciliters(VolumeMeasurement):
    factor = 1E-1

class Kiloliters(VolumeMeasurement):
    factor = 1000.0

class Volume(Unit):
    """Volume provide features for calculating volume arithmetics."""

    milliliters = Milliliters()
    centiliters = Centiliters()
    deciliters = Deciliters()
    kiloliters = Kiloliters()

    def __init__(self, liters = 0.0):
        self._liters = float(liters)
    
    @classmethod
    def new(cls, liters):
        return Unit.new(Volume, liters)
    
    @property
    def ml(self):
        return self.milliliters
    
    @property
    def cl(self):
        return self.centiliters
    
    @property
    def dl(self):
        return self.deciliters
    
    @property
    def kl(self):
        return self.kiloliters
    
    @property
    def l(self):
        return self.liters

    @property
    def liters(self):
        return self._liters

    @liters.setter
    def liters(self, value):
        self._liters = float(value)
    
    def __int__(self):
        return int(self._liters)
    
    def __float__(self):
        return float(self._liters)
    
    def __str__(self):
        return str(self._liters)

class AngleMeasurement(Measurement):
    """Generic descriptor for angle units. 'factor' is the apparent degrees per unit."""
    backing = "_degrees"
    factor = 1.0

class Radians(AngleMeasurement):
    factor = 180 / math.pi

class Gradians(AngleMeasurement):
    factor = 0.9

class Angle(Unit):
    """Angle provide features for calculating angle arithmetics."""

    radians = Radians()
    gradians = Gradians()

    def __init__(self, degrees = 0.0):
        self._degrees = float(degrees)
    
    @classmethod
    def new(cls, degrees):
        return Unit.new(Angle, degrees)
    
    def sin(self):
        return math.sin(self.radians)
    
    def cos(self):
        return math.cos(self.radians)
    
    def tan(self):
        return math.tan(self.radians)
    
    def sinh(self):
        return math.sinh(self.radians)
    
    def cosh(self):
        return math.cosh(self.radians)
    
    def tanh(self):
        return math.tanh(self.radians)

    @property
    def degrees(self):
        return self._degrees

    @degrees.setter
    def degrees(self, value):
        self._degrees = float(value)
    
    def __int__(self):
        return int(self._degrees)
    
    def __float__(self):
        return float(self._degrees)
    
    def __str__(self):
        return str(self._degrees)

class StorageMeasurement(Measurement):
    """Generic descriptor for storage units. 'factor' is the apparent bits per unit."""
    backing = "_bytes"
    factor = 1.0

class Kilobytes(StorageMeasurement):
    factor = 1000.0

class Megabytes(StorageMeasurement):
    factor = 1000.0**2

class Gigabytes(StorageMeasurement):
    factor = 1000.0**3

class Terabytes(StorageMeasurement):
    factor = 1000.0**4

class Petabytes(StorageMeasurement):
    factor = 1000.0**5

class Exabytes(StorageMeasurement):
    factor = 1000.0**6

class Zettabytes(StorageMeasurement):
    factor = 1000.0**7

class Yottabytes(StorageMeasurement):
    factor = 1000.0**8

class Ronnabytes(StorageMeasurement):
    factor = 1000.0**9

class QuettaBytes(StorageMeasurement):
    factor = 1000.0**10

class Bytes(Unit):
    """Bytes provide features for calculating bytes arithmetics. (SI, not bytes, by default. See `Unit.configure`)"""

    kilobytes = Kilobytes()
    megabytes = Megabytes()
    gigabytes = Gigabytes()
    terabytes = Terabytes()
    petabytes = Petabytes()
    exabytes = Exabytes()
    zettabytes = Zettabytes()
    yottabytes = Yottabytes()
    ronnabytes = Ronnabytes()
    quettabytes = QuettaBytes()

    def __init__(self, bytes = 0.0):
        self._bytes = float(bytes)
    
    @classmethod
    def new(self, bytes):
        return Unit.new(Bytes, bytes)
    
    @property
    def kb(self):
        return self.kilobytes
    
    @property
    def mb(self):
        return self.megabytes
    
    @property
    def gb(self):
        return self.gigabytes
    
    @property
    def tb(self):
        return self.terabytes
    
    @property
    def pb(self):
        return self.petabytes
    
    @property
    def eb(self):
        return self.exabytes
    
    @property
    def zb(self):
        return self.zettabytes
    
    @property
    def yb(self):
        return self.yottabytes
    
    @property
    def rb(self):
        return self.ronnabytes
    
    @property
    def qb(self):
        return self.quettabytes
    
    @property
    def b(self):
        return self.bytes

    @property
    def bytes(self):
        return self._bytes

    @bytes.setter
    def bytes(self, value):
        self._bytes = float(value)
    
    def __int__(self):
        return int(self._bytes)
    
    def __float__(self):
        return float(self._bytes)

    def __str__(self):
        return str(self._bytes)

class Score(Unit):
    """Score provide features for calculating score arithmetics."""

    def __init__(self, score = 0.0):
        self._score = float(score)
    
    @classmethod
    def new(self, score):
        return Unit.new(Score, score)
    
    @property
    def points(self):
        """Points can be set, in difference to other aliases."""
        return self.score
    
    @points.setter
    def points(self, value):
        self.score = value
    
    @property
    def score(self):
        return float(self._score)
    
    @score.setter
    def score(self, value):
        self._score = float(value)
    
    def __int__(self):
        return int(self._score)
    
    def __float__(self):
        return float(self._score)

    def __str__(self):
        return str(self._score)

class Value(Unit):
    """A normal value."""

    def __init__(self, value):
        self._value = value
    
    @classmethod
    def new(self, value):
        return Unit.new(Value, value)
    
    @property
    def value(self):
        return float(self._value)
    
    @value.setter
    def value(self, value):
        self._value = float(value)
    
    def exp(self):
        return math.exp(self._value)
    
    def exp2(self):
        return math.exp2(self._value)
    
    def sqrt(self):
        return math.sqrt(self._value)
    
    def __int__(self):
        return int(self._value)
    
    def __float__(self):
        return float(self._value)

    def __str__(self):
        return str(self._value)

class RandomValue(Value):
    """A random value."""

    def __init__(self, a, b, seed = None):
        self._a, self._b = a, b
        self._random = random.Random(seed)
    
    @classmethod
    def new(self, a, b, seed = None):
        return Unit.new(RandomValue, a, b, seed)
    
    @property
    def value(self):
        return self.generate()
    
    def generate(self):
        """Generate a new value."""
        return min(self._a, self._b) + abs(self._a - self._b) * self._random.random()
    
    def to_int(self):
        """Use this for whole integers."""
        return self.__int__()
    
    def __int__(self):
        return int(self.value)
    
    def __float__(self):
        return float(self.value)

    def __str__(self):
        return str(self.value)

class ConstantValue(Value):
    """A constant value will never change."""

    _constant = True # Tell the arithmetic system that this is a constant
    
    @classmethod
    def new(self, value):
        return Unit.new(ConstantValue, value)
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        raise AttributeError("A constant value cannot be changed.")

class Text: # Easy to use and extend. Very low implementation, but practical when you want to extend.
    """The text is a string wrapper that provides basic utilities for units, saving, loading and comprehension."""
    def __init__(self, text = "", encoding = "utf-8"):
        self._text = str(text)
        self._encoding = encoding
    
    def set_encoding(self, encoding = "utf-8"):
        self._encoding = encoding
    
    def open_path(self, mode, *args, **kwargs):
        """Performs the normal `open` command on a file with the text as file path.
        Parse args and kwargs to open."""
        return open(self.text, mode, *args, **kwargs)
    
    def save(self, file_path):
        with open(file_path, "w") as f:
            f.write(self._text)
        
    def load(self, file_path):
        with open(file_path, "r") as f:
            self._text = f.read()
    
    @property
    def length(self):
        return len(self._text)
    
    @property
    def bytes(self):
        return self._text.encode(encoding=self._encoding)
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = str(value)
    
    def __str__(self):
        return str(self._text)
    
    def __eq__(self, other):
        if isinstance(other, Text):
            return self._text == other._text
        elif isinstance(other, str):
            return self._text == other
        else:
            return False

class Char(Text, Generic[T3]):
    """The text is a string wrapper that provides basic utilities for units, saving, loading and comprehension. 
    A `Char` must be exactly one unit long."""
    def __init__(self, text = "", encoding = "utf-8"):
        """At runtime `Char("A")` constructs a Char whose `.text == "A"`.  At typing time
        you can use `Char[Literal["A"]]` to refer to the type `Char` specialized to
        the literal "A"."""
        super().__init__(text, encoding)
        self._check()
    
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)
        self._check()

    def _check(self):
        if len(self._text) != 1:
            raise RuntimeError("A 'Char' must contain exactly one singular letter.")

class NotUnitError(TypeError):
    """Error whenever an supposed unit is opposed."""

def char_type(lit):
    """Create a char like `Char[Literal[lit]]`, manifactured. 
    The returned type will take no arguments, and return as `Char[Literal[lit]](lit)`. 
    This disables changing the character, making it a constant."""
    T = Literal[lit]
    class C(Char[T]):   # type: ignore
        def __init__(self):
            super().__init__(lit)
        @property
        def text(self):
            return self._text
        @text.setter
        def text(self, value):
            raise AttributeError("You cannot set this attribute. It is a constant.")
    C.__name__ = f"Char_{lit}"
    return C

def new_char(char):
    """Create this char with proper typing. This disables you from ever changing the character, now a constant."""
    create = char_type(char)
    return create()

def to_text(unit):
    """Get a text wrapper with that unit."""
    unit = extract(unit)
    if not isinstance(unit, Unit):
        raise NotUnitError("You must provide a unit to get a text wrapper.")
    return Text(unit)

def to_str(unit):
    """Get a string representation. You may also provide a text object."""
    unit = extract(unit)
    if not isinstance(unit, (Unit, Text)):
        raise NotUnitError("You must provide a unit or text to get the string representation.")
    return unit.__str__()

def base_unit(unit):
    """Get the base value of that unit."""
    unit = extract(unit)
    if not isinstance(unit, Unit):
        raise NotUnitError("You must provide a unit to get base value.")
    return unit.__float__()

def as_base_unit(unit_or_base):
    """Ensure the given unit or base is a base value."""
    # We cannot extract, in case it is a value
    if isinstance(unit_or_base, (Unit, UninitializedUnit)):
        unit_or_base = base_unit(unit_or_base)
    return unit_or_base

def is_unit(unit):
    """Get if whether the given unit is an actual unit."""
    unit = extract(unit)
    return issubclass(unit, Unit) if isinstance(unit, type) else isinstance(unit, Unit)

def not_initialized(unit):
    """Returns whether the unit isn't initialized yet. 
    That is if the class that it resides in is initialized yet."""
    return isinstance(unit, UninitializedUnit)

def initialized(unit):
    """Returns whether the unit is initialized yet. 
    That is if the class that it resides in is initialized yet."""
    return not not_initialized(unit)

def extract(unit):
    """If the unit is uninitialized, it ensures the unit is extracted."""
    if not_initialized(unit):
        return unit.extract()
    return unit

def new(unit, *args, **kwargs):
    return Unit.new(unit, *args, **kwargs)

def copy(unit):
    """Copy any unit."""
    # Make a copy of that unit
    unit = extract(unit)
    return unit.copy()