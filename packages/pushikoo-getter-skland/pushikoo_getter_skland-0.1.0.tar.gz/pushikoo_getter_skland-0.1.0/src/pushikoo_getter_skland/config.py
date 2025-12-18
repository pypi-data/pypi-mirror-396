from pydantic import Field
from pushikoo_interface import GetterConfig, GetterInstanceConfig


class SklandAdapterConfig(GetterConfig):
    page_size_min: int = Field(default=5, description="Minimum page size for feed list")
    page_size_max: int = Field(
        default=11, description="Maximum page size for feed list"
    )


class SklandInstanceConfig(GetterInstanceConfig):
    phone: str = Field(default="", description="Hypergryph phone number")
    password: str = Field(default="", description="Hypergryph password")
