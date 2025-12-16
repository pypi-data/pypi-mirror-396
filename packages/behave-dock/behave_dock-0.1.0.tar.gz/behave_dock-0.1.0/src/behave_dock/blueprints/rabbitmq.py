import abc
from dataclasses import dataclass

from behave_dock.blueprints import ProviderBlueprint


@dataclass
class RabbitMqConfig:
    host: str
    port: int
    username: str
    password: str
    vhost: str


@dataclass
class RabbitMqInstrumentConfig:
    # Instrument config, used by adapters
    host: str
    port: int
    username: str
    password: str
    vhost: str


class RabbitMqProviderBlueprint(ProviderBlueprint, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_config(self, vhost: str) -> RabbitMqConfig: ...

    @abc.abstractmethod
    def get_instrument_config(self, vhost: str) -> RabbitMqInstrumentConfig: ...
