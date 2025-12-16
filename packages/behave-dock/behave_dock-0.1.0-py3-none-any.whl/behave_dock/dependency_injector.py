import graphlib
from collections.abc import Iterable, Mapping
from inspect import isclass
from typing import TypeVar, get_args, get_type_hints

from behave_dock.adapters import Adapter
from behave_dock.blueprints import ProviderBlueprint
from behave_dock.environment import Environment

_DependencyNode = ProviderBlueprint | Adapter
_TypeDependencyNode = TypeVar("_TypeDependencyNode", bound=_DependencyNode)
_T = TypeVar("_T")


class DependencyInjector:
    """Handles dependency injection for providers and adapters.

    Responsibilities:
    - Discover dependencies via type hints
    - Resolve providers from environment
    - Topologically sort dependencies for correct setup order
    - Inject resolved dependencies into instances
    """

    def __init__(self, environment: Environment) -> None:
        self._environment = environment
        self._providers: dict[type, ProviderBlueprint] = {}

    def get_all_dependencies_of_node(
        self,
        node: _DependencyNode,
    ) -> Mapping[type, ProviderBlueprint]:
        """Recursively collect all providers that a provider depends on."""
        output: dict[type, ProviderBlueprint] = {}
        for dep_class in self._get_direct_dependencies_of_node(node).values():
            provider = self._get_node_for_blueprint(dep_class)
            output[dep_class] = provider
            output.update(self.get_all_dependencies_of_node(provider))
        return output

    @staticmethod
    def _get_direct_dependencies_of_node(
        blueprint: _DependencyNode,
    ) -> Mapping[str, type[ProviderBlueprint]]:
        """Extract blueprint's direct dependencies from type hints."""
        node_class = type(blueprint)
        module = __import__(node_class.__module__, fromlist=[""])

        return {
            name: dependency_class
            for name, dependency_class in get_type_hints(
                node_class,
                globalns=getattr(module, "__dict__", {}),
                localns=None,
            ).items()
            if isclass(dependency_class)
            and issubclass(dependency_class, get_args(_DependencyNode))
        }

    def _get_node_for_blueprint(
        self,
        blueprint: type,
    ) -> ProviderBlueprint:
        """Get provider instance from environment."""
        return self._environment.get_provider_for_blueprint(blueprint)

    def inject_dependencies_to_node(
        self, target: _TypeDependencyNode
    ) -> _TypeDependencyNode:
        """Inject resolved provider dependencies into target instance."""
        for name, dep_class in self._get_direct_dependencies_of_node(
            target,
        ).items():
            setattr(target, name, self._providers[dep_class])
        return target

    def _topological_sort(
        self,
        blueprint_classes: Iterable[type[_T]],
    ) -> Iterable[type[_T]]:
        """Sort blueprint classes in topological order based on their dependencies.

        This ensures providers are set up in the correct order (dependencies first).
        """
        blueprint_list = list(blueprint_classes)
        id_to_class_map = {id(dep_cls): dep_cls for dep_cls in blueprint_list}
        dependency_graph = {
            id(dep_cls): [
                id(dep_cls2)
                for dep_cls2 in self._get_direct_dependencies_of_node(
                    self._get_node_for_blueprint(dep_cls),
                ).values()
            ]
            for dep_cls in blueprint_list
        }

        # Filter to only return classes that were in the original input
        return (
            id_to_class_map[key]
            for key in graphlib.TopologicalSorter(dependency_graph).static_order()
            if key in id_to_class_map
        )

    def resolve_and_inject_providers(
        self,
        blueprint_classes: Iterable[type[ProviderBlueprint]],
    ) -> Mapping[type, ProviderBlueprint]:
        """Resolve all providers for given blueprints and inject their dependencies.

        Returns a mapping from blueprint classes to their injected provider instances.
        """
        for blueprint_class in self._topological_sort(blueprint_classes):
            provider = self._get_node_for_blueprint(blueprint_class)
            self._providers[blueprint_class] = self.inject_dependencies_to_node(
                provider
            )

        return self._providers
