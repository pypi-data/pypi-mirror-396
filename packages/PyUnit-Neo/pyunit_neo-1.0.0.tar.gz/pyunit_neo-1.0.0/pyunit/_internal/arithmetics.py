import math
from typing import Union, Self, Any

class Arithmetics:
    """Provide arithmetic, reflected, in-place and comparison dunders.

    Assumptions:
      - A global function `base_unit(obj)` exists and returns a numeric base value
        for objects that represent units (Unit or subclasses).
      - Unit subclasses implement `new(cls, unit_or_class, *args, **kwargs)` as in your
        Unit implementation; here we call `self.__class__.new(self.__class__, value)`
        to create a new instance of the same unit type.
      - UninitializedUnit objects implement `.extract()` returning the underlying
        unit descriptor; if that object is passed as an operand we attempt to extract
        a numeric value from it (via base_unit) or fall back to its `.extract()` value.
    """

    # ---------- Helpers ----------
    def _is_number(self, obj: Any) -> bool:
        return isinstance(obj, (int, float))

    def _extract_numeric(self, obj: Any) -> float:
        """Return a plain float for obj:
           - numbers -> float
           - UninitializedUnit -> extract() and try again
           - objects with base_unit() -> call global base_unit(obj) if available
           - objects with attribute 'base_unit' method -> call that method
           - otherwise raise TypeError
        """
        # plain numbers
        if self._is_number(obj):
            return float(obj)

        # UninitializedUnit (or similar) that exposes extract()
        if hasattr(obj, "extract") and not hasattr(obj, "base_unit"):
            try:
                extracted = obj.extract()
            except Exception:
                # If extract exists but fails, propagate meaningful error
                raise TypeError(f"cannot extract numeric value from {obj!r}")
            return self._extract_numeric(extracted)

        # If object has global helper base_unit available, prefer that
        try:
            # try calling the global function `base_unit` if it exists
            numeric = base_unit(obj) # type: ignore   -- Don't mind the warning.
            return float(numeric)
        except Exception:
            pass

        # if the object itself implements a base_unit() instance method
        if hasattr(obj, "base_unit") and callable(getattr(obj, "base_unit")):
            numeric = obj.base_unit()
            return float(numeric)

        # last resort: try numeric conversion
        if hasattr(obj, "__float__"):
            try:
                return float(obj)
            except Exception:
                pass

        raise TypeError(f"unsupported operand type for numeric extraction: {obj!r}")

    def _wrap_result(self, numeric: float, left_operand: Any) -> Union[Self, int, float]:
        """Wrap numeric into a unit of left_operand's class if left_operand is an Arithmetics/Unit.
           Otherwise return plain numeric (float or int when exact).
        """
        # if the left operand is an Arithmetics-derived object, return a new instance
        if isinstance(left_operand, Arithmetics):
            # prefer float, but if integer-like, keep as int for nicety
            value = int(numeric) if float(numeric).is_integer() else float(numeric)
            # Use the class's `new` method if available (Unit.new pattern)
            cls = left_operand.__class__
            #if hasattr(cls, "new") and callable(getattr(cls, "new")):
            #    return cls.new(cls, value) # This feature doesn't function but is saved for maintanence
            # fallback: try construct directly with numeric argument
            try:
                return cls(value)
            except Exception:
                # If we cannot construct, return numeric so caller can handle
                return value
        # otherwise return float or int if integer-valued
        if float(numeric).is_integer():
            return int(numeric)
        return float(numeric)

    # ---------- Arithmetic ----------
    def __binary_op(self, other, op, reflected=False):
        if getattr(self, "_constant", False):
            raise AttributeError("A constant value should be accessed directly.")

        left = self if not reflected else other
        right = other if not reflected else self

        a = self._extract_numeric(left)
        b = self._extract_numeric(right)
        try:
            result = op(a, b)
        except ZeroDivisionError:
            raise ZeroDivisionError("division by zero")
        return self._wrap_result(result, left)

    def __add__(self, other):
        return self.__binary_op(other, lambda a, b: a + b)

    def __radd__(self, other):
        return self.__binary_op(other, lambda a, b: a + b, reflected=True)

    def __sub__(self, other):
        return self.__binary_op(other, lambda a, b: a - b)

    def __rsub__(self, other):
        return self.__binary_op(other, lambda a, b: a - b, reflected=True)

    def __mul__(self, other):
        return self.__binary_op(other, lambda a, b: a * b)

    def __rmul__(self, other):
        return self.__binary_op(other, lambda a, b: a * b, reflected=True)

    def __truediv__(self, other):
        return self.__binary_op(other, lambda a, b: a / b)

    def __rtruediv__(self, other):
        return self.__binary_op(other, lambda a, b: a / b, reflected=True)

    def __floordiv__(self, other):
        return self.__binary_op(other, lambda a, b: a // b)

    def __rfloordiv__(self, other):
        return self.__binary_op(other, lambda a, b: a // b, reflected=True)

    def __mod__(self, other):
        return self.__binary_op(other, lambda a, b: a % b)

    def __rmod__(self, other):
        return self.__binary_op(other, lambda a, b: a % b, reflected=True)

    def __pow__(self, other, modulo=None):
        # modulo ignored for floats; keep signature compatibility
        return self.__binary_op(other, lambda a, b: math.pow(a, b))

    def __rpow__(self, other):
        return self.__binary_op(other, lambda a, b: math.pow(a, b), reflected=True)

    # ---------- In-place (map to normal ops) ----------
    def __iadd__(self, other):
        return self.__add__(other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __itruediv__(self, other):
        return self.__truediv__(other)

    def __ifloordiv__(self, other):
        return self.__floordiv__(other)

    def __imod__(self, other):
        return self.__mod__(other)

    def __ipow__(self, other):
        return self.__pow__(other)

    # ---------- Unary ----------
    def __neg__(self):
        a = self._extract_numeric(self)
        return self._wrap_result(-a, self)

    def __pos__(self):
        a = self._extract_numeric(self)
        return self._wrap_result(+a, self)

    def __abs__(self):
        a = self._extract_numeric(self)
        return self._wrap_result(abs(a), self)

    def __int__(self):
        return int(self._extract_numeric(self))

    def __float__(self):
        return float(self._extract_numeric(self))

    def __round__(self, ndigits=None):
        a = self._extract_numeric(self)
        if ndigits is None:
            return self._wrap_result(round(a), self)
        return self._wrap_result(round(a, ndigits), self)

    # ---------- Comparisons ----------
    def __eq__(self, other):
        try:
            return self._extract_numeric(self) == self._extract_numeric(other)
        except TypeError:
            return False

    def __ne__(self, other):
        try:
            return self._extract_numeric(self) != self._extract_numeric(other)
        except TypeError:
            return True

    def __lt__(self, other):
        return self._extract_numeric(self) < self._extract_numeric(other)

    def __le__(self, other):
        return self._extract_numeric(self) <= self._extract_numeric(other)

    def __gt__(self, other):
        return self._extract_numeric(self) > self._extract_numeric(other)

    def __ge__(self, other):
        return self._extract_numeric(self) >= self._extract_numeric(other)

    # ---------- Boolean ----------
    def __bool__(self):
        return bool(self._extract_numeric(self))