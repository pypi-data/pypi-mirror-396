from testcontainers.redis import RedisContainer

from behave_dock.blueprints.redis import (
    RedisConfig,
    RedisInstrumentConfig,
    RedisProviderBlueprint,
)
from behave_dock.providers.docker.base import DockerContainerProvider


class RedisDockerProvider(
    DockerContainerProvider[RedisContainer],
    RedisProviderBlueprint,
):
    def __init__(
        self,
        *,
        image: str = "redis/redis-stack-server",
        tag: str = "latest",
        name: str = "redis",
    ) -> None:
        super().__init__()
        self._image = image
        self._tag = tag
        self._name = name
        self._database_ids: dict[str, int] = {}
        self._port = 6379

    def _get_container_definition(self) -> RedisContainer:
        return RedisContainer(
            f"{self._image}:{self._tag}",
            name=self.environment.generate_container_full_name(self._name),
            network=self.environment.get_network(),
            ports=[self._port],
        )

    def get_config(self, database_name: str) -> RedisConfig:
        db_id = self._database_ids.get(database_name)
        if not db_id:
            self._database_ids[database_name] = db_id = len(self._database_ids) + 1

        return RedisConfig(
            host=self.environment.get_container_internal_ip(self._container),
            port=self._port,
            password="",
            database_id=db_id,
        )

    def get_instrument_config(self, database_name: str) -> RedisInstrumentConfig:
        config = self.get_config(database_name)
        return RedisInstrumentConfig(
            host=self._container.get_container_host_ip(),
            port=self._container.get_exposed_port(self._port),
            password=config.password,
            database_id=config.database_id,
        )
