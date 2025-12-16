import abc
import typing

if typing.TYPE_CHECKING:
    from behave_dock.environment import Environment


class ProviderBlueprint(metaclass=abc.ABCMeta):
    """The base class for defining the components of the application being tested.

    Each component is defined by inheriting this class, and overriding `setup`,
    `teardown`, and `get_log_streams` methods accordingly.

    You can expose additional functionality from your blueprint to be used by
    adapters or other providers by defining extra methods.

    Please note that direct subclasses of this class should not be used directly in
    tests. Instead, define abstract blueprints of your components (like
    `KafkaBlueprint`, `PostgresqlBlueprint`, etc.) and implement them according to the
    environment they'll run inside (like `KafkaDockerProvider`,
    `PostgresqlStagingProvider`, etc.)

    You can access other blueprint providers by type-hinting the base blueprint class
    you need as a class variable. The blueprint provider instance will be injected in
    your instance by the test platform.

    Example: `kafka: KafkaBlueprint`
    """

    environment: "Environment"

    @abc.abstractmethod
    def setup(self) -> None: ...

    @abc.abstractmethod
    def teardown(self) -> None: ...

    @abc.abstractmethod
    def get_log_streams(self) -> dict[str | None, typing.Iterable[str]]: ...
