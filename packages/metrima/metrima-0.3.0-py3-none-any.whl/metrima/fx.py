from metrima.errors import UnexpectedTypeError

class Fx:
    def __init__(self, value: str | float | int) -> None:
        s = str(value)
        if '.' in s:
            whole, frac = s.split('.')
            self.scale: int = len(frac)
            self.value: int = int(whole + frac)
        else:
            self.scale: int = 0
            self.value: int = int(s)

        self._normalize()

    def is_zero(self) -> bool:
        return int(self.value) == 0

    def is_positive(self) -> bool:
        return int(self.value) > 0

    def is_negative(self) -> bool:
        return int(self.value) < 0

    def copy(self) -> 'Fx':
        new_copy = Fx.__new__(Fx)
        new_copy.value = self.value
        new_copy.scale = self.scale
        return new_copy

    def _normalize(self):
        """Remove trailing zeros from the fractional part"""
        if self.value == 0:
            self.scale = 0
            return

        while self.scale > 0 and self.value % 10 == 0:
            self.value //= 10
            self.scale -= 1

    def _align(self, other: 'Fx') -> tuple[int, int, int]:
        if not isinstance(other, Fx):
            raise UnexpectedTypeError(f"Unexpected type {type(other)}")

        if self.scale == other.scale:
            return self.value, other.value, self.scale
        if self.scale > other.scale:
            diff = self.scale - other.scale
            return self.value, other.value * (10 ** diff), self.scale
        diff = other.scale - self.scale
        return self.value * (10 ** diff), other.value, other.scale

    def __repr__(self):
        return f"Fx(value={self.value}, scale={self.scale})"

    def __hash__(self):
        """Allows Fx objects to be used as dict keys or in sets."""
        return hash((self.value, self.scale))

    #--- Conversions ---#
    def __float__(self):
        return self.value / (10 ** self.scale)

    def __int__(self):
        return int(float(self))

    def __str__(self):
        if self.scale == 0:
            return str(self.value)

        sign = "-" if self.value < 0 else ""
        val_str = str(abs(self.value))

        val_str = val_str.zfill(self.scale + 1)

        integer_part = val_str[:-self.scale]
        fractional_part = val_str[-self.scale:]

        return f"{sign}{integer_part}.{fractional_part}"

    #--- Miscellaneous ---#
    def __neg__(self) -> 'Fx':
        result = Fx.__new__(Fx)
        result.value = -self.value
        result.scale = self.scale
        result._normalize()
        return result

    def __pos__(self) -> 'Fx':
        result = Fx.__new__(Fx)
        result.value = self.value
        result.scale = self.scale
        result._normalize()
        return result

    def __abs__(self) -> 'Fx':
        result = Fx.__new__(Fx)
        result.value = abs(self.value)
        result.scale = self.scale
        result._normalize()
        return result

    def __round__(self, n: int = 0) -> 'Fx':
        return Fx(round(float(self), n))

    def __index__(self) -> int:
        return int(self)

    def __format__(self, format_spec: str) -> str:
        return format(float(self), format_spec)

    #--- Comparisons ---#
    # --- Comparisons (FIXED) ---#
    # All comparisons now use the precise Fx representation for the other operand.

    def _to_fx(self, other):
        """Helper to convert non-Fx types to Fx for safe comparison/arithmetic."""
        if isinstance(other, Fx):
            return other
        if isinstance(other, (int, float, str)):
            # Uses the global fx() function for conversion
            return fx(other)
        return NotImplemented

    def __eq__(self, other):
        other = self._to_fx(other)
        if other is NotImplemented: return False
        a, b, _ = self._align(other)
        return a == b

    def __ne__(self, other):
        other = self._to_fx(other)
        if other is NotImplemented: return True
        a, b, _ = self._align(other)
        return a != b

    def __gt__(self, other):
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, _ = self._align(other)
        return a > b

    def __ge__(self, other):
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, _ = self._align(other)
        return a >= b

    def __lt__(self, other):
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, _ = self._align(other)
        return a < b

    def __le__(self, other):
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, _ = self._align(other)
        return a <= b

    # --- Arithmetics (Refactored for Cleanliness) --#
    # Conversion logic simplified by using the helper self._to_fx()

    def __add__(self, other: 'Fx' | float | int) -> 'Fx':
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, scale = self._align(other)
        result_value = a + b
        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = scale
        result._normalize()
        return result

    def __sub__(self, other: 'Fx' | float | int) -> 'Fx':
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        a, b, scale = self._align(other)
        result_value = a - b
        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = scale
        result._normalize()
        return result

    def __mul__(self, other: 'Fx' | float | int) -> 'Fx':
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        result_value = self.value * other.value
        scale = self.scale + other.scale
        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = scale
        result._normalize()
        return result

    def __truediv__(self, other: 'Fx' | float | int) -> 'Fx':
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        if other.value == 0:
            raise ZeroDivisionError

        a, b, _ = self._align(other)

        calc_precision = max(16, self.scale + other.scale + 4)

        numerator = a * (10 ** calc_precision)

        result_value = numerator // b
        result_scale = calc_precision

        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = result_scale
        result._normalize()
        return result

    def __floordiv__(self, other: 'Fx' | float | int) -> 'Fx':
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented
        if other.value == 0:
            raise ZeroDivisionError

        a, b, _ = self._align(other)  # common_scale is not needed here

        result_value = a // b

        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = 0
        result._normalize()
        return result

    def __pow__(self, other: 'Fx' | float | int) -> 'Fx':
        if isinstance(other, (int, float)):
            other = fx(other)  # Use fx to convert standard types
        if not isinstance(other, Fx):
            return NotImplemented

        exponent = float(other)
        base = self

        if other.scale == 0 and other.value >= 0:
            exp_int = other.value
            if exp_int == 0:
                return Fx(1)
            result = Fx(1)
            for _ in range(exp_int):
                result *= base
            return result

        else:
            # NOTE: This uses floating-point arithmetic and may introduce errors.
            base_float = float(base)
            result_float = base_float ** exponent
            return Fx(result_float)

    def __mod__(self, other: 'Fx' | float | int) -> 'Fx':
        other = self._to_fx(other)
        if other is NotImplemented: return NotImplemented

        a, b, scale = self._align(other)

        result_value = a % b

        result = Fx.__new__(Fx)
        result.value = result_value
        result.scale = scale
        result._normalize()
        return result

    # --- Right hand (Refactored for Cleanliness) ---#
    # These still rely on Fx(other) in the implementation, which needs fx()
    def __radd__(self, other: int | float) -> 'Fx':
        return self + other

    def __rsub__(self, other: int | float) -> 'Fx':
        return fx(other) - self

    def __rmul__(self, other: int | float) -> 'Fx':
        return self * other

    def __rtruediv__(self, other: int | float) -> 'Fx':
        return fx(other) / self

    def __rfloordiv__(self, other: int | float) -> 'Fx':
        return fx(other) // self

    def __rmod__(self, other: int | float) -> 'Fx':
        return fx(other) % self

    def __rpow__(self, other: int | float) -> 'Fx':
        return fx(other) ** self

    # --- In-place operators (FIXED) ---#
    # These methods must be removed to enforce immutability.
    # Python automatically handles `a += b` by doing `a = a.__add__(b)`
    # if the in-place operator is absent, which preserves immutability.
    # The following are explicitly removed:

    # def __iadd__(self, other: Fx | int | float) -> Fx: ...
    # def __isub__(self, other: Fx | int | float) -> Fx: ...
    # def __imul__(self, other: Fx | int | float) -> Fx: ...
    # def __itruediv__(self, other: Fx | int | float) -> Fx: ...
    # def __ifloordiv__(self, other: Fx | int | float) -> Fx: ...
    # def __ipow__(self, other: Fx | int | float) -> Fx: ...
    # def __imod__(self, other: Fx | int | float) -> Fx: ...

    def is_integer(self) -> bool:
        """Checks if the Fx number represents an integer value."""
        return self.scale == 0


def fx(value: str | int | float) -> Fx:
    """
    Converts the following `value` to fx, if possible.
    :param value:
    :return:
    """
    return Fx(value)

if __name__ == "__main__":
    from tests import test_fx
    test_fx()