import ast
from typing import Callable, Any, Tuple, Set, List, Optional, Union, Iterable, Dict
from node_categories import GetNodeCategories
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
from itertools import chain



def parse(path: str) -> Module:
    with open(path, 'r') as file:
        tree = ast.parse(file.read(), filename=path)
    return tree

def get_source_segment(path: str, node) -> str | None:
    with open(path, 'r') as file:
        segment = ast.get_source_segment(file.read(), node=node)
    return segment

def apply(
        func: Callable[[Optional[AST], bool], Set[str]],
        nodes: Optional[Iterable[Optional[AST]]],
        past: bool = False
) -> Set[str]:
    return set.union(*(func(node, past) for node in nodes)) if nodes else set()

def FunctionsBodyCost(FuncNode: Union[FunctionDef, AsyncFunctionDef]) -> Set[str]:
    node_adds: List[Set[str]] = [future_node_adds(FuncNode.args)] + [future_node_adds(node) for node in FuncNode.body]
    node_costs: List[Set[str]] = [set("")] + [node_needs(node, past=True) for node in FuncNode.body]
    _, _, missing = implied_previous_needs(node_adds, node_costs, [True for _ in range(len(node_adds))])
    return set().union(*missing)
def future_node_adds(node: Optional[AST] = None, past: bool = False) -> Set[str]:
    match node:
        case ClassDef(name=name) | FunctionDef(name=name) | AsyncFunctionDef(name=name):
            return {name}

        case arguments(posonlyargs=posonlyargs, args=args, vararg=vararg, kwonlyargs=kwonlyargs, kwarg=kwarg):
            return apply(future_node_adds, chain(posonlyargs, args, [vararg, kwarg], kwonlyargs))

        case Assign(targets=targets):
            return apply(future_node_adds, targets)

        case AugAssign(target=target) | AnnAssign(target=target) | NamedExpr(target=target) | comprehension(
            target=target):
            return future_node_adds(target)

        case Import(names=names) | ImportFrom(names=names):
            return apply(future_node_adds, names)

        case alias(name=name, asname=asname):
            return {asname or name}

        case ast.arg(arg=arg):
            return {arg}

        case Name(id=id):
            return {id}

        case UnaryOp():
            return set()

        case None:
            return set()

        case Expr(_) | Attribute(_) | Subscript(_) | \
             keyword(_) | Return(_) | Yield(_) | \
             YieldFrom(_) | Starred(_) | FormattedValue(_):
            return set()

        case IfExp(_, _, _):
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

        case ast.List(_) | ast.Tuple(_) | ast.Set(_):
            return set()

        case ast.Dict(_, _):
            return set()

        case Constant() | Load() | ast.Pass:
            return set()

        case Global() | \
             Nonlocal() | \
             AsyncFor() | \
             AsyncWith() | \
             Await() | \
             Match() | \
             If() | \
             For() | \
             While() | \
             Break() | \
             Continue() | \
             Try() | \
             TryStar() | \
             ExceptHandler() | \
             With() | \
             withitem() \
            :
            error: str = f"{type(node)}  is not already implemented "
            raise NotImplementedError(error)

        case _:
            error_txt = f"Node type {type(node)} not implemented"
            raise NotImplementedError(error_txt)

def node_needs(node: Optional[AST] = None, past: bool = True) -> Set[str]:
    match node:
        case ClassDef(bases=bases, decorator_list=decorator_list, body=body):
            return apply(node_needs, chain(bases, decorator_list, body), past=past)

        case FunctionDef(decorator_list=decorator_list, args=args) | \
             AsyncFunctionDef(decorator_list=decorator_list, args=args):
            if past:
                print(node.name, "PAST NEED", apply(node_needs, decorator_list + [args]))
                return apply(node_needs, decorator_list + [args])
            else:
                print(node.name, "GLOBAL NEED", FunctionsBodyCost(node))
                return FunctionsBodyCost(node)

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
            return node_needs(value, past=past)

        case AnnAssign(annotation=annotation, value=value):
            return apply(node_needs, [annotation, value], past=past)

        case AugAssign(target=target, value=value):
            return apply(node_needs, [target, value], past=past)

        case Call(func=func, args=args, keywords=keywords):
            return apply(node_needs, chain([func], args, keywords), past=False)

        case IfExp(test=test, body=body, orelse=orelse):
            return apply(node_needs, [test, body, orelse], past=past)

        case ListComp(elt=elt, generators=generators) | \
             SetComp(elt=elt, generators=generators) | \
             GeneratorExp(elt=elt, generators=generators):
            return apply(node_needs, chain([elt], generators), past=past) - apply(future_node_adds, generators, past=past)

        case DictComp(key=key, value=value, generators=generators):
            return apply(node_needs, chain([key, value], generators), past=past) - apply(future_node_adds, generators,
                                                                                   past=past)

        case comprehension(iter=iter, ifs=ifs, target=target):
            return apply(node_needs, chain([iter, target], ifs), past=past)

        case BinOp(left=left, right=right):
            return apply(node_needs, [left, right], past=past)

        case BoolOp(values=values) | JoinedStr(values=values):
            return apply(node_needs, values, past=past)

        case UnaryOp(operand=operand):
            return node_needs(operand, past=past)

        case Compare(left=left, comparators=comparators):
            return node_needs(left, past=past) | apply(node_needs, comparators, past=past)

        case Slice(lower=lower, upper=upper):
            return apply(node_needs, [lower, upper], past=past)

        case arguments(kw_defaults=kw_defaults, defaults=defaults):
            return apply(node_needs, chain(kw_defaults, defaults) if kw_defaults else defaults, past=past)

        case Lambda(args=args, body=body):
            return node_needs(body, past=past) - future_node_adds(args)

        case arg(arg_name):
            return {arg_name}

        case Name(id=name_id):
            return {name_id}

        case Raise(exc=exc, cause=cause):
            return apply(node_needs, [exc, cause], past=past)
        case Assert(test=test, msg=msg):
            return apply(node_needs, [test, msg], past=past)
        case Delete(targets=targets):
            return apply(node_needs, targets, past=past)
        case ast.List(elts=elts) | ast.Tuple(elts=elts) | ast.Set(elts=elts):
            return apply(node_needs, elts, past=past)
        case ast.Dict(keys=keys, values=values):
            return apply(node_needs, chain(keys, values), past=past) if keys else set()
        case Constant() | \
             Load() | \
             ast.Pass | \
             Import() | \
             ImportFrom() | \
             alias() | \
             None \
            :
            return set()
        case Global() | \
             Nonlocal() | \
             AsyncFor() | \
             AsyncWith() | \
             Await() | \
             Match() | \
             If() | \
             For() | \
             While() | \
             Break() | \
             Continue() | \
             Try() | \
             TryStar() | \
             ExceptHandler() | \
             With() | \
             withitem() \
            :
            error: str = f"{type(node)}  is not already implemented "
            raise NotImplementedError(error)
        case _:
            error_txt = f"Node type {type(node)} is Unhandled"
            raise NotImplementedError(error_txt)


def implied_globals_needs(node_adds: List[Set[str]], node_costs: List[Set[str]], selected: List[bool]) -> Tuple[
    Set[str], Set[str], Set[str]]:
    assets: Set[str] = set().union(*(s for s, b in zip(node_adds, selected) if b))
    needs: Set[str] = set().union(*(s for s, b in zip(node_costs, selected) if b))
    missing: Set[str] = needs - assets
    return assets, needs, missing


def implied_previous_needs(node_adds: List[Set[str]], node_costs: List[Set[str]], selected: List[bool]) -> Tuple[
    List[Set[str]], List[Set[str]], List[Set[str]]]:
    assets = [set().union(*(s for s, b in zip(node_adds[:end], selected[:end]) if b)) if any(selected[:end]) else set()
              for end in range(len(node_adds)+1)]
    needs = [set().union(*(s for s, b in zip(node_costs[:end], selected[:end]) if b)) if any(selected[:end]) else set()
             for end in range(len(node_adds)+1)]
    if needs[0]:
        raise ImportError(f'You should not have first need different from 0 {needs[0]}')
    missing: List[Set[str]] = [needs[0]] + [n - a for n, a in zip(needs[1:], assets[:-1])]
    return assets, needs, missing


def MinimalNodesFunction(tree_nodes: List[stmt], target: str, module_path: str,
                         node_categories: Dict[str, Tuple[type, ...]],
                         already_selected: Optional[List[bool]] = None) -> Union[List[stmt], List[bool]]:
    needed_node: List[bool] = already_selected or [False for _ in tree_nodes]
    node_adds: List[Set[str]] = [future_node_adds(node) for node in tree_nodes]
    past_costs: List[Set[str]] = [node_needs(node) for node in tree_nodes]
    global_costs: List[Set[str]] = [node_needs(node, past=False) for node in tree_nodes]

    target_encountered_at: List[int] = []
    for node_num, node in enumerate(tree_nodes):
        node_info: str = f'line {node.lineno} in {module_path}\n{get_source_segment(module_path, node)}\nNode type {type(node).__name__}'
        error_str: str = node_info
        if isinstance(node, node_categories['unpossible_at_top']):
            error_str += ' in top code level is impossible - Python cannot compile this file'
            raise SyntaxError(error_str)
        elif isinstance(node, node_categories['not_yet_handled']):
            error_str += ' is unvalid - SmartCompiler does not handled it for the moment - Only defines functions and class in the file idealy'
            raise SyntaxError(error_str)
        elif not isinstance(node, node_categories['valid']):
            error_str += ' in top code level is Unknown to SmartCompiler'
            raise SyntaxError(error_str)
        elif target in node_adds[node_num] and not needed_node[node_num]:
            target_encountered_at.append(node_num)
        else:
            # Case when an already selected node defines the target
            pass
    if not target_encountered_at:
        raise ImportError(f'Unable to locate the target {target} in the not already selected nodes')
    print('target_encountered_at', target_encountered_at)
    new_node_num: int = target_encountered_at[-1]
    needed_node[target_encountered_at[-1]] = True
    past_needs, past_assets, missings = implied_previous_needs(node_adds, past_costs, needed_node)
    missing = missings[new_node_num]
    selected_nodes: List[bool]
    while missing and not all(needed_node[:new_node_num]):
        miss = missing.pop()
        try:
            selected_nodes = MinimalNodesFunction(tree_nodes[:new_node_num], miss, module_path,
                                                              node_categories,
                                                              already_selected=needed_node)
        except ImportError as e:
            raise ImportError(
                f'--> Error occured searching in the past {miss} in order to define {target} - had {past_assets} and required {past_needs} <==> {missing}\n{e}\n ')
        except Exception as e:
            raise Exception(
                f'--> Error occured searching in the past {miss} in order to define {target} - had {past_assets} and required {past_needs} <==> {missing}\n{e}\n')

        needed_node = [a or b for a, b in zip(needed_node[:new_node_num], selected_nodes[:new_node_num])] + needed_node[
                                                                                                            new_node_num:]
        past_needs, past_assets, missings = implied_previous_needs(node_adds, past_costs, needed_node)
        missing = missings[new_node_num]

    needs, assets, missing = implied_globals_needs(node_adds, global_costs, needed_node)
    while missing and not all(needed_node):
        miss = missing.pop()
        try:
            selected_nodes = MinimalNodesFunction(tree_nodes, miss, module_path, node_categories,
                                                              already_selected=needed_node)
        except ImportError as e:
            raise ImportError(
                f'--> Error occured searching at global {miss} in order to define {target} - had {assets} and required {needs} <==> {missing}\n{e}\n ')
        except Exception as e:
            raise Exception(
                f'--> Error occured searching at global {miss} in order to define {target} - had {assets} and required {needs} <==> {missing}\n{e}\n')

        needed_node = [a or b for a, b in zip(needed_node, selected_nodes)]
        needs, assets, missing = implied_globals_needs(node_adds, past_costs, needed_node)

    if missing:
        raise ImportError(f'Missing Elements {missings} - to define {target} - had {assets} and required {needs}')
    if already_selected:
        return needed_node
    else:
        new_body: List[stmt] = list((s for s, b in zip(tree_nodes, needed_node) if b))
        print('Solution found with ', new_body)
        return new_body


def smart_import(module_path: str = 'C:/Users/remig/Desktop/pythonProject/test_files/testparse.py',
                 importer_globals: Optional[dict] = None, importer_locals: Optional[dict] = None,
                 targets: set = {'g', 'b'}, return_ast: bool = False) \
        -> Union[Tuple[str, ...], Tuple[Callable[..., Any], ...]]:
    node_categories: Dict[str, Tuple[type, ...]] = GetNodeCategories()
    tree: Module = parse(module_path)
    tree_nodes: List[stmt] = tree.body
    print(importer_globals, importer_locals)
    importer_globals = importer_globals or {}
    importer_locals = importer_locals or {}
    for target in targets:
        print(f'searching target: {target}')
        new_body: List[stmt] = MinimalNodesFunction(tree_nodes, target, module_path, node_categories)
        if return_ast:
            importer_locals[target] = Module(body=new_body, type_ignores=[])
        else:
            code = compile(Module(body=new_body, type_ignores=[]), filename='<ast>', mode='exec')
            exec(code, importer_globals, importer_locals)
        print(f'{target} loaded')
    return tuple(importer_globals[target] for target in targets)


if __name__ == '__main__':
    debug = False
    h, = smart_import(importer_globals=globals(), importer_locals=locals(), targets={'h'}, return_ast=debug)

    print('Normal Python', end=" ")
    try:
        from testparse import h as test_h
        print(test_h(3))
    except Exception as e:
        print(e)
    if debug:
        print(ast.dump(h, indent=4))
    else:
        print('ASThetic Python', h(3))
