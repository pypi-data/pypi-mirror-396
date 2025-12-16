from typing import Any
from urllib.parse import urlsplit, urlunsplit

from kafka import KafkaProducer
from kafka_schema_registry import prepare_producer

from behave_dock.blueprints.kafka import KafkaProviderBlueprint
from behave_dock.blueprints.schema_registry import SchemaRegistryProviderBlueprint

from .base import Adapter


class KafkaAdapter(Adapter):
    key = "kafka"

    kafka: KafkaProviderBlueprint
    schema_registry: SchemaRegistryProviderBlueprint

    def get_kafka_producer(
        self,
        topic_name: str,
        value_schema: dict[str, Any] | None = None,
        key_schema: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> KafkaProducer:
        bootstrap_servers = self.kafka.get_instrument_config().bootstrap_servers
        schema_registry_config = self.schema_registry.get_config()

        parts = urlsplit(schema_registry_config.url, allow_fragments=True)
        netloc = (schema_registry_config.basic_auth or "") + "@" + parts.netloc
        schema_registry_url = urlunsplit(
            (parts.scheme, netloc, parts.path, parts.query, parts.fragment),
        )

        return prepare_producer(
            bootstrap_servers,
            schema_registry_url,
            topic_name=topic_name,
            key_schema=key_schema,
            value_schema=value_schema,
            num_partitions=1,
            replication_factor=1,
            **kwargs,
        )
