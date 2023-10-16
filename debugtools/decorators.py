import functools
from copy import deepcopy
from typing import Callable, TypeVar, Any, Tuple

F = TypeVar('F', bound=Callable[..., Any])
count = 0
def InnOut(f: F) -> F:
    """
    A decorator to log the input arguments, output, and a unique identifier
    for calls to the decorated function.
    """

    @functools.wraps(f)  # Preserve original function's name and docstring
    def wrapper(*args: Tuple[Any, ...], **kwargs: Any) -> Any:
        global count
        count += 1
        uid = deepcopy(count)
        print(f'In {uid} {f.__name__} {args} {kwargs}')
        res = f(*args, **kwargs)
        print(f'Out {uid} {res}')
        return res

    return wrapper  # type: ignore
