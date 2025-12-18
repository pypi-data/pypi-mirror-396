<h1 align='center'><code>structional</code></h1>

Immutable structs, controlled randomness, and trees. These are the core tools I use to build reliable software in Python.

Whilst this library does not depend on PyTorch and is broadly applicable across all of Python, the downstream use-case is to make it possible to 'write functional PyTorch'.

This is *not* a library implementing monads, `foldl`, and all that magical Haskell stuff.

## Installation

```
pip install structional
```

## What's in the box?

- `Struct`:
  - is an immutable (frozen) dataclass, making writing safe code easy;
  - is an abstract base class, supporting the stdlib `abstractmethod` *and* our own extensions `AbstractVar` (declaring abstract attributes) and `__check_init__` (post-initialization invariants);
  - enforces 'abstract/final rules': every class can either be subclassed (abstract) or instantiated (concrete) – but not both.

- `PRNGKey` provides access to deterministic randomness.
  - Use-case in ML is perfectly reproducible training runs; awesome for catching bugs.
  - A function need no longer be 'secretly random' because it depends on a background stateful RNG.
  - Call `key.some_distribution()` to sample from a distribution.
  - Split a key via `key.split()` to create deterministic but statistically independent new sources of randomness.
  - Keys can only be used once (known as 'linear typing'), to prevent accidental reuse.

- `tree` is a subpackage for manipulating immutable nested structures of tuples, `Struct`s, etc.:
  - `tree.map` ('functors' for you programming geeks) applies a function to every leaf.
  - `tree.update` ('lenses' for the geeks) updates just part of a tree structure, returning a new object out-of-place.

## FAQ

<details><summary><b>What are similar reference points amongst other languages?</b></summary>

`Struct`s combine Rust-style traits with Julia-style 'abstract/final rules'.

Meanwhile in Python, we have several JAX/Equinox reference points:

- `Struct`s are inspired by `equinox.Module`;
- `PRNGKey` is inspired by `jax.random.key`;
- `tree.map` is inspired by `jax.tree.map`;
- `tree.replace` is inspired by `equinox.tree_at`.

(Broadly speaking these ideas are pretty standard in functional programming.)

</details>
<details><summary><b>Aren't there a lot of 'functional Python' libraries?</b></summary>

Yup. Most of them tend to either implement Haskell-isms (`foldl`, monads) or use all those complicated functional programming words (functors, ...) 😄. We try to take a pragmatic approach, implementing the tools that can't easily be already expressed in normal Python code.

</details>
<details><summary><b>How do these integrate with PyTorch <code>torch.nn.Module</code>s?</b></summary>

The idea is to treat the PyTorch modules as an implementation detail.

A typical pattern looks something like this:

```python
from structional import AbstractVar, PRNGKey, Struct
from jaxtyping import Float
from torch import from_numpy, nn, Tensor

class AbstractImageDiffusion(Struct):
    shape: AbstractVar[tuple[int, ...]]
    num_steps: AbstractVar[int]

    @abstractmethod
    def step(self, image: Float[Tensor, "*shape"]) -> Float[Tensor, "*shape"]: ...

class LinearImageDiffusion(AbstractImageDiffusion):  # State-of-the-art architecture.
    model: nn.Linear
    shape: tuple[int, ...]
    num_steps: int

    def __init__(self):
        self.model = nn.Linear(256*256, 256*256)
        self.shape = (256, 256)
        self.num_steps = 10

    def step(self, image: Float[Tensor, "*shape"]) -> Float[Tensor, "*shape"]:
        return self.model(image.reshape(-1)).reshape(self.shape)

def inference(model: AbstractImageDiffusion, key: PRNGKey) -> Float[Tensor, "*shape"]:
    x = key.normal(size=model.shape)  # Initial noise
    x = from_numpy(x)  # Zero-copy if we're on the CPU; efficient GPU is an exercise for the reader ;)
    for _ in range(model.num_steps):  # Denoise
        x = model.step(x)
    return x
```

</details>

<details><summary><b>Where should abstract base classes live?</b></summary>

When organizing code that's large enough to be split into multiple files, then ABCs could either be placed alongside their subclasses:

```python
# bar.py
class AbstractFoo(Struct): ...

class ConcreteFoo(AbstractFoo): ...

# qux.py
def frobnicate(x: AbstractFoo): ...
```

or they could live alongside their consumers:

```python
# baz.py
class AbstractFoo(Struct): ...

def frobnicate(x: AbstractFoo): ...

# fizzle.py
class ConcreteFoo(AbstractFoo): ...
```

There's no hard rule, but about 80% of the time I find it's more useful to keep the abstract class (`AbstractFoo`) next to its consumer (`frobnicate`). The other 20% of the time I find it's most useful to keep it next to its subclasses (`ConcreteFoo`).

The rationale for this is that typically it is the consumer (`frobnicate`) that is the 'first class citizen' of our code, and the ABC mostly just exists as a way to define the interface required by that consumer.

This approach also pairs well with how ABCs are often used to support extensibility: later authors can come along and define their own concrete subclasses.

This isn't a hard-and-fast rule. It matters most when the two files live in separately-versioned packages, and in this case it really is usually best to keep the ABC alongside its consumer.
</details>
