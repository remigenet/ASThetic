"""
Rémi Genet
17/10/2023
"""
import ast
from typing import Set, Optional
from ast import (
    ClassDef, FunctionDef, AsyncFunctionDef, Assign, AnnAssign, AugAssign,
    NamedExpr, Call, keyword, IfExp, ListComp, SetComp, GeneratorExp, DictComp,
    comprehension, Expr, BinOp, BoolOp, Compare, Attribute, Subscript, Slice,
    arguments, arg, Name, AST, Delete, Import, ImportFrom, For, While, Try, With,
    Break, Return, Yield, Global, Nonlocal, If, Assert,
    Match, AsyncFor, AsyncWith, Await, ExceptHandler,
    Lambda, Raise, Constant, Load, JoinedStr, YieldFrom,
    Starred, FormattedValue, withitem, Continue, alias, FunctionType, UnaryOp,
    TryStar, match_case, MatchOr, MatchAs, MatchStar, MatchValue, MatchMapping, MatchSingleton,
    MatchSequence, MatchClass,
)

from helpers import apply

def future_node_modifies(node: Optional[AST] = None, past: bool = False) -> Set[str]:
    match node:

        case FunctionType(argtypes=_, returns=_):
            return set() # Not Done Yetset()

        case ClassDef(name=name, bases = _, keywords= _, body= _, decorator_list= _):
            return set() # Not Done Yet{name}

        case FunctionDef(name=name, args = _, body = _, decorator_list = _, returns = _) | AsyncFunctionDef(name=name, args = _, body = _, decorator_list = _, returns = _):
            return set() # Not Done Yet{name}

        case arguments(posonlyargs = posonlyargs, args = args, vararg = vararg, kwonlyargs = kwonlyargs, kwarg = kwarg):
            return set() # Not Done Yetapply(future_node_modifies, chain(posonlyargs, args, [vararg, kwarg], kwonlyargs))

        case Assign(targets=targets, value=_):
            return set() # Not Done Yetapply(future_node_modifies, targets)

        case AugAssign(target=target) | AnnAssign(target=target) | NamedExpr(target=target) | comprehension(
            target=target):
            return set() # Not Done Yetfuture_node_modifies(target)

        case Import(names=names) | ImportFrom(names=names):
            return set() # Not Done Yetapply(future_node_modifies, names)

        case alias(name=name, asname=asname):
            return set() # Not Done Yet{asname or name}

        case arg(arg=a):
            return set() # Not Done Yet{a}

        case Name(id=id):
            return set() # Not Done Yet{id}

        case UnaryOp():
            return set() # Not Done Yetset()

        case None:
            return set() # Not Done Yetset()

        case Expr(_) | Attribute(_) | Subscript(_) | \
             keyword(_) | Return(_) | Yield(_) | \
             YieldFrom(_) | Starred(_) | FormattedValue(_):
            return set() # Not Done Yetset()

        case IfExp(test=_, body=_, orelse=_):
            return set() # Not Done Yetset()

        case ListComp(_, _) | SetComp(_, _) | GeneratorExp(_, _):
            return set() # Not Done Yetset()

        case DictComp(_, _, _):
            return set() # Not Done Yetset()

        case BinOp(_, _):
            return set() # Not Done Yetset()

        case BoolOp(_) | JoinedStr(_):
            return set() # Not Done Yetset()

        case Compare(_, _):
            return set() # Not Done Yetset()

        case Slice(_, _):
            return set() # Not Done Yetset()

        case Lambda(_, _):
            return set() # Not Done Yetset()

        case Raise(_, _):
            return set() # Not Done Yetset()

        case Assert(_, _):
            return set() # Not Done Yetset()

        case Delete(_):
            return set() # Not Done Yetset()

        case ast.List(_) | ast.Tuple(_) | ast.Set(_):
            return set() # Not Done Yetset()

        case ast.Dict(_, _):
            return set() # Not Done Yetset()

        case Constant() | Load() | ast.Pass:
            return set() # Not Done Yetset()

        case For(target=target, body=body, orelse=orelse):
            return set() # Not Done Yetapply(future_node_modifies, [target] + body + orelse)

        case While(body=body, orelse=orelse) | If(body=body, orelse=orelse):
            return set() # Not Done Yetapply(future_node_modifies, body + orelse)

        case Break() | Continue():
            return set() # Not Done Yetset()

        case Try(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody) | TryStar(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody):
            return set() # Not Done Yetapply(future_node_modifies, body + handlers + orelse + finalbody)

        case ExceptHandler(body=body):
            return set() # Not Done Yetapply(future_node_modifies, body)

        case With(items=items, body=body):
            return set() # Not Done Yetapply(future_node_modifies, items) | apply(future_node_modifies, body)

        case withitem(context_expr=_, optional_vars=optional_vars):
            return set() # Not Done Yet{optional_vars.name}  if optional_vars is not None and hasattr(optional_vars, 'name') else set()

        case Match(subject = _, cases= cases):
            return set() # Not Done Yetapply(future_node_modifies, cases)

        case match_case(pattern = pattern, guard = _, body =body):
            return set() # Not Done Yetapply(future_node_modifies, [pattern] +body)

        case MatchValue(value = _) | MatchSingleton(value = _):
            return set() # Not Done Yetset()

        case MatchSequence(patterns = patterns) | MatchOr(patterns = patterns):
            return set() # Not Done Yetapply(future_node_modifies, patterns)

        case MatchStar(name=name):
            return set() # Not Done Yetfuture_node_modifies(name)

        case MatchAs(pattern=pattern, name=name):
            return set() # Not Done Yetapply(future_node_modifies, [pattern, name])

        case MatchMapping(keys=_, patterns=patterns, rest=rest):
            return set() # Not Done Yetapply(future_node_modifies, patterns +  [rest])

        case MatchClass(cls = _, patterns = patterns, kwd_attrs = _, kwd_patterns=kwd_patterns):
            return set() # Not Done Yetapply(future_node_modifies, patterns + kwd_patterns)

        case Global(names=_) | Nonlocal(names=_) | AsyncFor(target=_, iter=_, body=_, orelse=_) | AsyncWith(items=_, body=_) | Await(value=_) | _:
            error: str = f"{type(node)}  is not already implemented "
            raise NotImplementedError(error)

