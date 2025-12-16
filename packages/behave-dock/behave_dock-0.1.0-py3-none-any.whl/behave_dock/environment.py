import abc
import random
from collections.abc import Mapping

from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

from behave_dock.blueprints import ProviderBlueprint
from behave_dock.exceptions import InvalidStateError


class Environment(metaclass=abc.ABCMeta):
    """Resolves the provider instance for any provider blueprint.

    Inherit from this class in your code, and override the
    `get_blueprint_to_provider_map` method to return a dictionary mapping blueprint
    classes to their implementation in your desired environment.
    """

    def __init__(self) -> None:
        # Provider objects need to live through the entire test suite, that's why we
        # initialize them once here.
        self._blueprint_map = self.get_blueprint_to_provider_map()

    @abc.abstractmethod
    def setup(self) -> None: ...

    @abc.abstractmethod
    def teardown(self) -> None: ...

    @abc.abstractmethod
    def get_blueprint_to_provider_map(
        self,
    ) -> Mapping[type, ProviderBlueprint]:
        """Return a mapping of blueprint classes to their provider instances.

        Keys must be abstract ProviderBlueprint subclasses.
        Blueprint classes serve as identifiers for dependency injection.

        Values are concrete provider instances implementing those blueprints.

        Note: The return type uses bare 'type' instead of 'type[ProviderBlueprint]'
        because Python's type system treats type[T] as "concrete instantiable class",
        which rejects abstract blueprints.
        """

    def get_provider_for_blueprint(
        self,
        blueprint_class: type,
    ) -> ProviderBlueprint:
        if not issubclass(blueprint_class, ProviderBlueprint):
            msg = f"'{blueprint_class}' is not a subclass of 'ProviderBlueprint'."
            raise TypeError(msg)
        if blueprint_class not in self._blueprint_map:
            msg = f"Provider blueprint '{blueprint_class}' is not implemented."
            raise NotImplementedError(msg)
        return self._blueprint_map[blueprint_class]


class DockerEnvironment(Environment, metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        super().__init__()
        self._random_prefix = f"{random.getrandbits(20):05x}"
        self._network = Network()

    def setup(self) -> None:
        self._network.create()

    def teardown(self) -> None:
        self._network.remove()

    @abc.abstractmethod
    def get_project_name(self) -> str: ...

    def get_network(self) -> Network:
        return self._network

    def generate_container_full_name(self, name: str) -> str:
        return f"{self.get_project_name()}_{self._random_prefix}_{name}"

    def get_container_internal_ip(self, container: DockerContainer) -> str:
        container_id = container.get_wrapped_container().id
        if not container_id:
            msg = "Container is not started yet; can't access internal IP"
            raise InvalidStateError(
                msg,
            )
        raw_container = container.get_docker_client().get_container(
            container_id,
        )
        return str(
            raw_container["NetworkSettings"]["Networks"][self._network.name][
                "IPAddress"
            ]
        )
