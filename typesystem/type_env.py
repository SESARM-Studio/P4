from typing import Any

from typesystem.data_types import TypeEnum

class TypeEnv():

    """
    Base class for the type environments
    """

    def __init__(self) -> None:
        """The empty function of a symbol table"""

        self.environment: dict[str, Any] = dict()

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

        if identifier in self.environment:
            return self.environment[identifier]

        return TypeEnum.UNKNOWN

class ScopedTypeEnvironment():

    """
    Implements the recursive definition of the scoped type environments
    and the two common operations for them: Enter scope and Exit scope
    """

    def __init__(self, outer_scope: "ScopedTypeEnvironment | None" = None,
                 current_scope: TypeEnv = TypeEnv()
                 ) -> None:
        """The empty function of a symbol table"""

        self.current_scope: TypeEnv = current_scope
        self.outer_scope: "ScopedTypeEnvironment | None" = outer_scope

    def lookup(self, identifier: str) -> Any:
        """Search the current scope and the outer scopes for the identifier binding"""

        lookup_type = self.current_scope.lookup(identifier)

        if lookup_type == TypeEnum.UNKNOWN: # identifier not found in the current scope
            lookup_type = self.outer_scope.lookup(identifier) if self.outer_scope else TypeEnum.UNKNOWN

        return lookup_type

    def enter_scope(self) -> "ScopedTypeEnvironment":
        """Creates a new scope the references the outer scope"""

        return ScopedTypeEnvironment(outer_scope=self)

    def exit_scope(self) -> "ScopedTypeEnvironment":
        """Exits the current scope if it is not the outermost"""

        if self.outer_scope is None:
            raise Exception("No scope to exit")

        return self.outer_scope

class VariableEnv(TypeEnv):
    pass

class AlgorithmEnv(TypeEnv):
    pass

class GraphEnv(TypeEnv):
    pass
