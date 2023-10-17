"""
Rémi Genet
17/10/2023
"""
from typing import Tuple, Set, List, Union, Callable, Optional
from ast import FunctionDef, AsyncFunctionDef,  AST,  Constant

from interface import interface_import
all_node_needs: Callable[[Optional[AST],bool], Set[str]] = interface_import("node_needs", fromlist=('all_node_needs',), level=0)[0]
future_node_adds: Callable[[Optional[AST],bool], Set[str]] = interface_import("node_adds", fromlist=('future_node_adds',), level=0)[0]


def TimeNodeCost(Node: [AST], InitDef: Set[str]) -> Set[str]:
    node_adds: List[Set[str]] = [InitDef] + [future_node_adds(node) for node in Node]
    node_costs: List[Set[str]] = [set()] + [all_node_needs(node, past=True) for node in Node]
    _, _, missing = implied_previous_needs(node_adds, node_costs, [True for _ in range(len(node_adds))])
    return set().union(*missing)

def prune_node(node: AST) -> AST:
    """

    :rtype: object
    """
    match node:
        case FunctionDef(_) | AsyncFunctionDef(_):
            return prune_function(node)
        case _:
            return node

def prune_function(FuncNode: Union[FunctionDef, AsyncFunctionDef]) -> Union[FunctionDef, AsyncFunctionDef]:
    # Determine the set of unused arguments in the function definition.
    unused_args: Set[str] = future_node_adds(FuncNode.args) - set().union(*(all_node_needs(node, past=True) for node in FuncNode.body))
    posixargs = [arg.arg for arg in FuncNode.args.posonlyargs + FuncNode.args.args][-len(FuncNode.args.defaults):]
    FuncNode.args.defaults = [Constant(value=None) if arg in unused_args else default for arg, default in zip(posixargs, FuncNode.args.defaults)]
    FuncNode.args.kw_defaults = [None if arg in unused_args else default for arg, default in
                              zip(FuncNode.args.kwonlyargs, FuncNode.args.kw_defaults)]
    return FuncNode

def implied_globals_needs(node_adds: List[Set[str]], node_costs: List[Set[str]], selected: List[bool]) \
        -> Tuple[Set[str], Set[str], Set[str]]:
    assets: Set[str] = set().union(*(s for s, b in zip(node_adds, selected) if b))
    needs: Set[str] = set().union(*(s for s, b in zip(node_costs, selected) if b))
    missing: Set[str] = needs - assets
    return assets, needs, missing


def implied_previous_needs(node_adds: List[Set[str]], node_costs: List[Set[str]], selected: List[bool]) \
        -> Tuple[List[Set[str]], List[Set[str]], List[Set[str]]]:
    assets = [set().union(*(s for s, b in zip(node_adds[:end], selected[:end]) if b)) if any(selected[:end]) else set()
              for end in range(len(node_adds) + 1)]
    needs = [set().union(*(s for s, b in zip(node_costs[:end], selected[:end]) if b)) if any(selected[:end]) else set()
             for end in range(len(node_adds) + 1)]
    if needs[0]:
        raise ImportError(f'You should not have first need different from 0 {needs[0]}')
    missing: List[Set[str]] = [needs[0]] + [n - a for n, a in zip(needs[1:], assets[:-1])]
    return assets, needs, missing

