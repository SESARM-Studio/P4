from typesystem.data_types import TypeEnum

class TypeEnv():

    """
    Symbol table implementation for the type environment in the type system

    **Example**

    ```python
        env = TypeEnv()
        env.bind("test", TypeEnum.INT)

        identifier = env.lookup("test")
        if identifer is not None:
            print(f"Found binding: {identifier}")
        else:
            print(f"Binding not found: {identifier}")
    ```
    """

    def __init__(self, outer_scope: "TypeEnv | None" = None) -> None:
        """The empty function of a symbol table"""

        self.environment = dict()
        self.outer_scope = outer_scope

    def bind(self, identifier, value) -> None:
        """Binds an identifier to a type"""

        self.environment[identifier] = value

    def lookup(self, identifier):
        """Search current and outer scopes for the identifier binding"""

        scope = self
        while scope is not None:
            if identifier in scope.environment:
                return scope.environment[identifier]
            scope = scope.outer_scope

        return TypeEnum.UNKNOWN

    def enter_scope(self) -> "TypeEnv":
        """Creates a new scope the references the outer scope"""
        return TypeEnv(outer_scope=self)

    def exit_scope(self) -> "TypeEnv":
        """Exits the current scope if it is not the outermost"""

        if self.outer_scope is None:
            return self

        return self.outer_scope
