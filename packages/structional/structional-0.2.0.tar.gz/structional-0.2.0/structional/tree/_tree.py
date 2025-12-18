# ruff: noqa: A001, PLC2801

import dataclasses
import enum
import functools as ft
import types
import typing
from collections.abc import Callable, Hashable
from typing import (
    Any,
    cast,
    ClassVar,
    Generic,
    NamedTuple,
    overload,
    TYPE_CHECKING,
    TypeAlias,
    TypeVar,
    TypeVarTuple,
)

import wadler_lindig as wl

from .._struct import is_abstract_struct, is_magic, Struct


_T = TypeVar("_T")
_Ts = TypeVarTuple("_Ts")


if not TYPE_CHECKING and getattr(typing, "GENERATING_DOCUMENTATION", False):

    class Tree(Generic[_T]):
        pass

    Tree.__module__ = "structional.tree"
else:
    if TYPE_CHECKING:
        # We use `Callable`, rather than the more accurate `types.FunctionType` and
        # `types.MethodType`, because pyright doesn't support the latter two.
        Tree: TypeAlias = (
            _T
            | tuple["Tree[_T]", ...]
            | dict[str, "Tree[_T]"]
            | list["Tree[_T]"]
            | Struct
            | ft.partial
            | Callable
        )
    else:
        Tree: TypeAlias = (
            _T
            | tuple
            | dict
            | list
            | Struct
            | ft.partial
            | types.FunctionType
            | types.MethodType
        )


class StructureFrom(enum.Enum):
    """Represents the possible ways in which `tree.map` can choose the structure to map
    over.
    """

    ALL = enum.auto()
    FIRST = enum.auto()
    COMMON = enum.auto()


class ListGetItem(Struct):
    item: int


class TupleGetItem(Struct):
    item: int


class NamedTupleGetAttr(Struct):
    name: str


class DictGetItem(Struct):
    item: Hashable


class StructDict(Struct):
    pass


class PartialFunc(Struct):
    pass


class PartialArgs(Struct):
    pass


class PartialKeywords(Struct):
    pass


class MethodFunc(Struct):
    pass


class MethodSelf(Struct):
    pass


class ClosureItem(Struct):
    item: int


Piece: TypeAlias = (
    ListGetItem
    | TupleGetItem
    | NamedTupleGetAttr
    | DictGetItem
    | StructDict
    | PartialFunc
    | PartialArgs
    | PartialKeywords
    | MethodFunc
    | MethodSelf
    | ClosureItem
)


class Path(Struct):
    """Represents a path through a tree structure. Typically obtained by using
    `tree.map(..., with_path=True)`. Individual elements of the path are accessible on
    its `.pieces` attribute.
    """

    pieces: tuple[Piece, ...]

    def __init__(self, *pieces: Piece):
        self.pieces = pieces

    def push(self, *pieces: Piece) -> "Path":
        """Returns a new `Path` with the extra piece(s) appended. The original path
        remains unchanged."""
        return Path(*self.pieces, *pieces)

    # Make these available under `Path` to avoid complicating the main namespace.
    ListGetItem: ClassVar[type] = ListGetItem
    TupleGetItem: ClassVar[type] = TupleGetItem
    NamedTupleGetAttr: ClassVar[type] = NamedTupleGetAttr
    DictGetItem: ClassVar[type] = DictGetItem
    StructDict: ClassVar[type] = StructDict
    PartialFunc: ClassVar[type] = PartialFunc
    PartialArgs: ClassVar[type] = PartialArgs
    PartialKeywords: ClassVar[type] = PartialKeywords
    MethodFunc: ClassVar[type] = MethodFunc
    MethodSelf: ClassVar[type] = MethodSelf
    ClosureItem: ClassVar[type] = ClosureItem
    Piece: ClassVar = Piece


class Lens(Struct, Generic[_T, *_Ts]):
    """Specifes a location within a tree structure, typically for specifying where
    `tree.map` or `tree.replace` should apply.

    Supports `.attribute_lookup` and `[item_lookup]` to specify locations within the
    tree.

    !!! Example

        ```python
        lens = tree.Lens(some_tree).some_attr[0].foo["hello"]

        # Then used as:
        ... = tree.map(lens, ...)
        ... = tree.replace(lens, ...)
        ```
    """

    if TYPE_CHECKING:

        def __init__(self, tree: _T, *trees: *_Ts): ...
    else:
        # Put this outside of typechecking, so that e.g. `.root` doesn't get suggested
        # as an autocomplete.
        roots: tuple[Tree, ...]
        trees: tuple[Tree, ...]
        path: Path

        def __init__(self, tree: Tree, *trees: Tree):
            """**Arguments:**

            - `tree`: the tree to specify the location within.
            - `*trees`: additional trees, for use when applying a function over multiple
                trees with `tree.map`.
            """
            trees = (tree, *trees)
            self.roots = trees
            self.trees = trees
            self.path = Path()

    def _new(self, trees: list[_T], path: Path) -> "Lens":
        out = object.__new__(Lens)
        object.__setattr__(out, "roots", object.__getattribute__(self, "roots"))
        object.__setattr__(out, "trees", tuple(trees))
        object.__setattr__(out, "path", path)
        return out

    def __getattribute__(self, name: str, /) -> "Lens":
        if is_magic(name) and name not in {"__closure__", "__self__", "__func__"}:
            # E.g. `__dataclass_fields__`
            return object.__getattribute__(self, name)
        trees = object.__getattribute__(self, "trees")
        path = object.__getattribute__(self, "path")
        new = object.__getattribute__(self, "_new")
        typ = _get_type(trees)
        if issubclass(typ, tuple) and hasattr(typ, "_fields"):
            return new(
                [getattr(tree, name) for tree in trees],
                path.push(Path.NamedTupleGetAttr(name)),
            )
        elif issubclass(typ, Struct):
            for f in dataclasses.fields(typ):
                if f.name == name:
                    break
            else:
                # In particular prohibit things like `__doc__`.
                raise AttributeError(f"Dataclass has no field {name}")
            return new(
                [tree.__dict__[name] for tree in trees],
                path.push(Path.StructDict(), Path.DictGetItem(name)),
            )
        elif typ is ft.partial:
            if name == "func":
                return new([tree.func for tree in trees], path.push(Path.PartialFunc()))
            elif name == "args":
                return new([tree.args for tree in trees], path.push(Path.PartialArgs()))
            elif name == "keywords":
                return new(
                    [tree.keywords for tree in trees], path.push(Path.PartialKeywords())
                )
            else:
                raise ValueError(
                    f"Cannot access attribute `{name}` on `functools.partial`."
                )
        elif typ is types.MethodType:
            if name == "__func__":
                return new(
                    [tree.__func__ for tree in trees], path.push(Path.MethodFunc())
                )
            elif name == "__self__":
                return new(
                    [tree.__self__ for tree in trees], path.push(Path.MethodSelf())
                )
            else:
                raise ValueError(
                    f"Cannot access attribute `{name}` on `types.MethodType`."
                )
        elif typ is types.FunctionType:
            if name == "__closure__":
                out = _LensClosureHelper1(cast(Lens[types.FunctionType], self))
                return cast(Lens, out)  # lie about the return type, it's fine
            else:
                raise ValueError(
                    f"Cannot access attribute `{name}` on `types.FunctionType`."
                )
        else:
            raise TypeError(
                f"{type(trees[0])} is not a tree type that `.attribute_lookup` can be "
                "applied to."
            )

    def __getitem__(self, item: Any, /) -> "Lens":
        trees = object.__getattribute__(self, "trees")
        path = object.__getattribute__(self, "path")
        new = object.__getattribute__(self, "_new")
        typ = _get_type(trees)
        if issubclass(typ, list):
            return new(
                [tree[item] for tree in trees], path.push(Path.ListGetItem(item))
            )
        elif issubclass(typ, tuple):
            try:
                fields = typ._fields  # pyright: ignore[reportAttributeAccessIssue]
            except AttributeError:
                return new(
                    [tree[item] for tree in trees], path.push(Path.TupleGetItem(item))
                )
            else:
                # Canonicalize namedtuple getitem into getattr, since that is what
                # `tree.map` does.
                return new(
                    [tree[item] for tree in trees],
                    path.push(Path.NamedTupleGetAttr(fields[item])),
                )
        elif issubclass(typ, dict):
            return new(
                [tree[item] for tree in trees], path.push(Path.DictGetItem(item))
            )
        else:
            raise TypeError(
                f"{type(trees[0])} is not a tree type that `[item_lookup]` can be "
                "applied to."
            )


def _one_type(trees) -> bool:
    type0 = type(trees[0])
    return all(type(tree) == type0 for tree in trees)  # noqa: E721


def _get_type(trees):
    if _one_type(trees):
        return type(trees[0])
    else:
        raise TypeError("Elements of `tree.Lens` had different types.")


class _LensClosureHelper1(Struct):
    lens: Lens[types.FunctionType]

    def __getitem__(self, item: int):
        return _LensClosureHelper2(self.lens, item)


class _LensClosureHelper2(Struct):
    lens: Lens[types.FunctionType]
    item: int

    def __getattribute__(self, name: str, /) -> Any:
        if is_magic(name):
            return object.__getattribute__(self, name)
        elif name == "cell_contents":
            lens = object.__getattribute__(self, "lens")
            item = object.__getattribute__(self, "item")
            trees = object.__getattribute__(lens, "trees")
            path = object.__getattribute__(lens, "path")
            new = object.__getattribute__(lens, "_new")
            return new(
                [tree.__closure__[item].cell_contents for tree in trees],
                path.push(Path.ClosureItem(item)),
            )
        else:
            raise ValueError(f"Closure has no (tree-accessible) attribute {name}")


# Python doesn't have higher-kinded type variables:
# https://github.com/python/typing/issues/548
# As such we cannot annotate directly that `tree.map` will both (a) preserve tree
# structures, and (b) map leaf types.
# We elect to declare that it preserves structure.


@overload
def map(
    x: Lens[_T],
    *,
    fn: Callable[..., Any],
    is_leaf: None | Callable[[Any], bool] = None,
    structure_from: None | StructureFrom = None,
    with_path: bool = False,
) -> _T: ...


@overload
def map(
    x: Lens[_T, *_Ts],
    *,
    fn: Callable[..., Any],
    is_leaf: None | Callable[[Any], bool] = None,
    structure_from: StructureFrom,  # not optional when we have multiple trees
    with_path: bool = False,
) -> _T: ...


@overload
def map(
    x: _T,
    *,
    fn: Callable[..., Any],
    is_leaf: None | Callable[[Any], bool] = None,
    structure_from: None | StructureFrom = None,
    with_path: bool = False,
) -> _T: ...


@overload
def map(
    x: _T,
    *xs: Tree,
    fn: Callable[..., Any],
    is_leaf: None | Callable[[Any], bool] = None,
    structure_from: StructureFrom,  # not optional when we have multiple trees
    with_path: bool = False,
) -> _T: ...


# We have a pyright-ignore here because the type annotations are the ones we want to
# appear in the documentation, which are a bit of a simplification to the real
# overloads.
def map(  # pyright: ignore[reportInconsistentOverload]
    *xs: _T | Lens[_T],
    fn: Callable[..., Any],
    is_leaf: None | Callable[[Any], bool] = None,
    structure_from: None | StructureFrom = None,
    with_path: bool = False,
) -> _T:
    """Given trees `*xs` with the same structure, this calls `y_i = fn(*xs_i)` for each
    leaf index `i`. The result will be a tree with the same structure and with the `i`th
    leaf having value `y_i`.

    Nontrivial tree types are tuples, dictionaries, lists, `Struct`s,
    `functools.partial`, methods, and function closures.

    The order of iteration is deterministic. (This is the reason that sets are not
    treated as non-leaf types.)

    **Arguments:**

    - `*xs`: The trees to operate over, as described above. This may also be wrapped in
        a `tree.Lens`, to specify only part of a tree structure to operate on. The rest
        of the tree will remain unchanged.
    - `fn`: The function to call on all leaves of the structure.
    - `is_leaf`: Optional callable. Will be called on each node of `xs[0]`. If the
        callable returns `True`, then this will be treated as leaf.
    - `structure_from`: What tree structure to map over. This is required if and only if
        multiple trees are provided, that is to say if `len(xs) > 1`.
        1. If `StructureFrom.ALL` is used, then we require that every one of `xs` to
            have the exact same structure, and will raise an error if not.
        2. If `StructureFrom.FIRST`, then the tree structure of the first tree `xs[0]`
            will be used. (For those coming from JAX, this is JAX's default.) In this
            case we require only that `xs[0]` be a tree-prefix for all of `xs`. For
            example, `tree.map([1], [[2]], fn=fn)` is valid, and it will return
            `[fn(1, [2])]`.
        3. If `StructureFrom.COMMON` is used, then we will locate the largest common
            tree-prefix and apply `fn` to those. For example this means that
            `tree.map([(1,)], [(2, 3)], fn=fn, structure_from=StructureFrom.COMMON)`
            returns `[fn((1,), (2, 3))]`, despite the fact that `(1,)` and `(2, 3)` are
            trees with different structures. As another example,
            `tree.map(..., fn=lambda _: None, structure_from=StructureFrom.COMMON)` can
            be used to find the shared tree-prefix (with `None` leaves) of some trees.
    - `with_path`: If `False` (the default), then `fn` is called as `fn(*xs)` for each
        leaf. If `True`, then `fn` is called as `fn(*xs, path=path)`, with `path` being
        a `Path` object that indicates the path to the current leaf.

    !!! warning

        Note that using `structure_from=StructureFrom.COMMON` can easily hide mistakes
        in the tree structure. It should be used very rarely.

    **Returns:**

    A tree-mapped `fn` over the provided trees.

    **Raises:**

    A `tree.StructureError` if:

    - `structure_from` is `StructureFrom.ALL` and trees do not match exactly.
    - `structure_from` is `StructureFrom.FIRST` and `x` is not a tree-prefix for all of
        `xs`.

    !!! info

        Some useful recipes are:

        1. To get just the leaves:
            ```python
            leaves = []
            tree.map(tree, fn=leaves.append)
            ```

        2. To get just the structure:
            ```python
            structure = tree.map(tree, fn=lambda _: None)
            ```

        3. To extend with a custom tree type:
            ```python
            def my_map(x, *, fn):
                def wrapped_fn(x):
                    if type(x) is MyTypeWithFooAttr:
                        return MyTypeWithFooAttr(foo=tree.map(x.foo, fn=wrapped_fn))
                    else:
                        return fn(x)
                return tree.map(x, fn=wrapped_fn)
            ```

    !!! FAQ

        Function closures are one of the more unusual, but important, kinds of
        nontrivial tree type. In particular this prevents a common footgun for a
        particular more advanced use-case:
        ```python
        def prints_arguments(fn):
            def wrapped(*args, **kwargs):
                print(f"Called with {args} and {kwargs}")
                return fn(*args, **kwargs)
            return wrapped

        class Adder(Struct):
            x: int

            def __call__(self, y: int) -> int:
                return self.x + y

        # This is a nontrivial tree.
        adds_three = Adder(3)
        # This is still a nontrivial tree.
        adds_three_loud = prints_arguments(adds_three)
        ```

        Meanwhile PyTorch modules are intentionally not a nontrivial tree type. PyTorch
        modules have inherently an OOP/mutable design, whilst trees are inherently based
        around a functional/immutable design. Too easy to footgun when mixing these
        approaches -- better to explicitly be in just one of these two regimes.
    """
    __tracebackhide__ = True
    if len(xs) == 0:
        raise ValueError("Need at least one tree argument for `tree.map(...)`.")
    if type(xs[0]) is Lens:
        if len(xs) > 1:
            raise ValueError(
                "Do not call as `tree.map(Lens(tree), *other_trees, ...)`, use "
                "`tree.map(Lens(tree, *other_trees), ...)` instead."
            )
        assert len(xs) == 1
        pieces = list(object.__getattribute__(xs[0], "path").pieces)
        xs = object.__getattribute__(xs[0], "roots")
    else:
        pieces = []
    if len(xs) > 1 and structure_from is None:
        raise ValueError(
            "If calling `tree.map` with multiple trees then the "
            "`tree.map(..., structure_from=...)` argument must be provided."
        )
    cache = dict[int, Any]()
    return _TreeMap(fn, is_leaf, structure_from, cache, pieces, 0, with_path).recurse(
        *xs
    )


class StructureError(Exception):
    """Raised to indicate that a `tree.map` was performed over incompatible
    structures."""


_Value = TypeVar("_Value")


class Static(Struct, Generic[_Value]):
    """Wraps a value into an empty tree. For example, `[]` is an empty tree, and a
    `tree.map` over it changes nothing.

    This class offers a way to build such an empty tree, but with arbitrary metadata
    (the wrapped value) attached.
    """

    value: _Value


@dataclasses.dataclass(frozen=False)
class _TreeMap:
    fn: Callable
    is_leaf: None | Callable
    structure_from: None | StructureFrom
    cache: dict
    pieces: list[Path.Piece]
    piece_index: int
    with_path: bool

    def recurse(self, x, *xs):
        __tracebackhide__ = True
        if self.piece_index == len(self.pieces) and (
            is_registered_leaf_type(type(x))
            or (self.is_leaf is not None and self.is_leaf(x))
        ):
            return self.call(x, xs)
        elif isinstance(x, Static):
            if any(type(xi) is not Static or xi.value is not x.value for xi in xs):
                return self.call_or_raise(
                    x, xs, "All tree-mapped `Static` must be the same object."
                )
            return x
        elif isinstance(x, (tuple, list)):  # This branch also handles named tuples.
            if not _one_type((x, *xs)):
                return self.call_or_raise(
                    x, xs, "All tree-mapped objects must have the same structure."
                )
            if any(len(x) != len(xi) for xi in xs):
                return self.call_or_raise(
                    x, xs, "All tree-mapped tuples/lists must have the same length."
                )
            if isinstance(x, tuple):
                if hasattr(x, "_fields"):
                    t = lambda i: Path.NamedTupleGetAttr(cast(NamedTuple, x)._fields[i])
                    make = lambda v: type(x)(*v)
                else:
                    t = Path.TupleGetItem
                    make = type(x)
            else:
                t = Path.ListGetItem
                make = type(x)
            value_gen = (
                self.recurse_or_skip(t(i), *xi)
                for i, xi in enumerate(zip(x, *xs, strict=True))
            )
            return make(value_gen)
        elif isinstance(x, dict):
            if not _one_type((x, *xs)):
                return self.call_or_raise(
                    x, xs, "All tree-mapped objects must have the same structure."
                )
            if any(xi.keys() != x.keys() for xi in xs):
                return self.call_or_raise(
                    x, xs, "All tree-mapped dictionaries must have the same keys."
                )
            return type(x)(
                {
                    k: self.recurse_or_skip(
                        Path.DictGetItem(k), *(xi[k] for xi in (x, *xs))
                    )
                    for k in x.keys()
                }
            )
        elif isinstance(x, Struct):
            if is_abstract_struct(type(x)):
                raise RuntimeError(
                    "How do you have an instance of an abstract struct??"
                )
            if not _one_type((x, *xs)):
                return self.call_or_raise(
                    x, xs, "All tree-mapped objects must have the same structure."
                )
            struct = object.__new__(type(x))  # pyright: ignore[reportArgumentType]
            __dict__ = self.recurse_or_skip(
                Path.StructDict(), *(_dataclass_asdict(xi) for xi in (x, *xs))
            )
            object.__setattr__(struct, "__dict__", __dict__)
            return struct
        elif type(x) is ft.partial:
            if not _one_type((x, *xs)):
                return self.call_or_raise(
                    x, xs, "All tree-mapped objects must have the same structure."
                )
            func = self.recurse_or_skip(
                Path.PartialFunc(),
                *(_unwrap_treemap_wrapper(xi.func) for xi in (x, *xs)),
            )
            args = self.recurse_or_skip(
                Path.PartialArgs(), *(xi.args for xi in (x, *xs))
            )
            keywords = self.recurse_or_skip(
                Path.PartialKeywords(), *(xi.keywords for xi in (x, *xs))
            )
            if not callable(func):
                # Handle annoying Python limitation
                func = _FakeCallable(func)
            return ft.partial(func, *args, **keywords)
        elif type(x) is types.MethodType:
            # Bound methods are trees. This means that
            # `higher_order_fn(some_fn)(foo.some_method, ...)` will work.
            # This doesn't come up super often, but it's an easy thing to support, and
            # an easy source of hard-to-find silent bugs otherwise.
            if not _one_type((x, *xs)):
                return self.call_or_raise(
                    x, xs, "All tree-mapped objects must have the same structure."
                )
            func = self.recurse_or_skip(
                Path.MethodFunc(),
                *(_unwrap_treemap_wrapper(xi.__func__) for xi in (x, *xs)),
            )
            self_ = self.recurse_or_skip(
                Path.MethodSelf(),
                *(_unwrap_treemap_wrapper(xi.__self__) for xi in (x, *xs)),
            )
            if func is None:
                func = _FakeCallable(None)
            if self_ is None:
                self_ = _FakeCallable(None)
            return types.MethodType(func, self_)
        elif type(x) is types.FunctionType:
            # Closures are trees.
            #
            # This one is included for one particular use case: to make things like the
            # following work:
            # ```python
            # def some_fn(x):
            #     def another_fn(y):
            #         return x + y
            #     return higher_order_fn(another_fn)("some static argument")
            # ```
            if not _one_type((x, *xs)):
                return self.call_or_raise(
                    x, xs, "All tree-mapped objects must have the same structure."
                )
            # Checking for the same name seems like the best way to check that the
            # 'structure' of the function is the same, as the identity changes with
            # being recreated during tree-mapping.
            if any(xi.__module__ != x.__module__ for xi in xs):
                return self.call_or_raise(
                    x, xs, "All tree-mapped functions must have the same module."
                )
            if any(xi.__qualname__ != x.__qualname__ for xi in xs):
                return self.call_or_raise(
                    x, xs, "All tree-mapped functions must have the same qualname."
                )
            if x.__closure__ is None:
                if any(xi.__closure__ is not None for xi in xs):
                    return self.call_or_raise(
                        x,
                        xs,
                        "All tree-mapped functions must have the same closure -- in "
                        "this case, no closure.",
                    )
                # Not fn(x). Functions count as container types, that we iterate over to
                # obtain their closed-over values.
                #
                # Not `_copy_function(x)`. I had that for a while and it ended up
                # playing merry hell with all kinds of things. In particular it's fairly
                # common that we tree-map over something containing a global function,
                # and if we copy it then it is now no longer pickleable. The fact that
                # you can copy functions is also not a commonly-understood concept, so
                # the downstream implications would likely confuse end users rather a
                # lot as well. The downside is that `tree.map` does not *quite* always
                # make a copy of its input: an end user needs to special-case functions
                # before performing any kind of mutation.
                return x
            else:
                if any(
                    xi.__closure__ is None or len(xi.__closure__) != len(x.__closure__)
                    for xi in xs
                ):
                    return self.call_or_raise(
                        x,
                        xs,
                        "All tree-mapped functions must have the same closure -- in "
                        "this case, the same number of closed-over variables.",
                    )
                # Okay, we do something pretty sneaky here.
                #
                # It's fairly common to have functions that reference themselves within
                # their own closure.
                # Recursive functions are the obvious example, but in fact
                # `jaxtyped.jaxtyped(...)(fn)` does this as well. (In its case, to check
                # if someone has set the `__no_type_check__` attribute on it, and as
                # such that it should disable itself.) It is therefore fairly important
                # that we allow reference cycles. (Which need not be just a
                # self-reference but could potentially be more complicated reference
                # cycles, e.g. `fn -> [other_fn] -> other_fn -> fn`.)
                #
                # As such, we actually create a copy of the function (which we were
                # going to do in the `tree.map` anyway), but now actually (a) cache that
                # and (b) mutate it in-place at the end of this block.
                #
                # That means that if our nested `recurse` over the closure takes us back
                # here, then we'll hit this cached value, and return our
                # yet-to-be-mutated copy. This preserves the reference cycle after the
                # `tree.map`.
                #
                # This is obviously pretty ugly. We don't really have a choice here, but
                # we do decide not to try and handle this for any other type. We're
                # happy to disallow self-referential lists etc.
                # It's also not obvious how to make this work for all other types. This
                # works here because a function's closure is mutable, so we can create
                # our copy, cache it, and then mutate it later. The same trick wouldn't
                # work for a tuple, for example.
                try:
                    return self.cache[id(x)]
                except KeyError:
                    pass
                out = self.cache[id(x)] = _copy_function(x)

                new_cells = []
                for i, cells in enumerate(
                    zip(*(xi.__closure__ for xi in (x, *xs)), strict=True)
                ):
                    is_empty = [_is_empty_cell(cell) for cell in cells]
                    if all(is_empty):
                        new_cells.append(_make_empty_cell())
                    elif any(is_empty):
                        self.cache.pop(id(x))
                        return self.call_or_raise(
                            x,
                            xs,
                            "All tree-mapped functions must have the same closure -- "
                            "in this case, for all closures to be empty or filled.",
                        )
                    else:
                        new_cell_contents = self.recurse_or_skip(
                            Path.ClosureItem(i), *(cell.cell_contents for cell in cells)
                        )
                        new_cells.append(_make_cell(new_cell_contents))
                _adjust_function_closure(out, tuple(new_cells))
                return out
        else:
            return self.call(x, xs)

    def recurse_or_skip(self, piece, x, *xs):
        __tracebackhide__ = True
        if self.piece_index < len(self.pieces):
            if self.pieces[self.piece_index] == piece:
                self.piece_index += 1
                out = self.recurse(x, *xs)
                self.piece_index -= 1
                return out
            else:
                return x
        else:
            assert self.piece_index == len(self.pieces)
            self.pieces.append(piece)
            self.piece_index += 1
            out = self.recurse(x, *xs)
            self.piece_index -= 1
            assert self.pieces.pop() is piece
            return out

    def call(self, x, xs):
        __tracebackhide__ = True
        if self.structure_from == StructureFrom.ALL:
            for xi in xs:
                if map(xi, fn=lambda _: None, is_leaf=self.is_leaf) is not None:
                    raise StructureError(
                        "Tree structures did not match exactly when using "
                        "`tree.map(..., structure_from=StructureFrom.ALL)`"
                    )
        assert self.piece_index == len(self.pieces)
        if self.with_path:
            return self.fn(x, *xs, path=Path(*self.pieces))
        else:
            return self.fn(x, *xs)

    def call_or_raise(self, x, xs, msg):
        __tracebackhide__ = True
        if self.structure_from == StructureFrom.COMMON:
            return self.call(x, xs)
        else:
            raise StructureError(msg)


def _dataclass_asdict(x):
    # Not `dataclasses.asdict` because that is recursive. Not `x.__dict__` because that
    # is written to by `functools.cached_property`.
    fields = {}
    sentinel = object()
    for f in dataclasses.fields(x):
        value = getattr(x, f.name, sentinel)
        if value is not sentinel:
            fields[f.name] = value
    return fields


class _FakeCallable:
    def __init__(self, item):
        self.item = item

    def __call__(self, *args, **kwargs):
        del args, kwargs
        assert False


def _unwrap_treemap_wrapper(x):
    if type(x) is _FakeCallable:
        return x.item
    return x


def _make_cell(val: Any) -> types.CellType:
    fn = lambda: val
    assert fn.__closure__ is not None
    return fn.__closure__[0]


def _is_empty_cell(cell: types.CellType) -> bool:
    try:
        _ = cell.cell_contents
    except ValueError:
        return True
    else:
        return False


def _make_empty_cell() -> types.CellType:
    fn = lambda: val  # pyright: ignore[reportUndefinedVariable]
    assert fn.__closure__ is not None
    return fn.__closure__[0]
    val = None


def _copy_function(fn: types.FunctionType) -> types.FunctionType:
    if fn.__closure__ is None:
        closure = None
    else:
        closure = tuple(
            _make_empty_cell()
            if _is_empty_cell(cell)
            else _make_cell(cell.cell_contents)
            for cell in fn.__closure__
        )
    out = types.FunctionType(
        code=fn.__code__,
        globals=fn.__globals__,
        name=fn.__name__,
        argdefs=fn.__defaults__,
        closure=closure,
    )
    out.__module__ = fn.__module__
    out.__qualname__ = fn.__qualname__
    out.__annotations__.update(fn.__annotations__)
    if fn.__kwdefaults__ is not None:
        out.__kwdefaults__ = fn.__kwdefaults__.copy()
    if hasattr(fn, "__no_type_check__"):
        out.__no_type_check__ = fn.__no_type_check__  # pyright: ignore[reportFunctionMemberAccess]
    return out


def _adjust_function_closure(
    fn: types.FunctionType, closure: tuple[types.CellType, ...]
) -> None:
    assert fn.__closure__ is not None
    for old_cell, new_cell in zip(fn.__closure__, closure, strict=True):
        if _is_empty_cell(new_cell):
            if not _is_empty_cell(old_cell):
                del old_cell.cell_contents
        else:
            old_cell.cell_contents = new_cell.cell_contents


_leaves = set[type]()


def register_leaf(x: type) -> None:
    """Registers a type as always being a leaf. Example usage:
    ```python
    class Foo(Struct):
        some_field: int

    register_leaf(Foo)

    tree.map(Foo(some_field=3), fn=print)

    # Foo(some_field=3)
    #
    # (Without the `register_leaf` we would have the individual `3` printed out.)
    ```
    """
    _leaves.add(x)


def is_registered_leaf_type(cls: type) -> bool:
    """Whether `register_leaf(cls)` or `register_leaf(some_parent_class)` has been
    called.
    """
    # Must be `issubclass` and not `type(x) in _leaves`. This is so that
    # `register_leaf(AbstractClassOfSomeKind)` works.
    return any(issubclass(cls, x) for x in _leaves)


class _Star:
    def __repr__(self):
        return "*"


_star = _Star()


def pformat_structure(tree: Tree) -> str:
    """Pretty-formats a tree's structure, using `*` to represent each leaf."""
    return wl.pformat(map(tree, fn=lambda _: _star), respect_pdoc=False)


def num_leaves(tree: Tree) -> int:
    """Counts the number of leaves in a tree."""
    counter = 0

    def _count(_):
        nonlocal counter
        counter += 1

    map(tree, fn=_count)
    return counter


_update_sentinel = object()


def replace(
    x: Lens[_Value], value: Any = _update_sentinel, *, fn: None | Callable = None
) -> _Value:
    """Replaces a value within a tree, leaving the rest of the tree unchanged.

    **Arguments:**

    - `x`: the tree, and location within it, to update. These are represented jointly as
        a `tree.Lens`.
    - `value`: the value to insert. Mutually exclusive with `fn`.
    - `fn`: a function to call on the old value, returning the new value. Mutually
        exclusive with `value`.

    **Returns:**

    The updated tree. The original tree is left unchanged.
    """
    if len(object.__getattribute__(x, "roots")) > 1:
        raise ValueError(
            "Cannot call `tree.replace(Lens(tree1, tree2, ...), ...)`. Only one tree "
            "may be specified."
        )
    if value is _update_sentinel:
        if fn is None:
            raise ValueError("Must provide at least one of `value` or `fn`.")
    else:
        if fn is None:
            fn = lambda _: value
        else:
            raise ValueError("Cannot provide both of `value` and `fn`.")
    return map(x, fn=fn, is_leaf=lambda _: True)


def get(x: Lens[_Value]) -> Any:
    """Gets the value currently pointed at by a lens."""
    out, *_ = object.__getattribute__(x, "trees")
    return out
