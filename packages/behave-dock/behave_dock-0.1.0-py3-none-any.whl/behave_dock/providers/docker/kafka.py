from testcontainers.kafka import KafkaContainer

from behave_dock.blueprints.kafka import (
    KafkaConfig,
    KafkaInstrumentConfig,
    KafkaProviderBlueprint,
)
from behave_dock.providers.docker.base import DockerContainerProvider


class KafkaDockerProvider(
    DockerContainerProvider[KafkaContainer],
    KafkaProviderBlueprint,
):
    def __init__(
        self,
        *,
        image: str = "apache/kafka",
        tag: str = "latest",
        name: str = "kafka",
    ) -> None:
        super().__init__()
        self._image = image
        self._tag = tag
        self._name = name
        self._port = 9093

    def _get_container_definition(self) -> KafkaContainer:
        return KafkaContainer(
            f"{self._image}:{self._tag}",
            name=self.environment.generate_container_full_name(self._name),
            network=self.environment.get_network(),
            port=self._port,
        )

    def get_config(self) -> KafkaConfig:
        return KafkaConfig(
            bootstrap_servers=[
                f"{self.environment.get_container_internal_ip(self._container)}:{self._port}",
            ],
        )

    def get_instrument_config(self) -> KafkaInstrumentConfig:
        return KafkaInstrumentConfig(
            bootstrap_servers=[self._container.get_bootstrap_server()],
        )
