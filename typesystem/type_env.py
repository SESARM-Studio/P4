from copy import deepcopy
from typing import (
    Any, # allows to type annotate that the value can be anything: Here, mostly to be consistent with type hints.
    cast # allows type hinting that a value is cast to another
)

from typesystem.data_types import TypeEnum

class TypeEnv():

    """
    Base class for the type environments
    """

    def __init__(self) -> None:
        """The empty function of a symbol table"""

        self.environment: dict[str, Any] = dict()

    def in_domain(self, identifier: str) -> bool:
        """The function for `in dom()` and `notin dom()` from the type system"""

        return identifier in self.environment

    def bind(self, identifier: str, value: Any) -> "TypeEnv":
        """Binds an identifier to a type"""

        # To match the formal type system the typeenv should be immutable
        # To achieve this with a mutable object like dict,
        # a copy of the current scope's environment is created, updated and returned
        new_env = TypeEnv()
        new_env.environment = self.environment.copy()
        new_env.environment[identifier] = value
        return new_env

    def lookup(self, identifier: str) -> Any:
        """Search current and outer scopes for the identifier binding"""

        if self.in_domain(identifier):
            return self.environment[identifier]

        return TypeEnum.UNKNOWN

class ScopedTypeEnvironment():

    """
    Implements the recursive definition of the scoped type environments
    and the two common operations for them: Enter scope and Exit scope
    """

    def __init__(self, outer_scope: "ScopedTypeEnvironment | TypeEnv" = TypeEnv(),
                 current_scope: TypeEnv = TypeEnv()
                 ) -> None:
        """The empty function of a symbol table"""

        self.current_scope: TypeEnv = current_scope
        self.outer_scope: "ScopedTypeEnvironment | TypeEnv" = outer_scope

    def lookup(self, identifier: str) -> Any:
        """Search the current scope and the outer scopes for the identifier binding"""

        lookup_type = TypeEnum.UNKNOWN
        if self.current_scope.in_domain(identifier):
            lookup_type = self.current_scope.lookup(identifier)
        else:
            lookup_type = self.outer_scope.lookup(identifier)

        return lookup_type

    def bind(self, identifier: str, value: Any) -> "ScopedTypeEnvironment":
        """Bind identifier to value in current scope"""

        new_scoped_env = deepcopy(self)
        new_scoped_env.current_scope = new_scoped_env.current_scope.bind(identifier, value)
        return new_scoped_env

    def enter_scope(self) -> "ScopedTypeEnvironment":
        """Creates a new scope the references the outer scope"""

        return ScopedTypeEnvironment(outer_scope=self)

    def exit_scope(self) -> "ScopedTypeEnvironment":
        """Exits the current scope if it is not the outermost"""

        if isinstance(self.outer_scope, TypeEnv):
            raise Exception("No scope to exit")

        return self.outer_scope

class VariableEnv(ScopedTypeEnvironment):
    """The scoped variable environment"""
    pass

class AlgorithmEnv(ScopedTypeEnvironment):
    """The scoped algorithm environment"""
    pass

class GraphEnv(ScopedTypeEnvironment):
    """The scoped graph environment"""

    def __init__(self, outer_scope: "GraphEnv | TypeEnv" = TypeEnv(), current_scope: TypeEnv = TypeEnv()) -> None:
        super().__init__(outer_scope, current_scope)
        self.outer_scope: "GraphEnv | TypeEnv" = outer_scope

    def bind(self, identifier: str, value: tuple[TypeEnum, TypeEnum, set]) -> "GraphEnv":
        return cast("GraphEnv", super().bind(identifier, value))

    def enter_scope(self) -> "GraphEnv":
        return GraphEnv(outer_scope=self)

    def update_node_set(self, identifier: str, node_set: set) -> "GraphEnv":
        """Follows the rule of the function named the same in the report"""

        if self.current_scope.in_domain(identifier):
            graph_type, graph_weight_type, graph_node_set = self.current_scope.lookup(identifier)
            self = self.bind(identifier, (graph_type, graph_weight_type, graph_node_set.union(node_set)))
            return self

        elif isinstance(self.outer_scope, TypeEnv) and self.outer_scope.in_domain(identifier):
            graph_type, graph_weight_type, graph_node_set = self.outer_scope.lookup(identifier)
            self.outer_scope = self.outer_scope.bind(
                identifier, (graph_type, graph_weight_type, graph_node_set.union(node_set))
            )
            return self

        elif isinstance(self.outer_scope, TypeEnv):
            return self

        else:
            self.outer_scope = self.outer_scope.update_node_set(identifier, node_set)
            return self

    @staticmethod
    def merge(graph_env1: TypeEnv, graph_env2: TypeEnv):
        """Merges the node sets from two of the same graph bindings into one"""

        new_graph_env = TypeEnv()
        graphs = set(graph_env1.environment).union(graph_env2.environment)

        for i in graphs:
            if graph_env1.in_domain(i) and graph_env2.in_domain(i):
                new_graph_env = new_graph_env.bind(i, GraphEnv.combine(graph_env1.lookup(i), graph_env2.lookup(i)))

            elif graph_env1.in_domain(i):
                new_graph_env = new_graph_env.bind(i, graph_env1.lookup(i))

            elif graph_env2.in_domain(i):
                new_graph_env = new_graph_env.bind(i, graph_env2.lookup(i))

            else:
                pass # varepsilon from rule = don not add binding

        return new_graph_env

    @staticmethod
    def combine(graph1: tuple[TypeEnum, TypeEnum, set],
                graph2: tuple[TypeEnum, TypeEnum, set]
                ) -> tuple[TypeEnum, TypeEnum, set]:
        """Helper function for the merge method"""

        return (graph1[0], graph1[1], graph1[2].union(graph2[2]))
