# BehaveDock

> E2E testing for people who'd rather write tests than YAML.

BehaveDock is a Python framework for end-to-end testing that gets out of your way. Define your dependencies once, swap implementations per environment, and let dependency injection do the wiring.

Built on top of [Behave](https://behave.readthedocs.io/) and [testcontainers](https://testcontainers-python.readthedocs.io/).

## Why?

E2E testing usually means:

1. Writing a bunch of Docker Compose files
2. Bash scripts to wait for services
3. More bash scripts to seed data
4. Even more scripts to tear everything down
5. Tests that break when someone changes a port number

BehaveDock flips this around. You declare *what* your tests need to work (a database, a message broker, your microservices), implement *how* to provide it (Docker, staging, mocks), and the framework handles the rest.

Same tests. Different environments. No YAML required.

## Install

```bash
pip install behave-dock
```

## Quick Start

```python
# 1. Define what you need (blueprint)
class DatabaseBlueprint(ProviderBlueprint, abc.ABC):
    @abc.abstractmethod
    def execute_query(self, query: str) -> list[dict]: ...

# 2. Implement how to provide it (provider)
class PostgresDockerProvider(DockerContainerProvider, DatabaseBlueprint):
    def _get_container_definition(self) -> PostgresContainer:
        return PostgresContainer("postgres:15")
    
    def execute_query(self, query: str) -> list[dict]:
        # ... actual implementation

# 3. Create a test interface (adapter)
class MyAdapter(Adapter):
    key = "app"
    database: DatabaseBlueprint  # <- injected automatically
    
    def create_user(self, name: str) -> None:
        self.database.execute_query(f"INSERT INTO users ...")

# 4. Wire it up (environment + sandbox)
class MyEnvironment(Environment):
    def get_blueprint_to_provider_map(self) -> dict[type, ProviderBlueprint]:
        return {DatabaseBlueprint: PostgresDockerProvider()}

class MySandbox(Sandbox):
    environment = MyEnvironment()
    adapter_classes = [MyAdapter()]

# 5. Use in Behave
def before_all(context) -> None:
    use_fixture(behave_dock, context, sandbox=MySandbox)

# 6. Write tests
@given("a user exists")
def step_impl(context) -> None:
    context.sandbox.adapters["app"].create_user("alice")
```

## Features

- **Blueprints** — Abstract interfaces for your dependencies
- **Providers** — Concrete implementations (Docker, mocks, staging)
- **Adapters** — Test interfaces your step definitions actually use
- **Dependency Injection** — Declare dependencies as type hints, get them injected
- **Lifecycle Management** — Setup and teardown handled automatically
- **Built-in Providers** — Kafka, PostgreSQL, Redis, RabbitMQ, Schema Registry

## Built-in Components

### Blueprints

- `KafkaProviderBlueprint`
- `PostgresqlProviderBlueprint`
- `RedisProviderBlueprint`
- `RabbitMQProviderBlueprint`
- `SchemaRegistryProviderBlueprint`

### Docker Providers

- `KafkaDockerProvider`
- `PostgresqlDockerProvider`
- `RedisDockerProvider`
- `RabbitMQDockerProvider`
- `SchemaRegistryDockerProvider`

### Adapters

- `KafkaAdapter` — Produce messages to Kafka
- `APIAdapter` — HTTP requests with session management

## Examples

Check out the [`examples/`](./examples) directory for a complete tutorial building a Todo app with:

- Custom blueprints and providers
- SQLite in-memory database
- Dependency injection between providers
- Behave integration

```bash
cd examples/todo_app
python -m behave features/
```

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                        Sandbox                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │                   Environment                     │  │
│  │  ┌─────────────┐  ┌─────────────┐                │  │
│  │  │  Blueprint  │  │  Blueprint  │  ...           │  │
│  │  │      ↓      │  │      ↓      │                │  │
│  │  │  Provider   │  │  Provider   │                │  │
│  │  └─────────────┘  └─────────────┘                │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │                    Adapters                       │  │
│  │  ┌─────────────┐  ┌─────────────┐                │  │
│  │  │   Adapter   │  │   Adapter   │  ...           │  │
│  │  │ (injected)  │  │ (injected)  │                │  │
│  │  └─────────────┘  └─────────────┘                │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                              │
│                   Your Behave Tests                     │
└─────────────────────────────────────────────────────────┘
```

1. **Sandbox** orchestrates everything
2. **Environment** maps blueprints → providers
3. **Providers** are set up in dependency order (so that each provider has access to all dependencies)
4. **Tests** interact only with adapters
