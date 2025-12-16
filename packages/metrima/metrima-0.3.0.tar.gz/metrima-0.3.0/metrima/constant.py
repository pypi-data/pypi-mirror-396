from metrima.errors import ConstantError

class Constant:
    """
    An immutable container for a single constant value.
    Attempts to change any attribute after initialization will fail.
    """
    def __init__(self, value: int) -> None:
        object.__setattr__(self, 'value', value)

    def __setattr__(self, name, value) -> None:
        """Prevents modification of any attribute after __init__."""
        raise ConstantError()

    def __delattr__(self, name) -> None:
        raise ConstantError()

    def __repr__(self) -> str:
        return f"Constant({self.value!r})"

    def __str__(self) -> str:
        return str(self.value)