"""
Rémi Genet
17/10/2023
"""
import ast
from ast import Module, AST




def parse(path: str) -> Module:
    with open(path, 'r') as file:
        tree = ast.parse(file.read(), filename=path)
    return tree


def get_source_segment(path: str, node: AST) -> str | None:
    with open(path, 'r') as file:
        segment = ast.get_source_segment(file.read(), node=node)
    return segment

