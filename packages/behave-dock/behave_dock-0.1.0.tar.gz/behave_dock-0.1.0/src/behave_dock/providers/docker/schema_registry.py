from testcontainers.core.container import DockerContainer

from behave_dock.blueprints.kafka import KafkaProviderBlueprint
from behave_dock.blueprints.schema_registry import (
    SchemaRegistryConfig,
    SchemaRegistryInstrumentConfig,
    SchemaRegistryProviderBlueprint,
)
from behave_dock.providers.docker.base import DockerContainerProvider


class SchemaRegistryDockerProvider(
    DockerContainerProvider[DockerContainer],
    SchemaRegistryProviderBlueprint,
):
    kafka: KafkaProviderBlueprint

    def __init__(
        self,
        *,
        image: str = "confluentinc/cp-schema-registry",
        tag: str = "latest",
        name: str = "schema_registry",
    ) -> None:
        super().__init__()
        self._image = image
        self._tag = tag
        self._name = name
        self._port = 8081

    def _get_container_definition(self) -> DockerContainer:
        container_name = self.environment.generate_container_full_name(self._name)
        bootstrap_servers = ",".join(
            [
                "PLAINTEXT://" + bootstrap_server
                for bootstrap_server in self.kafka.get_config().bootstrap_servers
            ],
        )
        return DockerContainer(
            f"{self._image}:{self._tag}",
            name=container_name,
            env={
                "SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS": bootstrap_servers,
                "SCHEMA_REGISTRY_HOST_NAME": container_name,
                "SCHEMA_REGISTRY_LISTENERS": "http://0.0.0.0:8081",
            },
            ports=[self._port],
            network=self.environment.get_network(),
        )

    def get_config(self) -> SchemaRegistryConfig:
        return SchemaRegistryConfig(
            url=f"http://{self.environment.get_container_internal_ip(self._container)}:{self._port}",
            basic_auth="admin:admin",
        )

    def get_instrument_config(self) -> SchemaRegistryInstrumentConfig:
        config = self.get_config()
        return SchemaRegistryInstrumentConfig(
            url=f"http://{self._container.get_container_host_ip()}:{self._container.get_exposed_port(self._port)}",
            basic_auth=config.basic_auth,
        )
