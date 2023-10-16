import ast
import sys
from typing import Callable, TypeVar, Any, Tuple, Set, List, Optional, Union, Iterable, Dict


from ast import (
    ClassDef, FunctionDef, AsyncFunctionDef, Assign, AnnAssign, AugAssign,
    NamedExpr, Call, keyword, IfExp, ListComp, SetComp, GeneratorExp, DictComp,
    comprehension, Expr, BinOp, BoolOp, Compare, Attribute, Subscript, Slice,
    arguments, arg, Name, AST, Delete, Import, ImportFrom, For, While, Try, With,
    Break, Return, Yield, Global, Nonlocal, If, Assert,
    Match, Module, AsyncFor, AsyncWith, Await, ExceptHandler,
    Lambda, Raise, Constant, Load, JoinedStr, YieldFrom,
    Starred, FormattedValue, stmt, withitem, TryStar, Continue, alias, FunctionType, UnaryOp
)

def version_above(major: int, minor: int = 0, micro: int = 0) -> bool:
    return sys.version_info >= (major, minor, micro)

def GetNodeCategories() -> Dict[str, Tuple[type, ...]]:
    # Define node types categorization as dictionaries or namedtuples for better readability
    NodeCategories: dict[str, Set[type]] = dict(
        valid={FunctionDef, AsyncFunctionDef, AugAssign, ClassDef, Assign, AnnAssign, Delete,
               Import, ImportFrom},
        unpossible_at_top={Break, Return, Yield, alias},
        not_yet_handled={Global, Nonlocal, If, Assert, For, While, Try, TryStar, With})
    # Update node types categorization based on Python version
    if version_above(3, 8):
        NodeCategories['valid'].update((NamedExpr,))
        NodeCategories['not_yet_handled'].update((FunctionType,))

    if version_above(3, 10):
        NodeCategories['not_yet_handled'].update((Match,))

    if version_above(3, 11):
        NodeCategories['not_yet_handled'].update((TryStar,))

    if version_above(3, 12):
        NodeCategories['not_yet_handled'].update((TypeVar, ast.ParamSpec, ast.TypeVarTuple, ast.TypeAlias,))

    return {k: tuple(v) for k, v in NodeCategories.items()}