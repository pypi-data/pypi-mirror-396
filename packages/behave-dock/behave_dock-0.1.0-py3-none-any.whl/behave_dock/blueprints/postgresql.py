import abc
from dataclasses import dataclass

from behave_dock.blueprints import ProviderBlueprint


@dataclass
class PostgresqlConfig:
    host: str
    port: int
    username: str
    password: str
    database_name: str


@dataclass
class PostgresqlInstrumentConfig:
    # Instrument config, used by adapters
    host: str
    port: int
    username: str
    password: str
    database_name: str


class PostgresqlProviderBlueprint(ProviderBlueprint, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_config(self, database_name: str) -> PostgresqlConfig: ...

    @abc.abstractmethod
    def get_instrument_config(
        self,
        database_name: str,
    ) -> PostgresqlInstrumentConfig: ...

    def get_instrument_uri(self, database_name: str) -> str:
        config = self.get_instrument_config(database_name)
        return (
            f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}"
            f"/{config.database_name}"
        )
