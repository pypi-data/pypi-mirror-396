"""Core contracts for the PipeCo pipeline framework."""
from typing import TypeVar, Generic, Any
from pydantic import BaseModel, ValidationError
import abc, logging

I = TypeVar("I", bound=BaseModel)
O = TypeVar("O", bound=BaseModel)
C = TypeVar("C", bound=BaseModel)

class Context(BaseModel):
    """Shared context passed through pipeline execution.
    
    Provides logging, shared resources, and caching across steps.
    """
    model_config = {"arbitrary_types_allowed": True}
    logger: logging.Logger = logging.getLogger()
    resources: dict[str, Any] = {}
    cache: dict[str, Any] = {}

class Step(Generic[I, O, C], abc.ABC):
    """Base class for type-safe pipeline steps.
    
    Enforces strict input/output validation using Pydantic models.
    Override `process()` to implement step logic.
    """
    name: str
    input_model: type[I]
    output_model: type[O]
    config_model: type[C]

    def __init__(self, config: C | dict[str, Any] | None = None) -> None:
        """Initialize step with optional configuration."""
        if config is None:
            self.config: C = self.config_model()
        elif isinstance(config, BaseModel):
            if not isinstance(config, self.config_model):
                raise TypeError(f"Bad config type for {self.__class__.__name__}")
            self.config = config
        else:
            self.config = self.config_model(**config)

    @abc.abstractmethod
    def process(self, data: I, ctx: Context) -> O:
        """Process input data and return output. Override this method."""
        ...

    def __call__(self, data: BaseModel | dict[str, Any], ctx: Context) -> BaseModel:
        """Execute step with automatic validation of inputs and outputs."""
        # Validate input to I
        try:
            i: I = data if isinstance(data, self.input_model) else self.input_model.model_validate(data)
        except ValidationError as e:
            raise TypeError(f"{self.name}: input validation failed") from e

        ctx.logger.info(f"Starting step: {self.name}")
        out = self.process(i, ctx)

        # Validate output to O
        try:
            return out if isinstance(out, self.output_model) else self.output_model.model_validate(out)
        except ValidationError as e:
            raise TypeError(f"{self.name}: output validation failed") from e
        
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.config == other.config

class Nothing(BaseModel):
    """Empty model."""
    pass
