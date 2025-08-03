# Python 3.13 Type Parameter Defaults Demo

This example demonstrates one of the most exciting new features in Python 3.13: **Type Parameter Defaults** (PEP 696).

## What's New in Python 3.13?

Based on my research, Python 3.13 introduces several major improvements:

- <cite index="1-1,1-16">A new interactive interpreter, experimental support for running in a free-threaded mode (PEP 703), and a Just-In-Time compiler (PEP 744)</cite>
- <cite index="1-2,1-17">Error messages continue to improve, with tracebacks now highlighted in color by default</cite>
- <cite index="1-18">The locals() builtin now has defined semantics for changing the returned mapping, and type parameters now support default values</cite>
- <cite index="3-11">typing.TypeVar, typing.ParamSpec, and typing.TypeVarTuple all let you define defaults to be used if no type is explicitly specified</cite>

## Type Parameter Defaults Feature

<cite index="12-2">This PEP introduces the concept of type defaults for type parameters, including TypeVar, ParamSpec, and TypeVarTuple, which act as defaults for type parameters for which no type is specified</cite>.

### Key Benefits:

1. **Reduces Boilerplate**: No need to specify common types repeatedly
2. **Better API Design**: Makes generic classes more user-friendly
3. **Maintains Type Safety**: Still provides full type checking
4. **Backward Compatible**: Existing code continues to work

### Example Usage:

```python
from typing import TypeVar, Generic

# Define a TypeVar with a default
T = TypeVar("T", default=str)

class Container(Generic[T]):
    def __init__(self, value: T):
        self.value = value

# Uses default type (str)
container1 = Container("hello")

# Explicitly specify type
container2: Container[int] = Container(42)
```

## Running the Demo

```bash
# Make sure you have Python 3.13
python --version

# Run the demonstration
python python313_type_defaults_demo.py
```

## What the Demo Shows

The example file demonstrates:

1. **Basic TypeVar Defaults**: Simple containers with default string types
2. **Multiple Type Parameters**: Cache with default key/value types
3. **ParamSpec Defaults**: Function signature defaults for decorators
4. **TypeVarTuple Defaults**: Variadic generics with default tuple types
5. **Real-world Examples**: Configuration managers and repository patterns

## Other Notable Python 3.13 Features

- <cite index="1-30,1-31">Python now uses a new interactive shell by default, based on code from the PyPy project. When the user starts the REPL from an interactive terminal, the following new features are now supported: Multiline editing with history preservation</cite>
- <cite index="6-21,6-22">It is now possible to disable the Global Interpreter Lock (GIL), an experimental feature disabled by default. The free-threaded mode needs different binaries, e.g., python3.13t</cite>
- <cite index="7-7">Virtual environments also changed in a very subtle, but very handy way, for those of us using Git to version-control our code</cite> - they're now automatically git-ignored
- <cite index="3-1,3-2">Python 3.13 adds new elements to the JIT that generate actual machine code at runtime, instead of just specialized bytecode. The resulting speedup isn't much just yet—maybe 5%—but it paves the way for future optimizations that weren't previously possible</cite>

This demo focuses on type parameter defaults because it's a feature that will immediately benefit many Python developers working with generic code, making it more accessible and easier to use while maintaining the full power of Python's type system.