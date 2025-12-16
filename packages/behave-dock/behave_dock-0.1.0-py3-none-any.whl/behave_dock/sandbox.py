import threading
from collections.abc import Callable, Iterable
from multiprocessing.dummy import Pool as ThreadPool
from typing import ClassVar

from behave_dock.adapters import Adapter
from behave_dock.blueprints import ProviderBlueprint
from behave_dock.dependency_injector import DependencyInjector
from behave_dock.environment import Environment


class Sandbox:
    """The `Sandbox` class is the main entrypoint for the E2E Test platform.

    Usage:

    ```
    class MySandbox(Sandbox):
        environment = MyEnvironment()
        adapter_classes = [KafkaAdapter(), GatewayAPIAdapter()]
    ```

    Provide a single instance of the class you implemented to your tests, and access the
    adapters to run the tests.

    Usage in behave:
        `use_fixture(behave_dock, context, sandbox=<Your>Sandbox)`
    """

    environment: ClassVar[Environment]
    adapter_classes: ClassVar[list[Adapter]]

    def __init__(self) -> None:
        self._injector = DependencyInjector(self.environment)
        self._providers: dict[type, ProviderBlueprint] = {}
        self.adapters: dict[str, Adapter] = {}

    def setup(self) -> None:
        self.environment.setup()
        self._setup_dependencies()
        self._setup_adapters()
        self._setup_logging()

    def teardown(self) -> None:
        for adapter in self.adapters.values():
            adapter.teardown()
        for provider in self._providers.values():
            provider.teardown()
        self.environment.teardown()

    def _get_all_required_providers(self) -> dict[type, ProviderBlueprint]:
        """Collect all providers needed by adapters."""
        blueprint_to_provider_map: dict[type, ProviderBlueprint] = {}
        # Only load what our adapters need -- the rest aren't going to be tested anyway
        for adapter in self.adapter_classes:
            blueprint_to_provider_map.update(
                self._injector.get_all_dependencies_of_node(adapter),
            )
        return blueprint_to_provider_map

    def _setup_dependencies(self) -> None:
        required_blueprints = self._get_all_required_providers().keys()
        self._providers = dict(
            self._injector.resolve_and_inject_providers(
                required_blueprints,
            )
        )

        with ThreadPool(len(self._providers)) as pool:
            pool.map(lambda d: d.setup(), self._providers.values())

    def _setup_adapters(self) -> None:
        if not self.adapter_classes:
            msg = "'adapters' must be defined in sandbox"
            raise AttributeError(msg)

        self.adapters = {}
        for adapter in self.adapter_classes:
            self.adapters[adapter.key] = self._injector.inject_dependencies_to_node(
                adapter
            )

        with ThreadPool(len(self.adapters)) as pool:
            pool.map(lambda i: i.setup(), self.adapters.values())

    def _setup_logging(self) -> None:
        for provider in self._providers.values():
            for log_category, gen in provider.get_log_streams().items():
                threading.Thread(
                    target=self._get_logging_handler(provider, log_category, gen),
                    daemon=True,
                ).start()

    @staticmethod
    def _get_logging_handler(
        provider: ProviderBlueprint, log_category: str | None, iterable: Iterable[str]
    ) -> Callable[[], None]:
        def handler() -> None:
            cls_name = type(provider).__name__
            for log in iterable:
                print(
                    f"[{cls_name}] "
                    f"{'[' + log_category + '] ' if log_category else ''}"
                    f"{log}"
                )

        return handler
