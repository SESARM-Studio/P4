from typing import Tuple

from TypeEnv import TypeEnv, TypeEnum

class ASTNode: # import from ast folder when fixed
    pass

class TypeChecker():

    """
    Follows the type rules of type system and annotates the AST

    **Example**

    ```python
        ast = ...
        type_checker = TypeChecker(ast)
        well_typed: = type_checker.parse_program(TypeEnv())
    ```
    """

    def __init__(self, ast: ASTNode) -> None:
        self.ast = ast

    def parse_program(self, env: TypeEnv) -> bool:
        """Annotates program"""

        well_formed = True
        if getattr(self.ast, "token") == "Statement":
            try:
                self.__parse_statement(env, TypeEnum.UNKNOWN)
            except Exception:
                well_formed = False
        else:
            pass

        return well_formed

    def __parse_expression(self, env: TypeEnv) -> TypeEnum:
        return TypeEnum.UNKNOWN

    def __parse_graph_expression(self, env: TypeEnv) -> TypeEnum:
        return TypeEnum.UNKNOWN

    def __parse_node_expression(self, env: TypeEnv) -> TypeEnum:
        return TypeEnum.UNKNOWN

    def __parse_edge_expression(self, env: TypeEnv) -> TypeEnum:
        return TypeEnum.UNKNOWN

    def __parse_statement(self, env: TypeEnv, kind: TypeEnum) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def __parse_loop_modifier(self, env: TypeEnv) -> bool:
        return True

    def __parse_type(self, env: TypeEnv) -> bool:
        return True

    def __parse_type_arithmetic(self, env: TypeEnv) -> bool:
        return True

    def __parse_graph_type(self, env: TypeEnv) -> bool:
        return True

    def __parse_algorithm(self, env: TypeEnv) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def __parse_declaration(self, env: TypeEnv) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def __parse_declaration_list(self, env: TypeEnv) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def __parse_dimensions(self, env: TypeEnv) -> bool:
        return True

    def __parse_graph_declaration(self, env: TypeEnv) -> TypeEnv:
        return TypeEnv()

    def __parse_graph_declaration_weight(self, env: TypeEnv) -> TypeEnum:
        return TypeEnum.UNKNOWN

if __name__ == "__main__":
    ast = ASTNode()
    checker = TypeChecker(ast)

    print(checker._TypeChecker__parse_expression(TypeEnv()))
