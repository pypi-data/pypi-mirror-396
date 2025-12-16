import abc
from dataclasses import dataclass

from behave_dock.blueprints import ProviderBlueprint


@dataclass
class RedisConfig:
    host: str
    port: int
    password: str
    database_id: int


@dataclass
class RedisInstrumentConfig:
    # Instrument config, used by adapters
    host: str
    port: int
    password: str
    database_id: int


class RedisProviderBlueprint(ProviderBlueprint, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_config(self, database_name: str) -> RedisConfig: ...

    @abc.abstractmethod
    def get_instrument_config(self, database_name: str) -> RedisInstrumentConfig: ...
