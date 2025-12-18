import dataclasses
import inspect
import operator
from collections.abc import Callable, Hashable
from typing import Any, Protocol, TypeVar
from typing_extensions import dataclass_transform
from weakref import WeakSet

import wadler_lindig as wl

from ._better_abstract import (
    # These are part of the public interface of `struct`.
    AbstractClassVar as AbstractClassVar,
    AbstractVar as AbstractVar,
    better_dataclass,
    BetterABCMeta,
)


def _is_special_form(cls: type) -> bool:
    return (
        cls.__module__ in {"typing", "typing_extensions", "collections.abc"}
        or Protocol in cls.__bases__
    )


def _is_abstract_class(cls: type) -> bool:
    return (
        (len(cls.__abstractmethods__) > 0)
        or (len(cls.__abstractvars__) > 0)
        or (len(cls.__abstractclassvars__) > 0)
        or (cls in _abstract_struct_registry)
    )


def _is_abstract_method(x: Any) -> bool:
    return inspect.isfunction(x) and getattr(x, "__isabstractmethod__", False)


def is_magic(k: str) -> bool:
    return (k.startswith("__") and k.endswith("__")) or (k == "_abc_impl")


def _check_concrete(cls: type, concrete_objects: dict[str, tuple[type, bool]]) -> None:
    for k, v in cls.__dict__.items():
        if not is_magic(k) and not _is_abstract_method(v):
            try:
                previous_cls, is_function = concrete_objects[k]
            except KeyError:
                concrete_objects[k] = cls, inspect.isfunction(v)
            else:
                if is_function:
                    raise TypeError(
                        "Structs cannot override concrete methods. "
                        f"`{cls.__module__}.{cls.__qualname__}.{k}` is "
                        "attempting to override "
                        f"`{previous_cls.__module__}.{previous_cls.__qualname__}.{k}`."
                    )
                raise TypeError(
                    "Structs cannot override non-methods. "
                    f"`{cls.__module__}.{cls.__qualname__}.{k}` "
                    "is attempting to override "
                    f"`{previous_cls.__module__}.{previous_cls.__qualname__}.{k}`."
                )


# collection of explicitly defined abstract Structs
_abstract_struct_registry = WeakSet()
_T = TypeVar("_T")
# Pyright-ignore because sadly typevars aren't valid in this context:
# https://github.com/microsoft/pyright/issues/7825
#  There's no good reason for that though, so I'm going to use it anyway for
# documentation purposes.
eq_checkers: dict[tuple[str, str], Callable[[_T, _T], bool]] = {}  # pyright: ignore[reportGeneralTypeIssues]


# This deliberately does not pass `frozen_default=True`, as that clashes with custom
# `__init__` methods.
@dataclass_transform(field_specifiers=(dataclasses.field,))
class _StructMeta(BetterABCMeta):
    def __new__(mcs, name, bases, namespace, *, is_abstract: bool = False, **kwargs):
        #
        # Structs are dataclasses.
        #
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if is_abstract:
            _abstract_struct_registry.add(cls)

        if (
            "__init__" in cls.__dict__
        ):  # Check before `dataclass` adds an `__init__` method.
            if _is_abstract_class(cls):
                raise TypeError(
                    "Only concrete Structs can have custom `__init__` methods. "
                    f"`{cls.__module__}.{cls.__qualname__}` is abstract and has a "
                    "custom `__init__` method."
                )
            if hasattr(cls, "__post_init__"):
                raise TypeError(
                    f"`{cls.__module__}.{cls.__qualname__}` has both an `__init__` and "
                    "a `__post_init__` method. This is an error: only the `__init__` "
                    "method will be used, and the `__post_init__` is ignored."
                )
        if "__post_init__" in cls.__dict__ and _is_abstract_class(cls):
            raise TypeError(
                "Only concrete Structs can have `__post_init__` methods. "
                f"`{cls.__module__}.{cls.__qualname__}` is abstract and has a custom "
                "`__post_init__` method."
            )
        cls = better_dataclass(frozen=True, eq=False, repr=False)(cls)
        #
        # Abstract naming
        #
        if cls.__name__.startswith("Abstract") or cls.__name__.startswith("_Abstract"):
            if not _is_abstract_class(cls):
                raise TypeError(
                    "Concrete Structs cannot have names starting with 'Abstract' or "
                    "'_Abstract'."
                )
        elif _is_abstract_class(cls):
            raise TypeError(
                "Abstract Structs must have names starting with 'Abstract' or "
                "'_Abstract'."
            )

        concrete_objects = dict()
        # `reversed` so that `_check_concrete` performs its checks in the order that
        # namespaces are overlaid during inheritance.
        for base in reversed(bases):
            #
            # Inheritance
            #
            if base is globals().get(
                "Struct"
            ):  # `Struct` is not defined when defining `Struct` itself.
                continue
            if _is_special_form(base):
                continue
            if not issubclass(base, Struct):
                raise TypeError(
                    "Structs can only inherit from other Structs. "
                    f"`{cls.__module__}.{cls.__qualname__}` is a Struct inheriting "
                    f"from `{base.__module__}.{base.__qualname__}`, which is not a "
                    "Struct."
                )
            #
            # Concrete-means-final
            #
            if not _is_abstract_class(base):
                raise TypeError(
                    "Every Struct must be either abstract or final. It is not possible "
                    "to inherit from a concrete Struct. "
                    f"`{cls.__module__}.{cls.__qualname__}` is a Struct inheriting "
                    f"from `{base.__module__}.{base.__qualname__}`, which is concrete."
                )
            #
            # Concrete methods (or any attributes) are not overridden.
            #
            _check_concrete(base, concrete_objects)
        _check_concrete(cls, concrete_objects)

        field_names = frozenset({f.name for f in dataclasses.fields(cls)})  # pyright: ignore[reportArgumentType]
        orig_setattr = cls.__setattr__

        def __setattr__(self, name: str, value: Any):
            if name in field_names and name not in self.__dict__.keys():
                # We are presuambly inside initialisation, and this field has not been
                # set yet.
                object.__setattr__(self, name, value)
            elif name == "__orig_class__":
                # Allow:
                # ```
                # class SomeStruct(Struct, Generic[T]): ...
                # x = SomeStruct[int]()
                # x.__orig_class__ # SomeStruct[int]
                # ```
                # This attribute is set after instantiation here:
                # https://github.com/python/cpython/blob/7b3ab5921fa25ed8b97b6296f97c5c78aacf5447/Lib/typing.py#L728
                # So without special-casing it's incompatible with frozen dataclasses.
                object.__setattr__(self, name, value)
            else:
                # Raise normal frozen dataclass error.
                orig_setattr(self, name, value)

        __setattr__.__module__ = orig_setattr.__module__
        __setattr__.__name__ = orig_setattr.__name__
        __setattr__.__qualname__ = orig_setattr.__qualname__
        cls.__setattr__ = __setattr__
        return cls

    def __call__(cls, *args, **kwargs):  # noqa: N805
        self = super().__call__(*args, **kwargs)  # pyright: ignore[reportAttributeAccessIssue]

        missing_names = {
            f.name
            for f in dataclasses.fields(cls)  # pyright: ignore[reportArgumentType]
            if f.name not in self.__dict__
        }
        if len(missing_names) > 0:
            raise TypeError(
                "The following fields were not initialized during __init__: "
                f"{missing_names}"
            )

        for parent_cls in cls.__mro__:
            try:
                check_init = parent_cls.__dict__["__check_init__"]
            except KeyError:
                pass
            else:
                check_init(self)
        return self

    # Ensure that `help(FooStruct)` still works, even though we've overriden `__call__`.
    @property
    def __signature__(cls):  # noqa: N805
        sig = inspect.signature(cls.__init__)
        params = list(sig.parameters.values())[1:]  # Remove self parameter
        return sig.replace(parameters=params)


class Struct(Hashable, metaclass=_StructMeta):
    """The standard structured type. You should subclass this.

    This gives:

    - a frozen dataclass;
    - it supports `abc.abstractmethod`s.
    - it also supports our custom `AbstractVar` and `AbstractClassVar`, to define
        abstract (class) attributes.
    - it also supports `__check_init__`, to assert that post-initialization invariants
        hold. All superclasses will automatically have this method called. This method
        exists to allow invariant-checking in ABCs *without* needing to put it in
        `__init__` or `__post_init__` (which will almost always be overridden in
        subclasses).

    In addition, it enforces several invariants (a set of rules to allow ABCs whilst
    avoiding OOP-badness):

    - it may only inherit from other Structs;
    - ABCs must have names starting with `Abstract` or `_Abstract`;
    - ABCs must either define abstract methods, or be defined with the keyword argument
        `is_abstract=True`:
        ```python
        class AbstractStruct(Struct, is_abstract=True):
            ...
        ```
    - concrete Structs cannot be further subclassed (an idea we stole from Julia);
    - concrete methods cannot be overridden.

    You should not user `super()` in conjunction with `Struct`s. They are designed to
    enable a different design pattern than co-operative multiple inheritance (which as
    above we file under "OOP-badness").

    Example:
    ```python
    class AbstractOptimizer(Struct):
        learning_rate: AbstractVar[float]

        def __check_init__(self):
            if self.learning_rate <= 0:
                raise ValueError("You will not be going to space today.")

        @abc.abstractmethod
        def make(self, params: Iterable[torch.nn.Parameter]) -> torch.optim.Optimizer:
            ...

    class SGD(AbstractOptimizer):
        learning_rate: float

        def make(self, params: Iterable[torch.nn.Parameter]) -> torch.optim.Optimizer:
            return torch.optim.SGD(params, learning_rate=self.learning_rate)
    ```
    """

    def __repr__(self):
        return wl.pformat(self)

    def __hash__(self) -> int:
        """Hashes the struct.

        We hash Structs as a frozen mapping `tuple[tuple[str, Any]]` where key,value
        pairs are (attribute names, attribute values) pairs.
        """
        return hash(
            tuple(
                (f.name, getattr(self, f.name)) for f in dataclasses.fields(type(self))
            )
        )

    # Work around NumPy/Torch/Pandas/Polars poor behavior.
    def __eq__(self, other) -> bool:
        if type(self) is not type(other):
            return False
        for field in dataclasses.fields(type(self)):
            self_value = getattr(self, field.name)
            other_value = getattr(other, field.name)
            if type(self_value) is not type(other_value):
                return False
            module, *_ = type(self_value).__module__.split(".", 1)
            qualname = type(self_value).__qualname__
            checker = eq_checkers.get((module, qualname), operator.eq)
            if not checker(self_value, other_value):
                return False
        return True


# Lookup based on strings to avoid importing these heavyweight modules here. This was
# previously a bottleneck in TTFX.
eq_checkers["numpy", "ndarray"] = lambda x, y: x.shape == y.shape and (x == y).all()  # pyright: ignore[reportAttributeAccessIssue]
eq_checkers["torch", "Tensor"] = lambda x, y: x.shape == y.shape and (x == y).all()  # pyright: ignore[reportAttributeAccessIssue]
eq_checkers["polars", "DataFrame"] = lambda x, y: x.equals(y)  # pyright: ignore[reportAttributeAccessIssue]
eq_checkers["polars", "Series"] = lambda x, y: x.equals(y)  # pyright: ignore[reportAttributeAccessIssue]


_Struct = TypeVar("_Struct", bound=Struct)


def is_abstract_struct(cls: type[Struct]) -> bool:
    """Return whether this struct is abstract or concrete."""
    if not issubclass(cls, Struct):
        raise TypeError(f"{cls} is not a subclass of `Struct`.")
    return _is_abstract_class(cls)


def replace(struct: _Struct, **kwargs) -> _Struct:
    """Replace fields in a `Struct`. (Like `dataclasses.replace`, but works even with
    custom `__init__` methods.)

    To replace deeply-nested items, see `structional.tree.replace`.

    **Arguments:**

    - `struct`: the struct to replace a field on.
    - `**kwarg`: keyword names are the names of the fields to replace; keyword values
        are the values to set the fields to.

    **Returns:**

    The update struct. The original struct is left unchanged.

    !!! FAQ

        Note that no typechecking is performed when doing `replace`, nor are `__init__`
        or  `__check_init__` called. If this is important to you then you should perform
        this check afterwards.

        The reason for this is because in some use-cases it is important that structs be
        polymorphic over their leaf types, e.g. when attaching metadata. This isn't
        super common in business code, but it's useful in more 'infrastructure' code to
        be able to create a 'matching' structure with different leaf values. For
        example, maybe you have `MyData(x=array(...), y=array(...))`, and then to
        determine whether you should save each value to disk then you'd like to
        construct a matching `MyData(x=True, y=False)`. This general idea extends to a
        lot of other use-cases: replacing leaves with cheap serialized representations;
        replacing leaves with async future objects that will become those leaves in the
        future, etc.
    """
    new_object = object.__new__(type(struct))
    object_args = dataclasses.fields(struct)
    set_diff = {f.name for f in object_args} - set(kwargs.keys())
    valid_fields = {f.name for f in object_args}.intersection(set(kwargs.keys()))
    invalid_fields = set(kwargs.keys()) - {f.name for f in object_args}
    if len(invalid_fields) > 0:
        raise AttributeError(
            f"Fields {invalid_fields} not present in {struct.__class__}"
        )
    for k in set_diff:
        object.__setattr__(new_object, k, getattr(struct, k))  # noqa: PLC2801
    for k in valid_fields:
        object.__setattr__(new_object, k, kwargs[k])  # noqa: PLC2801
    return new_object
