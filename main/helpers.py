"""
Rémi Genet
17/10/2023
"""
from typing import Callable, Set, Optional, Iterable
from ast import AST


def apply(
        func: Callable[[Optional[AST], bool], Set[str]],
        nodes: Optional[Iterable[Optional[AST]]],
        past: bool = False
) -> Set[str]:
    return set.union(*(func(node, past) for node in nodes)) if nodes else set()




