import contextlib

import psycopg2
from psycopg2 import sql
from psycopg2.errors import DuplicateDatabase
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from testcontainers.postgres import PostgresContainer

from behave_dock.blueprints.postgresql import (
    PostgresqlConfig,
    PostgresqlInstrumentConfig,
    PostgresqlProviderBlueprint,
)
from behave_dock.providers.docker.base import DockerContainerProvider


class PostgresqlDockerProvider(
    DockerContainerProvider[PostgresContainer],
    PostgresqlProviderBlueprint,
):
    def __init__(
        self,
        *,
        image: str = "postgres",
        tag: str = "latest",
        name: str = "postgres",
    ) -> None:
        super().__init__()
        self._image = image
        self._tag = tag
        self._name = name
        self._port = 5432

    def _get_container_definition(self) -> PostgresContainer:
        return PostgresContainer(
            f"{self._image}:{self._tag}",
            name=self.environment.generate_container_full_name(self._name),
            network=self.environment.get_network(),
            ports=[self._port],
        )

    def _ensure_database_exists(self) -> None:
        con = psycopg2.connect(
            host=self._container.get_container_host_ip(),
            port=self._container.get_exposed_port(self._port),
            user=self._container.username,
            password=self._container.password,
            dbname=self._container.dbname,
        )

        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with contextlib.suppress(DuplicateDatabase):
            con.cursor().execute(sql.SQL(f"CREATE DATABASE {self._container.dbname}"))
        con.cursor().execute(
            sql.SQL(
                f"GRANT ALL PRIVILEGES "
                f'ON DATABASE "{self._container.dbname}" '
                f"TO {self._container.username}",
            ),
        )

    def get_config(self, database_name: str) -> PostgresqlConfig:
        self._ensure_database_exists()
        return PostgresqlConfig(
            host=self.environment.get_container_internal_ip(self._container),
            port=self._port,
            username=self._container.username,
            password=self._container.password,
            database_name=database_name,
        )

    def get_instrument_config(self, database_name: str) -> PostgresqlInstrumentConfig:
        config = self.get_config(database_name)
        return PostgresqlInstrumentConfig(
            host=self._container.get_container_host_ip(),
            port=self._container.get_exposed_port(self._port),
            username=config.username,
            password=config.password,
            database_name=config.database_name,
        )
