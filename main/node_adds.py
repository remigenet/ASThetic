"""
Rémi Genet
17/10/2023

Patterns matching for Node adds
Tried to be as exhaustive as possible, it may stay misses or mistakes
apply function helps apply on any Iterable the base matching function

Consider that AST is used in mode exec of course, so Module, Expression, Interactive and FunctionType are not present
"""
import ast
from ast import (
    ClassDef, FunctionDef, AsyncFunctionDef, Assign, AnnAssign, AugAssign,
    NamedExpr, keyword, IfExp, ListComp, SetComp, GeneratorExp, DictComp,
    comprehension, Expr, BinOp, BoolOp, Compare, Attribute, Subscript, Slice,
    arguments, arg, Name, AST, Delete, Import, ImportFrom, For, While, Try, With,
    Break, Return, Yield, Global, Nonlocal, If, Assert,
    Match, AsyncFor, AsyncWith, Await, ExceptHandler,
    Lambda, Raise, Constant, JoinedStr, YieldFrom,
    Starred, FormattedValue, withitem, Continue, alias, FunctionType, UnaryOp,
    TryStar, match_case, MatchOr, MatchAs, MatchStar, MatchValue, MatchMapping, MatchSingleton,
    MatchSequence, MatchClass, Call
)
from itertools import chain
from typing import Set, Optional, Callable, Iterable

from interface import interface_import

apply: Callable[[Callable[[Optional[AST], bool], Set[str]], Optional[Iterable[Optional[AST]]], bool], Set[str]]
apply, = interface_import("helpers", fromlist=('apply',), level=0)


def future_node_adds(node: Optional[AST] = None, *args) -> Set[str]:
    match node:

        case Constant(value=_):
            # | ast.Pass:
            return set()

        case FormattedValue(value=_, conversion=_, format_spec=_):
            return set()

        case JoinedStr(values=_):
            return set()

        case ast.List(elts=_, ctx=_) | ast.Tuple(elts=_, ctx=_):
            return set()

        case ast.Set(elts=_):
            return set()

        case ast.Dict(keys=_, values=_):
            return set()

        case Name(id=id):
            return {id}

        case Starred(value=_, ctx=_):
            return set()

        case Expr(value=_):
            return set()

        case FunctionType(argtypes=_, returns=_):
            return set()

        case ClassDef(name=name, bases  = _, keywords= _, body= _, decorator_list= _):
            return {name}

        case FunctionDef(name=name, args = _, body = _, decorator_list = _, returns = _) | AsyncFunctionDef(name=name, args = _, body = _, decorator_list = _, returns = _):
            return {name}

        case arguments(posonlyargs = posonlyargs, args=argmnts, vararg=vararg, kwonlyargs=kwonlyargs, kw_defaults=_, kwarg=kwargmnts, defaults=_):
            return apply(future_node_adds, chain(posonlyargs, argmnts, [vararg, kwargmnts], kwonlyargs))

        case Assign(targets=targets, value=_):
            return apply(future_node_adds, targets)

        case AugAssign(target=target) | AnnAssign(target=target) | NamedExpr(target=target) | comprehension(
            target=target):
            return future_node_adds(target)

        case Import(names=names) | ImportFrom(names=names):
            return apply(future_node_adds, names)

        case alias(name=name, asname=asname):
            return {asname or name}

        case arg(arg=a):
            return {a}

        case Call(func=func, args=armts, keywords=keywords):
            # Here --> Need to check if the function creates new variables inside it, as using global and nonlocal
            # Or modifying mutable objects
            # Or attributing herself new attributes
            return set()

        case UnaryOp():
            return set()

        case None:
            return set()

        case Expr(_) | Attribute(_) | Subscript(_) | \
             keyword(_) | Return(_) | Yield(_) | \
             YieldFrom(_) | FormattedValue(_):
            return set()

        case IfExp(test=_, body=_, orelse=_):
            return set()

        case ListComp(_, _) | SetComp(_, _) | GeneratorExp(_, _):
            return set()

        case DictComp(_, _, _):
            return set()

        case BinOp(_, _):
            return set()

        case BoolOp(_) | JoinedStr(_):
            return set()

        case Compare(_, _):
            return set()

        case Slice(_, _):
            return set()

        case Lambda(_, _):
            return set()

        case Raise(_, _):
            return set()

        case Assert(_, _):
            return set()

        case Delete(_):
            return set()



        case For(target=target, body=body, orelse=orelse):
            return apply(future_node_adds, [target] + body + orelse)

        case While(body=body, orelse=orelse) | If(body=body, orelse=orelse):
            return apply(future_node_adds, body + orelse)

        case Break() | Continue():
            return set()

        case Try(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody) | TryStar(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody):
            return apply(future_node_adds, body + handlers + orelse + finalbody)

        case ExceptHandler(body=body):
            return apply(future_node_adds, body)

        case With(items=items, body=body):
            return apply(future_node_adds, items) | apply(future_node_adds, body)

        case withitem(context_expr=_, optional_vars=optional_vars):
            return {optional_vars.name}  if optional_vars is not None and hasattr(optional_vars, 'name') else set()

        case Match(subject = _, cases= cases):
            return apply(future_node_adds, cases)

        case match_case(pattern = pattern, guard = _, body =body):
            return apply(future_node_adds, [pattern] +body)

        case MatchValue(value = _) | MatchSingleton(value = _):
            return set()

        case MatchSequence(patterns = patterns) | MatchOr(patterns = patterns):
            return apply(future_node_adds, patterns)

        case MatchStar(name=name):
            return future_node_adds(name)

        case MatchAs(pattern=pattern, name=name):
            return apply(future_node_adds, [pattern, name])

        case MatchMapping(keys=_, patterns=patterns, rest=rest):
            return apply(future_node_adds, patterns +  [rest])

        case MatchClass(cls = _, patterns = patterns, kwd_attrs = _, kwd_patterns=kwd_patterns):
            return apply(future_node_adds, patterns + kwd_patterns)

        case Global(names=_) | Nonlocal(names=_) | AsyncFor(target=_, iter=_, body=_, orelse=_) | AsyncWith(items=_, body=_) | Await(value=_) | _:
            error: str = f"{type(node)}  is not already implemented "
            raise NotImplementedError(error)

