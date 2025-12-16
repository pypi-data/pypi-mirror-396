from testcontainers.rabbitmq import RabbitMqContainer

from behave_dock.blueprints.rabbitmq import (
    RabbitMqConfig,
    RabbitMqInstrumentConfig,
    RabbitMqProviderBlueprint,
)
from behave_dock.providers.docker.base import DockerContainerProvider
from behave_dock.utils.exec import container_exec


class RabbitMqDockerProvider(
    DockerContainerProvider[RabbitMqContainer], RabbitMqProviderBlueprint
):
    def __init__(
        self,
        *,
        image: str = "rabbitmq",
        tag: str = "latest",
        name: str = "rabbitmq",
    ) -> None:
        super().__init__()
        self._image = image
        self._tag = tag
        self._name = name
        self._vhosts: set[str] = set()
        self._port = 5672

    def _get_container_definition(self) -> RabbitMqContainer:
        return RabbitMqContainer(
            f"{self._image}/:{self._tag}",
            name=self.environment.generate_container_full_name(self._name),
            network=self.environment.get_network(),
            ports=[self._port],
        )

    def get_config(self, vhost: str) -> RabbitMqConfig:
        if vhost not in self._vhosts:
            container_exec(self._container, f"rabbitmqctl add_vhost {vhost}")
            container_exec(self._container, f"rabbitmqctl add_user {vhost} {vhost}")
            container_exec(
                self._container,
                f"rabbitmqctl set_permissions -p {vhost} {vhost} '.*' '.*' '.*'",
            )
            self._vhosts.add(vhost)
        return RabbitMqConfig(
            host=self.environment.get_container_internal_ip(self._container),
            port=self._port,
            username=vhost,
            password=vhost,
            vhost=vhost,
        )

    def get_instrument_config(self, vhost: str) -> RabbitMqInstrumentConfig:
        config = self.get_config(vhost)
        return RabbitMqInstrumentConfig(
            host=self._container.get_container_host_ip(),
            port=self._container.get_exposed_port(self._port),
            username=config.username,
            password=config.password,
            vhost=config.vhost,
        )
