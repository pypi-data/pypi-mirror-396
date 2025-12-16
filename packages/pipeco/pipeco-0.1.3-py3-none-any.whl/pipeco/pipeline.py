"""Pipeline orchestration for composing type-safe steps."""
from pydantic import BaseModel
from pipeco.contracts import Step, Context

class Pipeline:
    """Chains steps together with compile-time type checking."""
    def __init__(self, steps: list[Step]) -> None:
        """Create pipeline and verify type compatibility between steps."""
        if not steps:
            raise ValueError("Pipeline needs at least one step")
        # Type-compatibility check at build time
        for a, b in zip(steps, steps[1:]):
            if a.output_model is not b.input_model:
                raise TypeError(
                    f"Type mismatch: {a.name} -> {b.name} "
                    f"({a.output_model.__name__} != {b.input_model.__name__})"
                )
        self.steps = steps

    def run(self, data: BaseModel, ctx: Context | None = None) -> BaseModel:
        """Execute pipeline steps sequentially with validation at each step."""
        ctx = ctx or Context()
        x = data
        for step in self.steps:
            x = step(x, ctx)  # each step re-validates I and O
        return x

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.steps == other.steps