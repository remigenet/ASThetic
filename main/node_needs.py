"""
Rémi Genet
17/10/2023
"""
import ast
from itertools import chain
from typing import Set, Optional, Callable, Iterable, Tuple, Union, List
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
from interface import interface_import
prune_node: Callable[[AST],AST]
implied_globals_needs: Callable[[List[Set[str]], List[Set[str]], List[bool]],Tuple[Set[str], Set[str], Set[str]]]
implied_previous_needs: Callable[[List[Set[str]], List[Set[str]], List[bool]], Tuple[List[Set[str]], List[Set[str]], List[Set[str]]]]

future_node_adds: Callable[[Optional[AST],bool], Set[str]] = interface_import("node_adds", fromlist=('future_node_adds',), level=0)[0]
TimeNodeCost: Callable[[AST,Set[str]],Set[str]] = interface_import("node_selection", fromlist=('TimeNodeCost',), level=0)[0]
apply: Callable[[Callable[[Optional[AST], bool],Set[str]],Optional[Iterable[Optional[AST]]],bool],Set[str]] = interface_import("helpers", fromlist=('apply',), level=0)[0]
prune_node, implied_globals_needs, implied_previous_needs = interface_import("node_selection", fromlist=('prune_node', 'implied_globals_needs', 'implied_previous_needs',), level=0)


def all_node_needs(node: Optional[AST] = None, past: bool = True) -> Set[str]:

    if node is None:
        return set()

    match node:

        case FunctionType(argtypes=_, returns=_):
            return set()

        case ClassDef(name=_, bases=bases, keywords=_, body=body, decorator_list=decorator_list):
            return apply(all_node_needs, chain(bases, decorator_list, body), past=past)

        case FunctionDef(name=_, args=args, body=_, decorator_list=decorator_list, returns=_) | \
             AsyncFunctionDef(name=_, args=args, body=_, decorator_list=decorator_list, returns=_):
            if past:
                print(node.name, "PAST NEED", apply(all_node_needs, decorator_list + [args]))
                return apply(all_node_needs, decorator_list + [args])
            else:
                global_need = TimeNodeCost(node.body, future_node_adds(node.args))
                print(node.name, "GLOBAL NEED", global_need)
                return global_need

        case For(target=target, iter=iter, body=body, orelse=orelse):
            return TimeNodeCost([iter] + body + orelse, future_node_adds(target))

        case While(test, body, orelse) | If(test, body, orelse):
            return TimeNodeCost(test + body + orelse, set())

        case Break() | Continue():
            return set()

        case Try(body = body, handlers = handlers, orelse = orelse, finalbody = finalbody) | \
             TryStar(body = body, handlers = handlers, orelse = orelse, finalbody = finalbody):
            return TimeNodeCost(body + handlers + orelse + finalbody, set())

        case ExceptHandler(type=t, name=name, body=body):
            return all_node_needs(t) | TimeNodeCost(body, set(name))

        case With(items=items, body=body, type_comment=_):
            return apply(all_node_needs, items) | TimeNodeCost(body, apply(future_node_adds, items))

        case withitem(context_expr=context_expr, optional_vars=_):
            return all_node_needs(context_expr)

        case Yield(value=value) | YieldFrom(value=value):
            return all_node_needs(value)

        case Assign(value=value) | \
             NamedExpr(value=value) | \
             Expr(value=value) | \
             Attribute(value=value) | \
             Subscript(value=value) | \
             keyword(value=value) | \
             Return(value=value) | \
             Yield(value=value) | \
             YieldFrom(value=value) | Starred(value=value) | FormattedValue(value=value) \
            :
            return all_node_needs(value, past=past)

        case AnnAssign(annotation=annotation, value=value):
            return apply(all_node_needs, [annotation, value], past=past)

        case AugAssign(target=target, value=value):
            return apply(all_node_needs, [target, value], past=past)

        case Call(func=func, args=args, keywords=keywords):
            return apply(all_node_needs, chain([func], args, keywords), past=False)

        case IfExp(test=test, body=body, orelse=orelse):
            return apply(all_node_needs, [test, body, orelse], past=past)

        case ListComp(elt=elt, generators=generators) | \
             SetComp(elt=elt, generators=generators) | \
             GeneratorExp(elt=elt, generators=generators):
            return apply(all_node_needs, chain([elt], generators), past=past) - apply(future_node_adds, generators,
                                                                                  past=past)

        case DictComp(key=key, value=value, generators=generators):
            return apply(all_node_needs, chain([key, value], generators), past=past) - apply(future_node_adds, generators,
                                                                                         past=past)

        case comprehension(iter=iter, ifs=ifs, target=target):
            return apply(all_node_needs, chain([iter, target], ifs), past=past)

        case BinOp(left=left, right=right):
            return apply(all_node_needs, [left, right], past=past)

        case BoolOp(values=values) | JoinedStr(values=values):
            return apply(all_node_needs, values, past=past)

        case UnaryOp(operand=operand):
            return all_node_needs(operand, past=past)

        case Compare(left=left, comparators=comparators):
            return all_node_needs(left, past=past) | apply(all_node_needs, comparators, past=past)

        case Slice(lower=lower, upper=upper):
            return apply(all_node_needs, [lower, upper], past=past)

        case arguments(posonlyargs=_, args=_, vararg=_, kwonlyargs=_, kw_defaults=kw_defaults, kwarg=_, defaults=defaults):
            return apply(all_node_needs, chain(kw_defaults, defaults) if kw_defaults else defaults, past=past)

        case Lambda(args=args, body=body):
            return all_node_needs(body, past=past) - future_node_adds(args)

        case arg(arg_name):
            return {arg_name}

        case Name(id=name_id):
            return {name_id}

        case Raise(exc=exc, cause=cause):
            return apply(all_node_needs, [exc, cause], past=past)

        case Assert(test=test, msg=msg):
            return apply(all_node_needs, [test, msg], past=past)

        case Delete(targets=targets):
            return apply(all_node_needs, targets, past=past)

        case ast.List(elts=elts) | ast.Tuple(elts=elts) | ast.Set(elts=elts):
            return apply(all_node_needs, elts, past=past)

        case ast.Dict(keys=keys, values=values):
            return apply(all_node_needs, chain(keys, values), past=past) if keys else set()

        case Match(subject = subject, cases = cases):
            return all_node_needs(subject) | apply(all_node_needs, cases)

        case match_case(pattern = pattern, guard = guard, body =body):
            return apply(all_node_needs, [pattern, guard]) | TimeNodeCost(body, set())

        case MatchValue(value = _) | MatchSingleton(value = _):
            return set()

        case MatchSequence(patterns = patterns) | MatchOr(patterns = patterns):
            return apply(all_node_needs, patterns)

        case MatchStar(name=_):
            return set()

        case MatchAs(pattern=pattern, name=name):
            return set()

        case MatchMapping(_,_,_):
            return set()

        case MatchClass(cls = cls, patterns=_, kwd_attrs=_, kwd_patterns=_):
            return all_node_needs(cls)

        case Constant() | \
             Load() | \
             ast.Pass | \
             Import() | \
             ImportFrom() | \
             alias() \
            :
            return set()

        case Global() | \
             Nonlocal() | \
             AsyncFor() | \
             AsyncWith() | \
             Await() \
            :
            error: str = f"{type(node)}  is not already implemented "
            raise NotImplementedError(error)
        case _:
            error_txt = f"Node type {type(node)} is Unhandled"
            raise NotImplementedError(error_txt)
