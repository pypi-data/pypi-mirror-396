from metrima.lib import span
from typing import Callable, Final, Tuple, Any, Type, TypeVar, Dict, Optional
import time
from warnings import warn

F = TypeVar('F', bound=Callable[..., Any])

def mimic(wrapped: F) -> Callable[[F], F]:
    """
    Decorated factory to copy metadata from `wrapped` to wrapper function.
    
    :param wrapped:
    :type wrapped: Callable[..., Any]
    :return: 
    :rtype: Callable[[Callable[..., Any]], Callable[..., Any]]
    """
    WRAPPER_ASSIGNED: Final[Tuple[str]] = ('__module__', '__name__', '__qualname__', '__doc__', '__annotations__')
    WRAPPER_UPDATED: Final[Tuple[str]] = ('__dict__',)

    def decorator(wrapper: F) -> F:
        for attr in WRAPPER_ASSIGNED:
            try:
                value = getattr(wrapped, attr)
                setattr(wrapper, attr, value)
            except AttributeError:
                pass
        
        for attr in WRAPPER_UPDATED:
            try:
                wrapper_dict = getattr(wrapper, attr)
                wrapped_dict = getattr(wrapped, attr)
                wrapper_dict.update(wrapped_dict)
            except AttributeError:
                pass
        
        wrapper.__wrapped__ = wrapped
        
        return wrapper

    return decorator

def timed(func: F, announce: bool = False) -> F:
    """
    Measures execution time of a function.
    """
    @mimic(func)
    def wrapper(*args, **kwargs):
        start: float = time.perf_counter()
        result: Any = func(*args, **kwargs)
        duration: float = time.perf_counter() - start

        if announce:
            print(f"[timer] '{func.__name__}' took {duration:.3f} seconds to run")
            return result
        
        return result, duration
    return wrapper

def repeat(func: F, *args, **kwargs) -> F:
    """
    Creates a function factory that returns a decorator.
    The final call (count) dictates how many times 'func' is executed.
    Syntax: `repeat(func, *setup_args)(count)`
    
    :param func: The function that will be executed repeatedly.
    :param args: Ignored, but included for general function factory flexibility.
    :param kwargs: Ignored, but included for general function factory flexibility.
    :return: A function waiting for the 'count' argument.
    """
    def count_handler(count: int = 3):
        """
        Accepts the 'count' argument and returns the wrapper.
        """
        
        def wrapper(*w_args, **w_kwargs):
            last_result: Any = None
            
            for _ in span(count):
                last_result = func(*args, **kwargs)

            return last_result
        
        return wrapper
    
    return count_handler

def memo(clean: bool = True, max_cache: int = 5) -> F:
    if callable(clean):
        return memo(clean=True, max_cache=10)(clean)

    def decorator(func: F) -> F:
        cache: Dict[Tuple[Any, ...], Any] = {}

        @mimic(func)
        def wrapper(*args, **kwargs):
            key: Tuple = args + tuple(sorted(kwargs.items()))

            if key in cache:
                return cache[key]
            
            result = func(*args, **kwargs)
            cache[key] = result
            
            if clean and len(cache) > max_cache:
                del cache[next(iter(cache))]
            return result
        
        return wrapper
    return decorator

def legacy(message: str = "This is a legacy function and may behave "
            "differently from the updated version.") -> F:
    
    def decorator(func: F) -> F:
        @mimic(func)
        def wrapper(*args, **kwargs):
            warn(message, DeprecationWarning, stacklevel=2)

            result = func(*args, **kwargs)
            return result
        return wrapper
    
    return decorator

class attribute:
    """
    Acts as a descriptor that handles attribute access, assignment, and deletion.
    """

    def __init__(self, fget: Callable[[Any], Any],
                 fset: Optional[Callable[[Any, Any], None]] = None,
                 fdel: Optional[Callable[[Any], None]] = None) -> None:
        self.fget = fget
        self.fset = fset
        self.fdel = fdel

    def __get__(self, inst: Any, owner: Type[Any]) -> Any:
        """
        Handles attribute retrieval.
        """
        if inst is None:
            return self

        # Call the stored getter function, passing the instance
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        
        return self.fget(inst)

    def __set__(self, instance: Any, value: Any) -> None:
        """
        Handles attribute assignment (e.g., instance.attr = value).
        """
        if self.fset is None:
            raise AttributeError("can't set attribute")
        
        self.fset(instance, value)

    def __delete__(self, instance: Any) -> None:
        """
        Handles attribute deletion (e.g., del instance.attr).
        """
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        
        self.fdel(instance)

    # --- Decorator methods for setter and deleter ---
    
    def setter(self, fset: Callable[[Any, Any], None]) -> 'attribute':
        """
        Decorator method: returns a new Attribute instance with the new setter function.
        Used with the syntax: @attr.setter
        """
        return attribute(self.fget, fset, self.fdel)

    def deleter(self, fdel: Callable[[Any], None]) -> 'attribute':
        """
        Decorator method: returns a new Attribute instance with the new deleter function.
        Used with the syntax: @attr.deleter
        """
        return attribute(self.fget, self.fset, fdel)

def main() -> None:
    from tinycolors import cprint, color, clib

    cprint("=" * 50, as_="bold white")
    cprint("Decorators Demo with TinyColors", as_="bold cyan")
    cprint("=" * 50, as_="bold white")
    print()

    # Legacy decorator demo
    cprint("Testing @legacy decorator:", as_="bold yellow")
    cprint("-" * 50, as_="bold white")
    
    @legacy(message="Use float-add instead")
    def add(a: int, b: int) -> int:
        return a + b
    
    cprint("Calling add(1, 1)...", as_="italic blue")
    cprint(f"Result: {color.bold}{add(1, 1)}{clib.reset}", as_="bold green on black")
    print()

    # Modern function demo
    cprint("Using modern float_add function:", as_="bold yellow")
    cprint("-" * 50, as_="bold white")
    
    def float_add(a: float, b: float) -> float:
        return round(a + b)

    cprint("Calling float_add(1.2, 3.15)...", as_="italic blue")
    cprint(f"Result: {color.bold}{float_add(1.2, 3.15)}{clib.reset}", as_="bold green on black")
    print()

    # Timed decorator demo
    cprint("Testing @timed decorator:", as_="bold yellow")
    cprint("-" * 50, as_="bold white")
    
    @timed
    def slow_operation(n: int) -> int:
        total = 0
        for i in range(n):
            total += i
        return total
    
    cprint("Calling slow_operation(1000000)...", as_="italic blue")
    result, duration = slow_operation(1000000)
    cprint(f"Result: {color.bold}{result}{clib.reset}", as_="bold green on black")
    cprint(f"Duration: {color.italic}{duration:.6f} seconds{clib.reset}", color="yellow")
    print()

    # Memo decorator demo
    cprint("Testing @memo decorator:", as_="bold yellow")
    cprint("-" * 50, as_="bold white")
    
    @memo
    def fibonacci(n: int) -> int:
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)
    
    cprint("First call: fibonacci(30) - computing...", as_="italic blue")
    start_time = time.perf_counter()
    result3 = fibonacci(30)
    first_duration = time.perf_counter() - start_time
    cprint(f"Result: {color.bold}{result3}{clib.reset}", as_="bold green on black")
    cprint(f"Time taken: {color.italic}{first_duration:.6f} seconds{clib.reset}", color="yellow")
    print()
    
    cprint("Second call: fibonacci(30) - cached!", as_="italic blue")
    start_time = time.perf_counter()
    cached_duration = time.perf_counter() - start_time
    cprint(f"Result: {color.bold}{result3}{clib.reset}", as_="bold green on black")
    cprint(f"Time taken: {color.italic}{cached_duration:.9f} seconds{clib.reset}", color="cyan")
    
    cprint(f"Speedup: {color.bold}{first_duration / cached_duration if cached_duration > 0 else 0:.0f}x faster{clib.reset}", as_="bold bright green")
    print()
    
    cprint("Third call: fibonacci(28) - also cached (computed during first call)!", as_="italic blue")
    start_time = time.perf_counter()
    partial_duration = time.perf_counter() - start_time
    cprint(f"Result: {color.bold}{fibonacci(28)}{clib.reset}", as_="bold green on black")
    cprint(f"Time taken: {color.italic}{partial_duration:.9f} seconds{clib.reset}", color="cyan")
    print()

    cprint("=" * 50, as_="bold white")
    cprint("Demo Complete!", as_="bold cyan")
    cprint("=" * 50, as_="bold white")

if __name__ == "__main__":
    main()