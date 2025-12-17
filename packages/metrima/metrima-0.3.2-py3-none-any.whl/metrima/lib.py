from typing import Any, Iterable, Optional, Generator, Tuple
from metrima.core.fx import Fx

def length(collection: list | dict | str) -> int:
    """
    Get the length of a collection
    
    :param collection: Collection to get length of
    :type collection: list | dict | str
    :return: Length of the collection
    :rtype: int
    """
    count: int = 1
    for _ in collection:
        count += 1
    return count - 1

def invert(sequence: list[Any]) -> list[Any]:
    """
    Invert a sequence
    
    :param sequence: Sequence to invert
    :type sequence: list[Any]
    :return: Inverted sequence
    :rtype: list[Any]
    """
    reversed_sequence: list[Any] = []
    for i in span(length(sequence)-1, -1, -1):
        reversed_sequence.append(sequence[i])
    return reversed_sequence

def is_whitespace(string: str) -> bool:
    """
    Checks if a character is a whitespace character
    
    :param char: Description
    :type char: str
    :return: Description
    :rtype: bool
    """
    return has(char in (' ', '\n', '\t', '\r', '\f', '\xa0', '\v', '\u1680', '\u2002', '\u2003', '\u2009', '\u200a', '\u200b','\u3000', '\u2007','\u2008','\u2028','\u2029') for char in string)

def trim(string: str) -> str:
    """
    Trims whitespace from the start and end of a string
    
    :param string: String to trim
    :type string: str
    :return: Trimmed string
    :rtype: str
    """
    str_length: int = length(string)

    start_index: int = 0
    while start_index < str_length:
        if is_whitespace(string[start_index]):
            start_index += 1
        else:
            break
    
    if start_index == str_length:
        return ""
    
    end_index: int = str_length - 1
    while end_index >= start_index:
        if is_whitespace(string[end_index]):
            end_index -= 1
        else:
            break
    
    return string[start_index : end_index+1]

def has(iterable: Iterable[object]) -> bool:
    """
    Returns True if the iterable has at least one truthy element

    :param iterable: Description
    :type iterable: Iterable[object]
    :return: Description
    :rtype: bool
    """
    for element in iterable:
        if element:
            return True

    return False

def locate(string: str, substring: str) -> int: 
    """
    Locate the first occurrence of `substring` in `string`
    
    :param string: The string to search
    :type string: str
    :param substring: The substring to locate
    :type substring: str
    :return: Index of first occurrence of substring, or -1 if not found
    :rtype: int
    """
    str_length: int = length(string)
    sub_length: int = length(substring)

    if sub_length > str_length: 
        return -1

    for i in span(str_length - sub_length + 1): 
        if string[i : i + sub_length] == substring: 
            return i
    
    return -1

def span(start: int, stop: Optional[int] = None, 
         step: int = 1) -> Generator[int, None, None]:
    """
    Generate a sequence of numbers from start to stop with a specified step

    :param start: Starting number (or stop if only one argument is provided)
    :type start: int
    :param stop: Stopping number (optional)
    :type stop: Optional[int]
    :param step: Step size (default is 1)
    :type step: int
    :return: Generator yielding numbers in the specified range
    :rtype: Generator[int, None, None]
    """
    if step == 0:
        raise ValueError("span() step must not be zero")

    if stop is None:
        stop = start
        start = 0

    if step > 0:
        while start < stop:
            yield start
            start += step
    else:
        while start > stop:
            yield start
            start += step

def attach(target_list: list[Any], element: Any) -> None: 
    """
    Attach an element to the end of a list
    
    :param target_list: Target list to attach to
    :type target_list: list[Any]
    :param element: Element to attach
    :type element: Any
    """
    target_list += [element]

def push_back(target_list: list[Any], element: Any) -> list[Any]:
    """
    Push an element to the back of a list and return the new list
    
    :param target_list: Target list to push to
    :type target_list: list[Any]
    :param element: Element to push
    :type element: Any
    :return: New list with element pushed to back
    :rtype: list[Any]
    """
    return_list: list[Any] = duplicate(target_list)
    attach(return_list, element)
    return return_list

def combinelst(*lists: list[Any]) -> list[Any]:
    """
    Docstring for combine
    
    :param lists: Lists to combine
    :type lists: list[Any]
    :return: Combined list
    :rtype: list[Any]
    """
    result: list[Any] = []
    for lst in lists:
        result += lst
    return result

def duplicate(obj: Any, memo: Optional[dict] = None) -> Any:
    """
    Deeply duplicate an object
    
    :param obj: Object to duplicate
    :type obj: Any
    :param memo: Memoization dictionary to handle circular references
    :type memo: Optional[dict]
    :return: Duplicated object
    :rtype: Any
    """
    if memo is None:
        memo = {}
    
    obj_id = id(obj)
    if obj_id in memo:
        return memo[obj_id]
    
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif isinstance(obj, list):
        new_obj = []
        memo[obj_id] = new_obj
        new_obj.extend(duplicate(x, memo) for x in obj)
        return new_obj
    elif isinstance(obj, dict):
        new_obj = {}
        memo[obj_id] = new_obj
        for k, v in obj.items():
            new_obj[duplicate(k, memo)] = duplicate(v, memo)
        return new_obj
    elif isinstance(obj, set):
        new_obj = set()
        memo[obj_id] = new_obj
        for x in obj:
            new_obj.add(duplicate(x, memo))
        return new_obj
    elif isinstance(obj, tuple):
        new_obj = tuple(duplicate(x, memo) for x in obj)
        memo[obj_id] = new_obj
        return new_obj
    elif hasattr(obj, "__dict__"):
        new_obj = obj.__class__.__new__(obj.__class__)
        memo[obj_id] = new_obj
        for k, v in obj.__dict__.items():
            setattr(new_obj, k, duplicate(v, memo))
        return new_obj
    else:
        raise TypeError(f"Unsupported type for {duplicate.__name__}: {type(obj)}")

def verify(iterable: Iterable) -> bool: 
    for element in iterable:
        if not element:
            return False
    
    return True

def chop(string: str, delimiter: str) -> list[str]:
    """
    Splits a string into a list of substrings using a specified delimiter.
    Recreates the core logic of str.split(delimiter).
    
    :param string: The string to be split.
    :type string: str
    :param delimiter: The string used to separate the segments.
    :type delimiter: str
    :return: A list of substrings.
    :rtype: list[str]
    """
    parts: list[str] = []
    str_length: int = length(string)
    del_length: int = length(delimiter)
    current_index: int = 0

    if del_length == 0:
        for char in string:
            attach(parts, char)
        return parts

    while True:        
        search_area: str = string[current_index:]
        match_relative_index: int = locate(search_area, delimiter)
        
        if match_relative_index == -1:
            break
        
        match_absolute_index: int = current_index + match_relative_index
        
        segment: str = string[current_index : match_absolute_index]
        attach(parts, segment)
        
        current_index = match_absolute_index + del_length

    final_segment: str = string[current_index : str_length]
    attach(parts, final_segment)
    
    return parts

def is_whole(number: int | float | Fx) -> bool:
    """
    Check if a `number` argument is a whole number (integer value)

    :param number: Number to check
    :type number: int | float | Fx
    :return: True if number is whole, False otherwise
    :rtype: bool
    """
    if isinstance(number, bool):
        return False
    
    if isinstance(number, int):
        return True
    
    if isinstance(number, (float, Fx)):
        return number % 1 == 0

    return False

def indexed(collection: Iterable) -> Generator[Tuple[int, Any], None, None]:
    """Generates a sequence of index-value pairs from an iterable sequence.

    Args:
        collection (Iterable): The sequence or iterable object to be indexed.

    Yields:
        Generator[Tuple[int, Any], None, None]: A tuple containing the current index and the item.
    """
    i: int = 0

    for item in collection:
        yield i, item
        i += 1
