"""
Rémi Genet
17/10/2023
"""

from typing import Callable, Any, Tuple, Set, List, Optional, Union, Dict
import ast
from ast import Module,  stmt, AST
import logging
import sys
from interface import interface_import


console_logger: logging.Logger = logging.getLogger("console_logger")
console_handler: logging.StreamHandler = logging.StreamHandler(stream=sys.stdout)
console_logger.addHandler(console_handler)


all_node_needs: Callable[[Optional[AST],bool], Set[str]]
future_node_adds: Callable[[Optional[AST]], Set[str]]
prune_node: Callable[[AST],AST]
implied_globals_needs: Callable[[List[Set[str]], List[Set[str]], List[bool]],Tuple[Set[str], Set[str], Set[str]]]
implied_previous_needs: Callable[[List[Set[str]], List[Set[str]], List[bool]], Tuple[List[Set[str]], List[Set[str]], List[Set[str]]]]
GetNodeCategories: Callable[[], Dict[str, Tuple[type, ...]]]
parse: Callable[[str], Module]
get_source_segment: Callable[[str,AST],Optional[AST]]

all_node_needs, = interface_import("node_needs", fromlist=('all_node_needs',), level=0)
future_node_adds,= interface_import("node_adds", fromlist=('future_node_adds',), level=0)
prune_node, implied_globals_needs, implied_previous_needs = interface_import("node_selection", fromlist=('prune_node', 'implied_globals_needs', 'implied_previous_needs',), level=0)
GetNodeCategories, = interface_import("node_categories", fromlist=('GetNodeCategories',), level=0)
parse, get_source_segment = interface_import("utils", fromlist=('parse','get_source_segment'), level=0)



def MinimalNodesFunction(tree_nodes: List[AST], target: str, module_path: str,
                         node_categories: Dict[str, Tuple[type, ...]],
                         already_selected: Optional[List[bool]] = None) -> Union[List[AST], List[bool]]:
    needed_node: List[bool] = already_selected or [False for _ in tree_nodes]
    node_adds: List[Set[str]] = [future_node_adds(node) for node in tree_nodes]


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
            # Case when an already selected node that defines the target
            pass
    if not target_encountered_at:
        raise ImportError(f'Unable to locate the target {target} in the not already selected nodes')
    logging.debug('target_encountered_at', target_encountered_at)
    new_node_num: int = target_encountered_at[-1]
    needed_node[target_encountered_at[-1]] = True
    print('pruning', tree_nodes[new_node_num])
    tree_nodes[new_node_num] = prune_node(tree_nodes[new_node_num])
    node_adds: List[Set[str]] = [future_node_adds(node) for node in tree_nodes]
    past_costs: List[Set[str]] = [all_node_needs(node, past = True) for node in tree_nodes]
    global_costs: List[Set[str]] = [all_node_needs(node, past = False) for node in tree_nodes]
    past_needs, past_assets, missings = implied_previous_needs(node_adds, past_costs, needed_node)
    logging.debug(f"after adding: {tree_nodes[new_node_num]} num {node_num}")
    logging.debug('\n'.join([f'add={adds} |pasts= {pasts}|global= {globs}' for adds, pasts, globs in zip(node_adds, past_costs, global_costs)]))
    tmptxt="\n".join(str(missing) if i !=node_num else str(missing) +" stop here" for i, missing in enumerate(missings))
    logging.debug(f'missings: \n{tmptxt}')
    missing = missings[new_node_num]

    while missing and not all(needed_node[:new_node_num]):
        miss = missing.pop()
        try:
            selected_nodes: List[bool] = MinimalNodesFunction(tree_nodes[:new_node_num], miss, module_path,
                                                              node_categories,
                                                              already_selected=needed_node)
        except ImportError as e:
            raise ImportError(
                f'--> Error occurred searching in the past {miss} in order to define {target} - had {past_assets} and required {past_needs} <==> {missing}\n{e}\n ')
        except Exception as e:
            raise Exception(
                f'--> Error occurred searching in the past {miss} in order to define {target} - had {past_assets} and required {past_needs} <==> {missing}\n{e}\n')

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
                f'--> Error occurred searching at global {miss} in order to define {target} - had {assets} and required {needs} <==> {missing}\n{e}\n ')
        except Exception as e:
            raise Exception(
                f'--> Error occurred searching at global {miss} in order to define {target} - had {assets} and required {needs} <==> {missing}\n{e}\n')

        needed_node = [a or b for a, b in zip(needed_node, selected_nodes)]
        needs, assets, missing = implied_globals_needs(node_adds, past_costs, needed_node)

    if missing:
        raise ImportError(f'Missing Elements {missings} - to define {target} - had {assets} and required {needs}')
    if already_selected:
        return needed_node
    else:
        new_body: List[AST] = list((s for s, b in zip(tree_nodes, needed_node) if b))
        logging.info('Solution found with ', new_body)
        return new_body


def smart_import(module_path: str = 'C:/Users/remig/Desktop/pythonProject/test_files/a.py',
                 importer_globals: Optional[dict] = None, importer_locals: Optional[dict] = None,
                 targets: set = {'g', 'b'}, return_ast: Optional[bool] = False) \
        -> Union[Tuple[str, ...], Tuple[Callable[..., Any], ...]]:
    node_categories: Dict[str, Tuple[type, ...]] = GetNodeCategories()
    tree: Module = parse(module_path)
    tree_nodes: List[AST] = tree.body
    logging.debug(importer_globals, importer_locals)
    importer_globals = importer_globals or {}
    importer_locals = importer_locals or {}
    for trgt in targets:
        logging.info(f'searching target: {trgt}')
        new_body: List[AST] = MinimalNodesFunction(tree_nodes, trgt, module_path, node_categories)
        new_module = ast.increment_lineno(ast.fix_missing_locations(Module(body=new_body, type_ignores=[])), n=2)
        if return_ast:
            importer_locals[f'{trgt}'] = new_module
            continue
        importer_locals[f'{trgt}__AST_EXTRACT'] = new_module
        code = compile(new_module, filename='<ast>', mode='exec')
        exec(code, importer_globals, importer_locals)
        logging.info(f'{trgt} loaded')
    return tuple(importer_globals[target] for target in targets)



if __name__ == '__main__':
    import builtins
    debug = False
    console_logger.setLevel(logging.INFO)
    target = 'KK'
    file = 'extra/b.py'

    target_func, = smart_import(module_path=f'C:/Users/remig/Desktop/pythonProject/ASThetic/main/{file}',
                                importer_globals=globals(), importer_locals=locals(), targets={target},
                                return_ast=debug)

    logging.info('Normal Python', end=" ")
    try:
        test = builtins.__import__(file.replace('/','.').replace('.py', ''), globals(), locals() ,fromlist=[target])
        test_func = getattr(test, target)
        logging.info(test_func(5,6))
    except Exception as e:
        logging.error(e)
    if debug:
        logging.info(ast.dump(target_func, indent=4))
    else:
        logging.info('Rémi Python', target_func(9, 5))
