"""
Rémi Genet
17/10/2023
"""
from typing import Tuple, Dict, Self, Callable, Optional, Any
import builtins
import types



class InterfaceNode:
    name: str = None
    children: Dict[Self,Self] = None
    parent: Optional[Self] = None
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.children: Dict[str,Self] = {}
        self.parent: Optional[Self] = None

    def add_child(self, child: Self) -> Self:
        self.children[child.name] = child
        child.parent = self
        return self.children[child.name]

    def __str__(self: Self) -> str:
        return f"{self.__class__.__name__}({self.name})"

    def __repr__(self: Self) -> str:
        return f"{self.__class__.__name__}({self.name})"



class NewNode(InterfaceNode):

    def __init__(
            self, *args, level: int, is_leaf: bool, **kwargs
    ) -> None:
        self._level = level
        self._is_leaf = is_leaf
        self._module = None
        self._loaded_object = None
        super().__init__(*args, **kwargs)

    @property
    def module(self: Self):
        if self._loaded_object is not None:
            return self._loaded_object
        elif (self._is_leaf or not len(self.children)) and self.parent is not None:
            return self.parent.load_module(
                fromlist=(self.name,),
                level=self._level,
            )
        return self.load_module(fromlist=tuple(), level=self._level)

    @property
    def loaded_object(self):
        if self._loaded_object is None:
            loaded_object = getattr(self.module, self.name)
            imp_child = ImpNode(
                name=self.name, loaded_object=loaded_object
            )
            self._loaded_object = self.add_child(imp_child)
        return self._loaded_object

    @property
    def full_import(self: Self) -> str:
        if not self.parent.parent and len(self.children) > 0:
            return self.name
        return f"{self.parent.full_import}.{self.name}"


    def load_module(self: Self, fromlist: Tuple[str,...], level: int):
        return builtins.__import__(
            self.full_import,
            fromlist=list(fromlist),
            level=level,
        )

    def __call__(self, *args, **kwargs) -> Any:
        return self.loaded_object(*args, **kwargs)

class ImpNode(InterfaceNode):

    def __init__(self, *args, loaded_object, **kwargs):
        super().__init__(*args, **kwargs)
        self._loaded_object = loaded_object

    def __call__(self, *args, **kwargs):
        if isinstance(self._loaded_object, types.FunctionType):
            return self._loaded_object(*args, **kwargs)
        instance = self._loaded_object(*args, *kwargs)
        obj = InstNode(
            f"{self.name} n{len(self.children)}", instance=instance
        )
        return self.add_child(obj)


class InstNode(InterfaceNode):
    _search_objects = ["instance", ""]

    def __init__(self, *args, instance, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance

    def __call__(self, *args, **kwargs):
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


    def import__(self, name: str, fromlist:Tuple[str]=(), level: int =0) -> Self:
        if globals()["__name__"] == "_frozen_importlib_external":
            return builtins.__import__(name = name, fromlist = fromlist, level = level)
        return self.parse_import(name=name, fromlist=fromlist, level=level)

    def parse_import(self, name: str, fromlist: Tuple[str], level: int=0) -> Self:
        name_parts = name.split(".")
        current_node = self._result
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


def interface_import(name:str, fromlist: Tuple[str,...]=(), level:int = 0) -> Tuple[Callable[[...],...],...]:
    tree = ImportTree()
    tree.import__(name, fromlist=fromlist, level=level)
    parts = name.split('.')
    node = getattr(tree, parts[0])
    for part in parts[1:]:
        node = node.childrens[part]
    print(node, node.children)
    return tuple([node.children[trgt] for trgt in fromlist])

