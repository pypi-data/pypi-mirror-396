from typing import Optional, Tuple, List, Union
import warnings

from metrima.fx import Fx
from metrima.lib import is_whole

Numeric = Union[int, float]

def downgrade_float_fx(value: float, chain: List[Tuple[int, str]]) -> Tuple[int, Optional[Tuple[str, Fx]]]:
    """
    Downgrades a float through a chain of conversion factors until we get a whole number.
    
    :param value: Original float value.
    :param chain: List of (factor, unit_name) tuples, e.g., [(60, "minutes"), (60, "seconds"), (1000, "milliseconds")].
    :return: (whole_value: int, leftover: Optional[Tuple[str, Fx]]).
    """
    current_val = Fx(value)
    
    for i, (factor, unit_name) in enumerate(chain):
        current_val *= Fx(factor)
        
        if is_whole(current_val):
            remaining_chain = chain[i+1:]
            for next_factor, _ in remaining_chain:
                current_val *= Fx(next_factor)
            return int(current_val), None
            
    return int(current_val), (unit_name, current_val)


class TimeUnit():
    """
    Base class for all time units (Hour, Minute, Second, Millisecond).
    """
    raw_value: Union[int, 'TimeUnit', float]
    value: int

    def __init__(self, value: Union[int, 'Hour', 'Minute', 'Second', 'Millisecond', float]) -> None:
        """
        Initializes a TimeUnit instance with the provided value.
        Upon initialization, it calls the _process_value method to handle the input appropriately.
        Following the SI convention, time units will default to seconds unless specified otherwise by subclass.

        :param self: The instance of the TimeUnit class.
        :param value: The value representing the time unit, which can be an integer or another TimeUnit subclass instance.
        :type value: int | 'Hour' | 'Minute' | 'Second' | 'Millisecond'
        """
        self.raw_value = value

        self._process_value()

    def _process_value(self) -> None:
        """
        **Abstract Method:** This method is intended to be overridden by subclasses 
        to handle the input value in a way specific to the time unit (Hour, Minute, etc.).
        
        If a concrete class forgets to implement this, it will raise a NotImplementedError.
        """
        raise NotImplementedError(
            f"Subclass {self.__class__.__name__} must implement the {self._process_value.__name__} method."
        )
    
    def __second__(self) -> int:
        """
        Type casting to seconds. second(self)
        
        :param self: The instance of the class
        """
        raise NotImplementedError(
            f"Subclass {self.__class__.__name__} must implement the {self.__second__.__name__} method."
        )
    
    def __minute__(self) -> int:
        """
        Type casting to minutes. minute(self)
        
        :param self: The instance of the class
        """
        raise NotImplementedError(
            f"Subclass {self.__class__.__name__} must implement the {self.__minute__.__name__} method."
        )
    
    def __hour__(self) -> int:
        """
        Type casting to hours. hour(self)
        
        :param self: The instance of the class
        """
        raise NotImplementedError(
            f"Subclass {self.__class__.__name__} must implement the {self.__hour__.__name__} method."
        )
    
    def __ms__(self) -> None:
        """
        Type casting to milliseconds. ms(self)

        :param self: The instance of the class
        """
        raise NotImplementedError(
            f"Subclass {self.__class__.__name__} must implement the {self.__ms__.__name__} method."
        )
    
    def __add__(self, other: Union[int, float, 'TimeUnit']) -> 'Second':
        """Add two TimeUnit values and return a Second instance (SI base).

        - If `other` is a TimeUnit, both are converted to milliseconds, summed,
          and returned as `Second(total_ms / 1000)` so fractional seconds are
          preserved and processed by `Second` class.
        - If `other` is numeric, it is interpreted as seconds.
        """
        if isinstance(other, TimeUnit):
            total_ms = self.__ms__() + other.__ms__()
        elif isinstance(other, (int, float)):
            total_ms = self.__ms__() + int(float(other) * 1000)
        else:
            return NotImplemented

        return second(total_ms / 1000)

    def __radd__(self, other: Union[int, float, 'TimeUnit']) -> 'Second':
        """Right-side addition to support numeric + TimeUnit."""
        return self.__add__(other)

    def __sub__(self, other: Union[int, float, 'TimeUnit']) -> 'Second':
        """Subtract and return a `Second` instance (SI base)."""
        if isinstance(other, TimeUnit):
            total_ms = self.__ms__() - other.__ms__()
        elif isinstance(other, (int, float)):
            total_ms = self.__ms__() - int(float(other) * 1000)
        else:
            return NotImplemented

        return second(total_ms / 1000)

    def __rsub__(self, other: Union[int, float, 'TimeUnit']) -> 'Second':
        """Right-side subtraction: numeric - TimeUnit or TimeUnit - TimeUnit."""
        if isinstance(other, TimeUnit):
            total_ms = other.__ms__() - self.__ms__()
        elif isinstance(other, (int, float)):
            total_ms = int(float(other) * 1000) - self.__ms__()
        else:
            return NotImplemented

        return second(total_ms / 1000)

    def __mul__(self, other: Union[int, float]) -> 'Second':
        """Scale a time value by a numeric factor, returning `Second`."""
        if not isinstance(other, (int, float)):
            return NotImplemented
        total_ms = int(self.__ms__() * float(other))
        return second(total_ms / 1000)

    def __rmul__(self, other: Union[int, float]) -> 'Second':
        return self.__mul__(other)

    def __truediv__(self, other: Union[int, float, 'TimeUnit']):
        """Division operator.

        - If dividing by a numeric, returns a `Second` scaled down.
        - If dividing by another TimeUnit, returns a float ratio (self/other).
        """
        if isinstance(other, TimeUnit):
            other_ms = other.__ms__()
            if other_ms == 0:
                raise ZeroDivisionError("division by zero TimeUnit")
            return self.__ms__() / other_ms
        if isinstance(other, (int, float)):
            if float(other) == 0:
                raise ZeroDivisionError("division by zero")
            total_ms = int(self.__ms__() / float(other))
            return second(total_ms / 1000)
        return NotImplemented

    def __rtruediv__(self, other: Union[int, float]):
        """Right division: numeric / TimeUnit -> ratio (float)."""
        if not isinstance(other, (int, float)):
            return NotImplemented
        denom = self.__ms__()
        if denom == 0:
            raise ZeroDivisionError("division by zero TimeUnit")
        return (float(other) * 1000) / denom

    # Comparison operators based on milliseconds
    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimeUnit):
            return self.__ms__() == other.__ms__()
        if isinstance(other, (int, float)):
            return self.__ms__() == int(float(other) * 1000)
        return NotImplemented

    def __lt__(self, other: Union[int, float, 'TimeUnit']) -> bool:
        if isinstance(other, TimeUnit):
            return self.__ms__() < other.__ms__()
        if isinstance(other, (int, float)):
            return self.__ms__() < int(float(other) * 1000)
        return NotImplemented

    def __le__(self, other: Union[int, float, 'TimeUnit']) -> bool:
        return self == other or self < other

    def __gt__(self, other: Union[int, float, 'TimeUnit']) -> bool:
        return not self <= other

    def __ge__(self, other: Union[int, float, 'TimeUnit']) -> bool:
        return not self < other
class Hour(TimeUnit):
    """
    Hour-specific time unit.
    """
    minutes: Optional[Union[int, Fx]] = None
    seconds: Optional[Union[int, Fx]] = None
    milliseconds: Optional[Union[int, Fx]] = None

    def _process_value(self) -> None:
        """
        Hour-specific logic for processing the input value.
        
        :param self: The instance of the Hour class.
        """
        allowed: list = [TimeUnit, int, float]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError(
                "Hours can only be instantiated from another TimeUnit instance or a numeric type."
            )
        
        raw: Union[int, float, TimeUnit] = self.raw_value

        if isinstance(raw, int):
            self.value: int = raw
            return
        
        if isinstance(raw, float):
            chain = [(60, "minutes"), (60, "seconds"), (1000, "milliseconds")]
            whole, leftover = downgrade_float_fx(raw, chain)

            CONVERSION_FACTOR = 3_600_000

            if leftover is None:
                self.value = whole // CONVERSION_FACTOR
            else:
                unit_name, val_fx = leftover
                warnings.warn(
                    f"Float value stored in {unit_name} and truncated for calculations",
                    UserWarning
                )
                setattr(self, unit_name, val_fx)
                self.value = whole // CONVERSION_FACTOR
                    
        if isinstance(raw, TimeUnit):
            self.value = raw.__hour__()

    def __second__(self) -> int:
        return self.value * 3600
    
    def __ms__(self) -> int:
        return self.value * 3_600_000
    
    def __repr__(self) -> str:
        return f"Hour({self.value})"
    
    def __str__(self) -> str:
        parts = [f"{self.value}h"]
        if self.minutes is not None:
            parts.append(f"{int(self.minutes)}m")
        if self.seconds is not None:
            parts.append(f"{int(self.seconds)}s")
        if self.milliseconds is not None:
            parts.append(f"{int(self.milliseconds)}ms")
        return " ".join(parts)
    
    def __repr__(self) -> str:
        return f"Hour({self.value})"
    
    def __str__(self) -> str:
        parts = [f"{self.value}h"]
        if self.minutes is not None:
            parts.append(f"{int(self.minutes)}m")
        if self.seconds is not None:
            parts.append(f"{int(self.seconds)}s")
        if self.milliseconds is not None:
            parts.append(f"{int(self.milliseconds)}ms")
        return " ".join(parts)

class Minute(TimeUnit):
    def _process_value(self) -> None:
        """
        Minute-specific logic for processing the input value.
        
        :param self: The instance of the Minute class.
        """
        allowed: list = [TimeUnit, int, float]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError(
                "Minutes can only be instantiated from another TimeUnit instance or a numeric type."
            )
        
        self.seconds: None | int | float = None
        self.milliseconds: None | int | float = None

        raw: int | float = self.raw_value
        if isinstance(raw, int):
            self.value: int = raw
            return
        if isinstance(raw, float):
            chain = [(60, "seconds"), (1000, "milliseconds")]
            whole, leftover = downgrade_float_fx(raw, chain)

            CONVERSION_FACTOR = 60_000
            self.value = whole // CONVERSION_FACTOR
            if leftover is not None:
                unit_name, val_fx = leftover
                warnings.warn(
                    f"Float value stored in {unit_name} and truncated for calculations",
                    UserWarning
                )
                setattr(self, unit_name, val_fx)

        if isinstance(raw, TimeUnit):
            self.value = raw.__minute__()

    def __second__(self) -> int:
        return self.value * 60
    
    def __ms__(self) -> int:
        return self.value * 60_000
    
    def __repr__(self) -> str:
        return f"Minute({self.value})"
    
    def __str__(self) -> str:
        parts = [f"{self.value}m"]
        if self.seconds is not None:
            parts.append(f"{int(self.seconds)}s")
        if self.milliseconds is not None:
            parts.append(f"{int(self.milliseconds)}ms")
        return " ".join(parts)
    
    def __repr__(self) -> str:
        return f"Minute({self.value})"
    
    def __str__(self) -> str:
        parts = [f"{self.value}m"]
        if self.seconds is not None:
            parts.append(f"{int(self.seconds)}s")
        if self.milliseconds is not None:
            parts.append(f"{int(self.milliseconds)}ms")
        return " ".join(parts)

class Second(TimeUnit):
    def _process_value(self) -> None:
        """
        Second-specific logic for processing the input value.
        
        :param self: The instance of the Second class.
        """
        allowed: list = [TimeUnit, int, float]
        if not isinstance(self.raw_value, tuple(allowed)):
            raise TypeError(
                "Seconds can only be instantiated from another TimeUnit instance or a numeric type."
            )

        self.milliseconds: None | int | float = None

        raw: int | float = self.raw_value
        if isinstance(raw, int):
            self.value: int = raw
            return
        if isinstance(raw, float):
            chain = [(1000, "milliseconds")]
            whole, leftover = downgrade_float_fx(raw, chain)

            CONVERSION_FACTOR = 1000
            # `whole` is in milliseconds; compute seconds and leftover ms
            self.value = whole // CONVERSION_FACTOR
            remainder = whole % CONVERSION_FACTOR
            if remainder:
                # store leftover milliseconds for accurate representation
                self.milliseconds = remainder
                warnings.warn(
                    "Float value had millisecond remainder; stored in .milliseconds",
                    UserWarning
                )
            if leftover is not None:
                unit_name, val_fx = leftover
                warnings.warn(
                    f"Float value stored in {unit_name} and truncated for calculations",
                    UserWarning
                )
                setattr(self, unit_name, val_fx)

        if isinstance(raw, TimeUnit):
            self.value = raw.__second__()

    def __minute__(self) -> int:
        return self.value // 60
    
    def __second__(self) -> int:
        return self.value
    
    def __ms__(self) -> int:
        return self.value * 1000
    
    def __repr__(self) -> str:
        return f"Second({self.value})"
    
    def __str__(self) -> str:
        parts = [f"{self.value}s"]
        if self.milliseconds is not None:
            parts.append(f"{int(self.milliseconds)}ms")
        return " ".join(parts)
    
    def __repr__(self) -> str:
        return f"Second({self.value})"
    
    def __str__(self) -> str:
        parts = [f"{self.value}s"]
        if self.milliseconds is not None:
            parts.append(f"{int(self.milliseconds)}ms")
        return " ".join(parts)

class Millisecond(TimeUnit):
    def _process_value(self) -> None:
        """
        Millisecond-specific logic for processing the input value.
        
        :param self: The instance of the Millisecond class.
        """
        if not isinstance(self.raw_value, (TimeUnit, int, float)):
            raise TypeError(
                "Milliseconds can only be instantiated from another TimeUnit instance or a numeric type."
            )
        
        if isinstance(self.raw_value, float):
            warnings.warn(
                "Float values are not supported for milliseconds because it is the lowest unit implemented. Converting to int by truncation.",
                UserWarning
            )
            self.raw_value = int(self.raw_value)

        if isinstance(self.raw_value, int):
            self.value = self.raw_value
        else:
            self.value = self.raw_value.__ms__()

    def __hour__(self) -> int:
        return self.value // 3_600_000
    
    def __minute__(self) -> int:
        return self.value // 60_000
    
    def __second__(self) -> int:
        return self.value // 1000
    
    def __ms__(self) -> int:
        return self.value
    
    def __repr__(self) -> str:
        return f"Millisecond({self.value})"
    
    def __str__(self) -> str:
        return f"{self.value}ms"
    
def second(value: int | 'Second' | 'Hour' | 'Minute' | 'Millisecond') -> Second:
    """
    Converts the given value to seconds, if possible.
    
    :param value: Description
    :type value: int | 'Second' | 'Hour' | 'Minute' | 'Millisecond'
    :return: Description
    :rtype: Second
    """
    if isinstance(value, (int, float)):
        return Second(value)
    else:
        return Second(value.__second__())
    
def minute(value: int | 'Second' | 'Hour' | 'Minute' | 'Millisecond') -> Minute:
    if isinstance(value, (int, float)):
        return Minute(value)
    else:
        return Minute(value.__minute__())
    
def hour(value: int | 'Second' | 'Hour' | 'Minute' | 'Millisecond') -> Hour:
    if isinstance(value, (int, float)):
        return Hour(value)
    else:
        return Hour(value.__hour__())
    
def ms(value: int | 'Second' | 'Hour' | 'Minute' | 'Millisecond') -> Millisecond:
    if isinstance(value, (int, float)):
        return Millisecond(int(value))
    else:
        return Millisecond(value.__ms__())
    