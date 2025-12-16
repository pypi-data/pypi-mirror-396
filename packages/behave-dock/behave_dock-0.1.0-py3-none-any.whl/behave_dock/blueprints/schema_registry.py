import abc
from dataclasses import dataclass

from behave_dock.blueprints import ProviderBlueprint


@dataclass
class SchemaRegistryConfig:
    url: str
    basic_auth: str | None = None


@dataclass
class SchemaRegistryInstrumentConfig:
    # Instrument config, used by adapters
    url: str
    basic_auth: str | None = None


class SchemaRegistryProviderBlueprint(ProviderBlueprint, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_config(self) -> SchemaRegistryConfig: ...

    @abc.abstractmethod
    def get_instrument_config(self) -> SchemaRegistryInstrumentConfig: ...
