from pushikoo_interface import ProcesserConfig, ProcesserInstanceConfig
from pydantic import Field

# ProcesserConfig and ProcesserInstanceConfig inherit from pydantic.BaseModel,
# so when defining your own ClassConfig / InstanceConfig,
# you are essentially defining a BaseModel and can fully use all BaseModel features.


class AdapterConfig(ProcesserConfig):
    field1: float = Field(default=1, description="")


class InstanceConfig(ProcesserInstanceConfig):
    field1: float = Field(default=1, description="")
