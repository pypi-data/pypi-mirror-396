import abc
from collections.abc import Iterable
from typing import Generic, TypeVar

from testcontainers.core.container import DockerContainer

from behave_dock.blueprints import ProviderBlueprint
from behave_dock.environment import DockerEnvironment
from behave_dock.exceptions import InvalidStateError

ContainerT = TypeVar("ContainerT", bound=DockerContainer)


class DockerContainerProvider(
    ProviderBlueprint,
    Generic[ContainerT],
    metaclass=abc.ABCMeta,
):
    environment: DockerEnvironment

    def __init__(self) -> None:
        self._optional_container: ContainerT | None = None

    def setup(self) -> None:
        self._start_container()

    def teardown(self) -> None:
        self._stop_container()

    def get_log_streams(self) -> dict[str | None, Iterable[str]]:
        return {None: self._get_log_stream(self._container)}

    def _start_container(self) -> None:
        container = self._get_container_definition()
        container.start()
        self._optional_container = container

    def _stop_container(self) -> None:
        self._container.stop()
        self._optional_container = None

    @property
    def _container(self) -> ContainerT:
        if not self._optional_container:
            msg = "Container is not started"
            raise InvalidStateError(msg)
        return self._optional_container

    @abc.abstractmethod
    def _get_container_definition(self) -> ContainerT: ...

    @staticmethod
    def _get_log_stream(container: ContainerT) -> Iterable[str]:
        for msg in container.get_wrapped_container().logs(stream=True, follow=True):
            yield msg.decode("utf-8").strip()
