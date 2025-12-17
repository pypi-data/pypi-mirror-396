# hipr

**(pronounced "hyper")**

![CI](https://github.com/sencer/hipr/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/sencer/hipr/branch/main/graph/badge.svg)](https://app.codecov.io/github/sencer/hipr)

**Automatic Pydantic config generation from class and function signatures.**

Turn any class into a configurable, serializable, validated component—just add `@configurable` and mark tunable parameters with `Hyper[T]`. This simplifies the creation of reproducible machine learning experiments and configurable applications by reducing boilerplate and enforcing type safety and validation at definition time.

## Before & After

**Without hipr** — manual config classes, validation, and factory methods:

```python
from dataclasses import dataclass

# 1. Define the Config class (Boilerplate)
@dataclass
class OptimizerConfig:
    learning_rate: float = 0.01
    momentum: float = 0.9

    # 2. Write a factory method to create the object
    def make(self) -> "Optimizer":
        return Optimizer(
            learning_rate=self.learning_rate,
            momentum=self.momentum
        )

# 3. Define the actual class
class Optimizer:
    def __init__(self, learning_rate: float, momentum: float):
        self.learning_rate = learning_rate
        self.momentum = momentum

# 4. Repeat for every component...
@dataclass
class ModelConfig:
    optimizer: OptimizerConfig
    hidden_size: int = 128
    
    def make(self) -> "Model":
        return Model(
            optimizer=self.optimizer.make(),
            hidden_size=self.hidden_size
        )

class Model:
    def __init__(self, optimizer: Optimizer, hidden_size: int):
        self.optimizer = optimizer
        self.hidden_size = hidden_size
```

**With hipr** — automatic config generation with validation:

```python
from dataclasses import dataclass
from hipr import configurable, DEFAULT

@configurable
@dataclass
class Optimizer:
    learning_rate: float = 0.01
    momentum: float = 0.9

@configurable
@dataclass
class Model:
    hidden_size: int = 128
    dropout: float = 0.1
    optimizer: Optimizer = DEFAULT  # Nested config with default

# Create config
config = Model.Config(hidden_size=256, dropout=0.2)

# Serialize/deserialize
json_str = config.model_dump_json()
loaded = Model.Config.model_validate_json(json_str)

# Instantiate
model = config.make()
# model.optimizer is now an instance of Optimizer
print(model.optimizer.learning_rate)  # 0.01
```

All this magic stays fully type-safe—run `hipr-generate-stubs src/` and your IDE will autocomplete `.Config` classes, validate parameters, and catch errors before runtime.

## Installation

```bash
pip install hipr
# or: uv add hipr
```

## Core Concepts

### Classes & Dataclasses (Primary Use Case)

The `@configurable` decorator generates a `.Config` class that captures parameters:

```python
from dataclasses import dataclass
from hipr import configurable

@configurable
@dataclass
class Optimizer:
    learning_rate: float = 0.01
    momentum: float = 0.9

# Direct instantiation still works
opt = Optimizer(learning_rate=0.001)

# Or use Config for validation + serialization
config = Optimizer.Config(learning_rate=0.001)
opt = config.make()  # Returns Optimizer instance
```

Regular classes work the same way:

```python
@configurable
class Model:
    def __init__(
        self,
        hidden_size: int = 128,
        dropout: float = 0.1,
    ):
        self.hidden_size = hidden_size
        self.dropout = dropout

config = Model.Config(hidden_size=256)
model = config.make()  # Returns Model instance
```

### Functions

For functions, the `Hyper[T]` annotation is **required** to identify which parameters are configurable.

```python
from hipr import configurable, Hyper, Ge, Gt

@configurable
def train(
    data: list[float],              # Runtime data (not a hyperparameter)
    epochs: Hyper[int, Ge[1]] = 100,
    lr: Hyper[float, Gt[0.0]] = 0.001,
) -> dict:
    return {"trained": True}
```

Internally, `hipr` treats this as if it were a dataclass with a `__call__` method:

This conceptual representation shows how `hipr` treats configurable functions as if they were dataclasses with a `__call__` method, where the `Hyper[T]` parameters become fields of the dataclass.

```python
@configurable
@dataclass
class train:
    epochs: Hyper[int, Ge[1]] = 100
    lr: Hyper[float, Gt[0.0]] = 0.001

    def __call__(self, data: list[float]) -> dict:
        return {"trained": True}
```


### Constraints & Validation

The `Hyper[T]` annotation allows you to attach validation constraints to your parameters. This works for both classes and functions (where it is required).

```python
from dataclasses import dataclass
from hipr import configurable, Hyper, Ge, Le, Gt, MinLen, Pattern

@configurable
@dataclass
class Network:
    # Required parameter (no default) - Must come first in dataclass
    learning_rate: Hyper[float, Gt[0.0]]

    # Numeric bounds
    dropout: Hyper[float, Ge[0.0], Le[1.0]] = 0.5
    layers: Hyper[int, Ge[1], Le[100]] = 10

    # String constraints
    name: Hyper[str, MinLen[3], Pattern[r"^[a-z]+$"]] = "net"
```

**Available constraints:** `Ge` (>=), `Gt` (>), `Le` (<=), `Lt` (<), `MinLen`, `MaxLen`, `MultipleOf`, `Pattern`.

### Nested Configurations

Compose configs hierarchically with `DEFAULT`:
`hipr.DEFAULT` is a special sentinel value that instructs `hipr` to automatically use the default configuration of the nested configurable object. This simplifies defining nested structures, ensuring that if no specific override is provided, the nested component is initialized with its own predefined defaults.

```python
@configurable
@dataclass
class Pipeline:
    model: Model = DEFAULT      # Uses Model's defaults
    optimizer: Optimizer = DEFAULT

# Override nested values
config = Pipeline.Config(
    model=Model.Config(hidden_size=512),
    optimizer=Optimizer.Config(learning_rate=0.001),
)
pipeline = config.make()  # All nested configs are instantiated
```

After `make()`, nested fields are instances:
```python
print(pipeline.model.hidden_size)      # 512
print(pipeline.optimizer.learning_rate)  # 0.001
```

### Collections & Lists

You can use standard typed collections like `list[T]` and `dict[str, T]` for configurable objects. `hipr` automatically allows passing either instances or `Config` objects for these items.

```python
from hipr import configurable, DEFAULT
from typing import Any

@configurable
@dataclass
class Layer:
    size: int = 10

@configurable
@dataclass
class Network:
    # Use standard typing - hipr handles the rest
    layers: list[Layer] = DEFAULT

config = Network.Config(
    layers=[
        Layer.Config(size=32),
        Layer.Config(size=64),
    ]
)
net = config.make()
# net.layers is now [Layer(size=32), Layer(size=64)]
```

### Nested Functions

You can also nest configurable functions using the `.Type` attribute exposed by the decorator. This allows `hipr` to automatically manage the function's configuration.

```python
@configurable
def activation(x: float, limit: Hyper[float] = 1.0) -> float:
    return min(x, limit)

@configurable
@dataclass
class Layer:
    # Use .Type to nest the function configuration.
    act_fn: activation.Type = DEFAULT  # type: ignore

!!! note
    `# type: ignore` is required if you are working in the same file with the definition of `activation`. For other files, the generated stubs will correctly expose `.Type` as a class, making the `type: ignore` unnecessary after stub generation.

config = Layer.Config()
layer = config.make()

# layer.act_fn is now a callable with 'limit' pre-bound
print(layer.act_fn(2.0))  # Output: 1.0
```

### Literal Types & Enums

Use `Literal` or `Enum` for fixed choices:

```python
from typing import Literal
from enum import Enum

class Mode(str, Enum):
    FAST = "fast"
    SLOW = "slow"

@configurable
class Processor:
    def __init__(
        self,
        mode: Literal["train", "eval"] = "train",
        priority: Mode = Mode.FAST,
    ):
        self.mode = mode
        self.priority = priority
```

## Type Checking

Generate `.pyi` stubs for full IDE support:

```bash
# Generate stubs for your source
hipr-generate-stubs src/

# Or specific files
hipr-generate-stubs my_module.py "lib/**/*.py"
```

Add to your workflow:
```toml
# pyproject.toml
[tool.poe.tasks]
stubs = "hipr-generate-stubs src/"
```

## Serialization

Configs are Pydantic models with full serialization support:

```python
config = Model.Config(hidden_size=256)

# To dict/JSON
config.model_dump()
config.model_dump_json()

# From dict/JSON
Model.Config(**some_dict)
Model.Config.model_validate_json(json_string)
```

## Advanced Features

### Methods

Instance methods also work (self is passed automatically):

```python
class Analyzer:
    @configurable
    def detect(self, data: list, threshold: Hyper[float] = 3.0) -> list:
        return [x for x in data if x > threshold]

analyzer = Analyzer()
config = analyzer.detect.Config(threshold=2.0)
result = config.make()(analyzer, [1, 2, 3, 4])
```

### Validation & Safety

- **Constraint conflicts** detected at decoration time: `Hyper[int, Ge[10], Le[5]]` → error
- **Invalid regex** patterns caught immediately
- **Circular dependencies** in nested configs → error
- **Reserved names**: `model_config` is reserved by Pydantic

### Thread Safety

`@configurable` is thread-safe for concurrent config creation and usage.

## Comparison

| Feature | hipr | gin-config | hydra | tyro |
| :--- | :--- | :--- | :--- | :--- |
| **Philosophy** | Config from code | Dependency injection | YAML-first | CLI from types |
| **Error Detection** | Decoration + Runtime | Runtime only | Runtime | CLI parse time |
| **Type Checking** | Full (.pyi stubs) | None | Partial | Full |
| **Boilerplate** | Minimal | Minimal | Moderate | Minimal |
| **Serialization** | Pydantic native | Custom | YAML | YAML/JSON |
| **Best For** | Type-safe APIs, ML experiments | Google-style DI | Complex multi-run | CLI tools |

## Performance

- Config creation: ~2µs
- `make()` overhead: ~0.1µs
- Direct function call overhead: ~0.4µs vs raw function
- Full pattern `Config().make()()`: ~6µs

See `benchmarks/` for detailed measurements.

## Contributing

Contributions welcome! Please open an issue or pull request.

## License

MIT License

---

**hipr** — Configuration should be effortless.
