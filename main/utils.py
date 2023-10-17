"""
Rémi Genet
17/10/2023
"""
import ast
from ast import Module, AST
import functools
from typing import Callable, TypeVar, Any, Tuple
from copy import deepcopy
F = TypeVar('F', bound=Callable[..., Any])
count = 0


def parse(path: str) -> Module:
    with open(path, 'r') as file:
        tree = ast.parse(file.read(), filename=path)
    return tree


def get_source_segment(path: str, node: AST) -> str | None:
    with open(path, 'r') as file:
        segment = ast.get_source_segment(file.read(), node=node)
    return segment


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