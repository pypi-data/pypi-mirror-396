from docker.models.containers import ExecResult
from testcontainers.core.container import DockerContainer


class ExecError(Exception):
    def __init__(self, command: str, result: ExecResult) -> None:
        super().__init__("Failed to run command", command, result)
        self.command = command
        self.result = result


def container_exec(container: DockerContainer, command: str) -> ExecResult:
    result: ExecResult = container.exec(command)
    if result.exit_code != 0:
        raise ExecError(command, result)
    return result
