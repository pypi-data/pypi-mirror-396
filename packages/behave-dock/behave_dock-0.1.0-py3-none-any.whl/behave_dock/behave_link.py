from collections.abc import Generator

from behave import fixture
from behave.runner import Context

from behave_dock.sandbox import Sandbox


@fixture  # type: ignore[misc]
def behave_dock(  # type: ignore[no-untyped-def]
    context: Context, sandbox: type[Sandbox], *args, **kwargs
) -> Generator[Sandbox, None, None]:
    context.sandbox = sandbox()
    context.sandbox.setup()
    yield context.sandbox
    context.sandbox.teardown()
