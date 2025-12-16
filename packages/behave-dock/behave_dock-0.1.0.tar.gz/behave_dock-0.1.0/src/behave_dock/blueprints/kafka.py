import abc
import contextlib
from dataclasses import dataclass

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from behave_dock.blueprints import ProviderBlueprint


@dataclass
class KafkaConfig:
    bootstrap_servers: list[str]


@dataclass
class KafkaInstrumentConfig:
    # Instrument config, used by adapters
    bootstrap_servers: list[str]
    sasl_username: str | None = None
    sasl_password: str | None = None
    sasl_mechanism: str | None = None
    security_protocol: str | None = None


class KafkaProviderBlueprint(ProviderBlueprint, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_config(self) -> KafkaConfig: ...

    @abc.abstractmethod
    def get_instrument_config(self) -> KafkaInstrumentConfig: ...

    def get_admin_client(self) -> KafkaAdminClient:
        config = self.get_instrument_config()
        return KafkaAdminClient(
            bootstrap_servers=config.bootstrap_servers,
            sasl_mechanism=config.sasl_mechanism,
            sasl_plain_username=config.sasl_username,
            sasl_plain_password=config.sasl_password,
        )

    def ensure_topic_exists(self, topic_name: str) -> None:
        topic_list = [NewTopic(name=topic_name, num_partitions=1, replication_factor=1)]
        with contextlib.suppress(TopicAlreadyExistsError):
            self.get_admin_client().create_topics(
                new_topics=topic_list,
                validate_only=False,
            )
