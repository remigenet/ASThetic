"""
Rémi Genet
17/10/2023

TreeImport:
Basic Tree Implementation of a LazyLoader
Used as an interface it catches most of the circular dependencies issues that usually arise

Still Beta Version here

Doesn't relly on any external library

To use:
from interface import interface_import

# For 1 import do not forget to
all_node_needs: Callable[[Optional[AST],bool], Set[str]] = interface_import("node_needs", fromlist=('all_node_needs',), level=0)[0]
prune_node, implied_globals_needs, implied_previous_needs = interface_import("node_selection", fromlist=('prune_node', 'implied_globals_needs', 'implied_previous_needs',), level=0)


"""
from __future__ import annotations

import builtins
import types
from typing import Tuple, Dict, Self, Optional, Any, Union, List


class InterfaceNode:
    name: str = None
    children: Dict[str, InterfaceNode] = None
    parent: Optional[InterfaceNode] = None
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.children: Dict[str,Self] = {}
        self.parent: Optional[Self] = None

    def add_child(self, child: InterfaceNode) -> InterfaceNode:
        self.children[child.name] = child
        child.parent = self
        return self.children[child.name]

    def __str__(self: InterfaceNode) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self: InterfaceNode) -> str:
        return f"{self.__class__.__name__}({self.name})"



class NewNode(InterfaceNode):

    def __init__(
            self, *args, level: int, is_leaf: bool, **kwargs
    ) -> None:
        self._level: int = level
        self._is_leaf: bool = is_leaf
        self._module: Optional[ImpNode] = None
        self._loaded_object: Optional[ImpNode] = None
        super().__init__(*args, **kwargs)

    @property
    def module(self: NewNode) -> [types.ModuleType | ImpNode]:
        if self._loaded_object is not None:
            return self._loaded_object
        elif (self._is_leaf or not len(self.children)) and self.parent is not None:
            return self.parent.load_module(
                fromlist=(self.name,),
                level=self._level,
            )
        return self.load_module(fromlist=tuple(), level=self._level)

    @property
    def loaded_object(self: NewNode) -> ImpNode:
        if self._loaded_object is None:
            loaded_object: object = getattr(self.module, self.name)
            imp_child: ImpNode = ImpNode(
                name=self.name, loaded_object=loaded_object
            )
            self._loaded_object = self.add_child(imp_child)
        return self._loaded_object

    @property
    def full_import(self: NewNode) -> str:
        if not self.parent.parent and len(self.children) > 0:
            return self.name
        return f"{self.parent.full_import}.{self.name}"

    def load_module(self: Self, fromlist: Tuple[str, ...], level: int) -> types.ModuleType:
        return builtins.__import__(
            self.full_import,
            fromlist=list(fromlist),
            level=level,
        )

    def __call__(self, *args, **kwargs) -> Any:
        return self.loaded_object(*args, **kwargs)

class ImpNode(InterfaceNode):

    def __init__(self, *args, loaded_object: ImpNode, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._loaded_object: ImpNode = loaded_object

    def __call__(self, *args, **kwargs) -> Union[Any, InstNode]:
        if isinstance(self._loaded_object, types.FunctionType):
            return self._loaded_object(*args, **kwargs)
        instance: object = self._loaded_object(*args, *kwargs)
        obj: InstNode = InstNode(
            f"{self.name} n{len(self.children)}", instance=instance
        )
        return self.add_child(obj)


class InstNode(InterfaceNode):
    _search_objects = ["instance", ""]

    def __init__(self, *args, instance, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance: object = instance

    def __call__(self, *args, **kwargs) -> Any:
        return self.instance(*args, **kwargs)


class ImportTree:
    _instance: Self= None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> None:
        if not cls._instance:
            cls._instance = super(__class__, cls).__new__(cls)
        return cls._instance
    def __init__(self) -> None:
        if not self._initialized:
            self._result = NewNode(
                "",
                level=0,
                is_leaf=False,
            )
            __class__._initialized = True

    def import__(self, name: str, fromlist: Tuple[str] = (), level: int = 0) -> [ImportTree | types.ModuleType]:
        if globals()["__name__"] == "_frozen_importlib_external":
            return builtins.__import__(name = name, fromlist = fromlist, level = level)
        return self.parse_import(name=name, fromlist=fromlist, level=level)

    def parse_import(self, name: str, fromlist: Tuple[str], level: int = 0) -> ImportTree:
        name_parts: List[str] = name.split(".")
        current_node: NewNode = self._result
        current_path = ""
        for part in name_parts:
            current_path = f"{current_path}.{part}" if current_path else part
            child_node = current_node.children.get(part)
            if child_node is not None:
                current_node = child_node
                continue
            child_node = NewNode(
                part,
                level=level,
                is_leaf=False,
            )
            child_node = current_node.add_child(
                child_node
            )
            setattr(self, current_path, child_node)
            current_node = child_node

        for item in fromlist:
            if item in current_node.children:
                continue
            leaf_node = NewNode(
                item,
                level=level,
                is_leaf=True,
            )
            current_node.add_child(leaf_node)
            setattr(self, item, leaf_node)
        return self


def interface_import(name: str, fromlist: Tuple[str, ...] = (), level: int = 0) -> tuple[InterfaceNode, ...]:
    tree: ImportTree = ImportTree()
    tree.import__(name, fromlist=fromlist, level=level)
    parts: List[str] = name.split('.')
    node: InterfaceNode = getattr(tree, parts[0])
    for part in parts[1:]:
        node = node.children[part]
    return tuple([node.children[trgt] for trgt in fromlist])

