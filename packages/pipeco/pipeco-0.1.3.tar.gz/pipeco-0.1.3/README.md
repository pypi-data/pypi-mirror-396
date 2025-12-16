# PipeCo 🔗

**Type-safe, composable data pipelines built on Pydantic**

PipeCo is a lightweight Python framework for building robust data processing pipelines with compile-time type checking. Define your steps with clear input/output contracts, and PipeCo ensures they connect correctly.

## ✨ Features

- **Type Safety**: Pydantic-based validation at every step boundary
- **Compile-Time Checks**: Catches type mismatches before execution
- **Clean Abstractions**: Simple `Step` base class for building reusable components
- **Registry System**: Register and discover steps by name
- **Context Sharing**: Pass loggers, resources, and cache between steps
- **Easy Composition**: Chain steps together with confidence

## 📦 Installation

```bash
pip install pipeco
```

Or with uv:
```bash
uv add pipeco
```

## 🚀 Quick Start

### 1. Define Your Data Models

```python
from pipeco import BaseModel

class InputData(BaseModel):
    text: str

class ProcessedData(BaseModel):
    upper_text: str
    length: int
```

### 2. Create Pipeline Steps

```python
from pipeco import Step, Context, register

@register("uppercase")
class UppercaseStep(Step[InputData, ProcessedData, Nothing]):
    input_model = InputData
    output_model = ProcessedData
    config_model = Nothing
    
    def process(self, data: InputData, ctx: Context) -> ProcessedData:
        return ProcessedData(
            upper_text=data.text.upper(),
            length=len(data.text)
        )
```

### 3. Build and Run Your Pipeline

```python
from pipeco import Pipeline, get_step

# Create pipeline
pipeline = Pipeline(steps=[
    get_step("uppercase")()
])

# Run it
result = pipeline.run(InputData(text="hello world"))
print(result.upper_text)  # "HELLO WORLD"
print(result.length)       # 11
```

## 📚 Core Concepts

### Step

The `Step` class is the building block of pipelines. Each step:
- Declares its input type (`I`), output type (`O`), and configuration type (`C`)
- Implements the `process()` method for business logic
- Automatically validates inputs and outputs using Pydantic

### Pipeline

The `Pipeline` chains steps together and:
- Verifies type compatibility at initialization (compile-time checking)
- Validates data at each step boundary (runtime checking)
- Passes context through all steps

### Context

The `Context` object flows through your pipeline, providing:
- **Logger**: Centralized logging
- **Resources**: Shared objects (DB connections, API clients, etc.)
- **Cache**: Data sharing between non-adjacent steps

### Registry

Use `@register()` to make steps discoverable by name:
```python
from pipeco import get_step

StepClass = get_step("step-name")
step_instance = StepClass(config)
```

## 🎯 Example: CSV Processing

See `examples/pipelines.py` for a complete example that:
1. Reads a CSV file
2. Transforms the data
3. Saves the result

```python
pipeline = Pipeline(steps=[
    CSVPathToDict(),
    ChangeFavoriteFood(),
    SaveDictToCSV({"save_path": "output.csv"})
])

pipeline.run(ExampleCSVModel(csv_path="input.csv"))
```

## 🛡️ Type Safety

PipeCo catches mismatches early:

```python
# This raises TypeError at pipeline creation:
Pipeline(steps=[
    StepA(),  # outputs TypeX
    StepB(),  # expects TypeY (incompatible!)
])
```

## 📖 API Reference

### `Step[I, O, C]`
Base class for pipeline steps.
- `process(data: I, ctx: Context) -> O`: Override this method

### `Pipeline`
- `__init__(steps: list[Step])`: Create pipeline with type checking
- `run(data: BaseModel, ctx: Context | None) -> BaseModel`: Execute pipeline

### `Context`
- `logger`: logging.Logger instance
- `resources`: Shared resources dict
- `cache`: Data cache dict

### `@register(name: str)`
Decorator to register step classes.

### `get_step(name: str) -> type[Step]`
Retrieve registered step class by name.

## 🤝 Contributing

Contributions welcome! This is a lightweight framework designed to stay simple.

## 📄 License

See LICENSE file for details.

## 🔗 Links

- [GitHub](https://github.com/aelefebv/pipeco)
- [Issues](https://github.com/aelefebv/pipeco/issues)
