import abc
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from behave_dock.environment import Environment


class Adapter(abc.ABC):
    """The `Adapter` class is the base class that allows your tests to communicate
    with providers and execute their preparation, operation, and assertion steps.
    All communication with providers happen only through instances of the
    `Adapter` class.

    Just like provider classes, you can have any provider injected into your interface
    by type-hinting the provider blueprint class you need as a class variable.
    The provider will be injected in your instance by the test platform.
    Example: `kafka: KakfaBlueprint`

    The `key` class variable specifies how your tests can access this adapter from the
    sandbox instance. If the key is set to, say, 'kafka', your tests can access the
    interface like this: `sandbox.test_interface['kafka']`
    """

    key: ClassVar[str]
    environment: "Environment"

    @abc.abstractmethod
    def setup(self) -> None: ...

    @abc.abstractmethod
    def teardown(self) -> None: ...
