from typing import Tuple

from TypeEnv import TypeEnv, TypeEnum

# import from ast folder when fixed ##->
class ASTNode:
    pass

class Program(ASTNode):
    pass

class Statement(ASTNode):
    pass

class Expression(ASTNode):
    pass
###
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

    graph_types: set[TypeEnum] = { TypeEnum.GRAPH, TypeEnum.DIGRAPH, TypeEnum.TREE }
    arit_types: set[TypeEnum] = { TypeEnum.INT, TypeEnum.NAT, TypeEnum.REAL }

    def __init__(self, ast: ASTNode) -> None:
        self.ast = ast

    def parse_program(self, env: TypeEnv) -> bool:
        """Annotates program"""

        well_formed = True
        if isinstance(self.ast, Statement):
            try:
                self.__parse_statement(env, TypeEnum.UNKNOWN)
            except Exception:
                well_formed = False
        else:
            pass

        return well_formed

    def __parse_expression(self, env: TypeEnv) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN
        match getattr(self.ast, "token"):
            case "integer":
                kind = TypeEnum.INT

            case "natural":
                kind = TypeEnum.NAT

            case "real":
                kind = TypeEnum.REAL

            case "string":
                kind = TypeEnum.TEXT

            case "boolean":
                kind = TypeEnum.BOOL

            case "identifier":
                var = getattr(self.ast, "value")
                var_type = env.lookup(var)

                if var_type is TypeEnum.UNKNOWN:
                    raise Exception("Identifier is not bound")

                kind = var_type

            case "graph_expression":
                expr_type = self.__parse_graph_expression(env)

                if expr_type not in self.graph_types:
                    raise Exception(f"Graph expression should return a graph type, but was {expr_type}")

                kind = expr_type

            case "node_expression":
                expr_type = self.__parse_node_expression(env)

                if expr_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                kind = expr_type

            case "edge_expression":
                expr_type = self.__parse_edge_expression(env)

                if expr_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                kind = expr_type

            case "abs":
                expr_type = self.__parse_expression(env)

                if expr_type not in self.arit_types:
                    raise Exception(f"Expression should return a arit type, but was {expr_type}")

                kind = TypeEnum.NAT

            case "magnitude":
                expr_type = self.__parse_expression(env)

                if expr_type not in { TypeEnum.TEXT }: # missing the list types
                    raise Exception("Expression is invalid type for magnitude operation")

                kind = TypeEnum.NAT

            case "function_call":
                pass

            case "array_access":
                pass

            case "attribute_access":
                var = getattr(self.ast, "value")
                var_type = env.lookup(var)

                if var_type not in { *self.graph_types, TypeEnum.NODE, TypeEnum.EDGE }:
                    raise Exception("Identifier not of correct type")

                expr_type = self.__parse_expression(env)

                if expr_type is not TypeEnum.UNKNOWN:
                    raise Exception("Expression of unknown type")

                kind = expr_type

            case "list_expression":
                list_types = []
                for expr in getattr(self.ast, "children"):
                    list_types.append(self.__parse_expression(env))

                if not all(list_types):
                    raise Exception("Mixing of types in list not allowed")

                kind = list_types[0] if len(list_types) > 0 else TypeEnum.UNKNOWN

            case "plus" | "minus" | "multiply" | "divide" | "modulo" | "power":
                expr1_type = self.__parse_expression(env)
                if expr1_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                expr2_type = self.__parse_expression(env)
                if expr2_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                if expr1_type != expr2_type:
                    raise Exception("Type mismatch") # later they might not need to match

                kind = expr1_type
                pass

            case "weight_of -->":
                pass

            case "weight_of ---":
                pass

            case (
                "equal"
                | "not_equal"
                | "smaller_than"
                | "smaller_than_or_equal"
                | "greater_than"
                | "greater_than_or_equal"
            ):
                expr1_type = self.__parse_expression(env)
                if expr1_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                expr2_type = self.__parse_expression(env)
                if expr2_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                if expr1_type != expr2_type:
                    raise Exception("Type mismatch") # later they might not need to match

                kind = expr1_type

            case "negation":
                expr_type = self.__parse_expression(env)
                if expr_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                kind = expr_type

            case "and":
                expr1_type = self.__parse_expression(env)
                if expr1_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                expr2_type = self.__parse_expression(env)
                if expr2_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                if expr1_type != expr2_type:
                    raise Exception("Type mismatch") # later they might not need to match

                kind = expr1_type

            case "or":
                expr1_type = self.__parse_expression(env)
                if expr1_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                expr2_type = self.__parse_expression(env)
                if expr2_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                if expr1_type != expr2_type:
                    raise Exception("Type mismatch") # later they might not need to match

                kind = expr1_type

        setattr(self.ast, "type", kind)
        return kind

    def __parse_graph_expression(self, env: TypeEnv) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN

        match getattr(self.ast, "token"): # missing structure knowledge
            case "adn":
                var1 = getattr(self.ast, "value")
                var1_type = env.lookup(var1)

                if var1_type not in self.graph_types:
                    raise Exception(f"Identifier should be a graph type, but was {var1_type}")

                var2 = getattr(self.ast, "value")
                var2_type = env.lookup(var2)

                if var2_type is not TypeEnum.NODE:
                    raise Exception(f"Identifier should be a node type, but was {var2_type}")

                kind = var1_type

            case "ade":
                var = getattr(self.ast, "value")
                var_type = env.lookup(var)

                if var_type not in self.graph_types:
                    raise Exception(f"Identifier should be a graph type, but was {var_type}")

                expr_type = self.__parse_edge_expression(env)
                if expr_type is not TypeEnum.EDGE:
                    raise Exception(f"Identifier should be a edge type, but was {expr_type}")

                kind = var_type

            case "rmn":
                var1 = getattr(self.ast, "value")
                var1_type = env.lookup(var1)

                if var1_type not in self.graph_types:
                    raise Exception(f"Identifier should be a graph type, but was {var1_type}")

                var2 = getattr(self.ast, "value")
                var2_type = env.lookup(var2)

                if var2_type is not TypeEnum.NODE:
                    raise Exception(f"Identifier should be a node type, but was {var2_type}")

                kind = var1_type

            case "rme":
                var = getattr(self.ast, "value")
                var_type = env.lookup(var)

                if var_type not in self.graph_types:
                    raise Exception(f"Identifier should be a graph type, but was {var_type}")

                expr_type = self.__parse_edge_expression(env)
                if expr_type is not TypeEnum.EDGE:
                    raise Exception(f"Identifier should be a edge type, but was {expr_type}")

                kind = var_type

        setattr(self.ast, "type", kind)
        return kind

    def __parse_node_expression(self, env: TypeEnv) -> TypeEnum:
        expr_type = self.__parse_edge_expression(env)
        if expr_type is not TypeEnum.NODE:
            raise Exception(f"Identifier should be a node type, but was {expr_type}")

        list_expr_type = [expr_type] # unsure if this is the way
        setattr(self.ast, "type", list_expr_type)
        return list_expr_type

    def __parse_edge_expression(self, env: TypeEnv) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN

        if getattr(self.ast, "token") == "with weight?":
            var1 = getattr(self.ast, "value")
            var1_type = env.lookup(var1)

            if var1_type is not TypeEnum.NODE:
                raise Exception(f"Identifier should be a node type, but was {var1_type}")

            var2 = getattr(self.ast, "value")
            for var in var2:
                var2_type = env.lookup(var)
                if var2_type is not TypeEnum.NODE:
                    raise Exception(f"Identifier should be a node type, but was {var2_type}")

            kind = TypeEnum.EDGE
        else:
            var1 = getattr(self.ast, "value")
            var1_type = env.lookup(var1)

            if var1_type is not TypeEnum.NODE:
                raise Exception(f"Identifier should be a node type, but was {var1_type}")

            var2 = getattr(self.ast, "value")
            for var in var2:
                var2_type = env.lookup(var)
                if var2_type is not TypeEnum.NODE:
                    raise Exception(f"Identifier should be a node type, but was {var2_type}")

            weights = getattr(self.ast, "children")
            weight_types = []
            for weight in weights:
                weight_type = self.__parse_expression(env)
                if weight_type not in self.arit_types:
                    raise Exception(f"Expression should return a arit type, but was {expr_type}")

                weight_types.append(weight_type)

            if len(var2) != len(weights):
                raise Exception("Not the same amount of nodes and weights")

            kind = TypeEnum.EDGE

        setattr(self.ast, "type", kind)
        return kind

    def __parse_statement(self, env: TypeEnv, kind: TypeEnum) -> Tuple[TypeEnv, TypeEnum]:
        ekind: TypeEnum = TypeEnum.UNKNOWN
        match self.ast:
            case Expression():
                self.__parse_expression(env)
            case _:
                raise Exception("Unknown type")

        return (TypeEnv(), ekind)

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
