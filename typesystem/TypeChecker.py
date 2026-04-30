from typing import Tuple

from TypeEnv import TypeEnv, TypeEnum

# import from ast folder when fixed ##->
class ASTNode:
    def __init__(self) -> None:
        self.children = []
        self.token = None
        self.value = None

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
                self.parse_statement(self.ast, env, TypeEnum.UNKNOWN)
            except Exception:
                well_formed = False
        else:
            pass

        return well_formed

    def parse_expression(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN
        match node.token:
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
                var = node.value
                var_type = env.lookup(var)

                if var_type is TypeEnum.UNKNOWN:
                    raise Exception("Identifier is not bound")

                kind = var_type

            case "graph_expression":
                expr_type = self.parse_graph_expression(node.children[0], env)

                if expr_type not in self.graph_types:
                    raise Exception(f"Graph expression should return a graph type, but was {expr_type}")

                kind = expr_type

            case "node_expression":
                expr_type = self.parse_node_expression(node.children[0], env)

                if expr_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                kind = expr_type

            case "edge_expression":
                expr_type = self.parse_edge_expression(node.children[0], env)

                if expr_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                kind = expr_type

            case "abs":
                expr_type = self.parse_expression(node.children[0], env)

                if expr_type not in self.arit_types:
                    raise Exception(f"Expression should return a arit type, but was {expr_type}")

                kind = TypeEnum.NAT

            case "magnitude":
                expr_type = self.parse_expression(node.children[0], env)

                if expr_type not in { TypeEnum.TEXT }: # missing the list types
                    raise Exception("Expression is invalid type for magnitude operation")

                kind = TypeEnum.NAT

            case "function_call":
                pass

            case "array_access":
                pass

            case "attribute_access":
                var = node.value
                var_type = env.lookup(var)

                if var_type not in { *self.graph_types, TypeEnum.NODE, TypeEnum.EDGE }:
                    raise Exception("Identifier not of correct type")

                expr_type = self.parse_expression(node.children[0], env)

                if expr_type is not TypeEnum.UNKNOWN:
                    raise Exception("Expression of unknown type")

                kind = expr_type

            case "list_expression":
                list_types = []
                for child in node.children:
                    list_types.append(self.parse_expression(child, env))

                if len(set(list_types)) > 1:
                    raise Exception("Mixing of types in list not allowed")

                kind = list_types[0] if len(list_types) > 0 else TypeEnum.UNKNOWN

            case "plus" | "minus" | "multiply" | "divide" | "modulo" | "power":
                expr1_type = self.parse_expression(node.children[0], env)
                if expr1_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                expr2_type = self.parse_expression(node.children[1], env)
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
                expr1_type = self.parse_expression(node.children[0], env)
                if expr1_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                expr2_type = self.parse_expression(node.children[1], env)
                if expr2_type is TypeEnum.UNKNOWN:
                    raise Exception("Unknown type")

                if expr1_type != expr2_type:
                    raise Exception("Type mismatch") # later they might not need to match

                kind = expr1_type

            case "negation":
                expr_type = self.parse_expression(node.children[0], env)
                if expr_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                kind = expr_type

            case "and":
                expr1_type = self.parse_expression(node.children[0], env)
                if expr1_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                expr2_type = self.parse_expression(node.children[1], env)
                if expr2_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                if expr1_type != expr2_type:
                    raise Exception("Type mismatch") # later they might not need to match

                kind = expr1_type

            case "or":
                expr1_type = self.parse_expression(node.children[0], env)
                if expr1_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                expr2_type = self.parse_expression(node.children[1], env)
                if expr2_type is not TypeEnum.BOOL:
                    raise Exception("Type must be bool")

                if expr1_type != expr2_type:
                    raise Exception("Type mismatch") # later they might not need to match

                kind = expr1_type

        setattr(node, "type", kind)
        return kind

    def parse_graph_expression(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN

        match node.token:
            case "adn":
                var1 = node.children[0].value
                var1_type = env.lookup(var1)

                if var1_type not in self.graph_types:
                    raise Exception(f"Identifier should be a graph type, but was {var1_type}")

                var2 = node.children[1].value
                var2_type = env.lookup(var2)

                if var2_type is not TypeEnum.NODE:
                    raise Exception(f"Identifier should be a node type, but was {var2_type}")

                kind = var1_type

            case "ade":
                var = node.children[0].value
                var_type = env.lookup(var)

                if var_type not in self.graph_types:
                    raise Exception(f"Identifier should be a graph type, but was {var_type}")

                expr_type = self.parse_edge_expression(node.children[0], env)
                if expr_type is not TypeEnum.EDGE:
                    raise Exception(f"Identifier should be a edge type, but was {expr_type}")

                kind = var_type

            case "rmn":
                var1 = node.children[0].value
                var1_type = env.lookup(var1)

                if var1_type not in self.graph_types:
                    raise Exception(f"Identifier should be a graph type, but was {var1_type}")

                var2 = node.children[1].value
                var2_type = env.lookup(var2)

                if var2_type is not TypeEnum.NODE:
                    raise Exception(f"Identifier should be a node type, but was {var2_type}")

                kind = var1_type

            case "rme":
                var = node.children[0].value
                var_type = env.lookup(var)

                if var_type not in self.graph_types:
                    raise Exception(f"Identifier should be a graph type, but was {var_type}")

                expr_type = self.parse_edge_expression(node.children[0], env)
                if expr_type is not TypeEnum.EDGE:
                    raise Exception(f"Identifier should be a edge type, but was {expr_type}")

                kind = var_type

        setattr(node, "type", kind)
        return kind

    def parse_node_expression(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        expr_type = self.parse_edge_expression(node.children[0], env)
        if expr_type is not TypeEnum.NODE:
            raise Exception(f"Identifier should be a node type, but was {expr_type}")

        list_expr_type = [expr_type] # unsure if this is the way
        setattr(node, "type", list_expr_type)
        return list_expr_type

    def parse_edge_expression(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN

        if node.token == "with weight?":
            var1 = node.children[0].value
            var1_type = env.lookup(var1)

            if var1_type is not TypeEnum.NODE:
                raise Exception(f"Identifier should be a node type, but was {var1_type}")

            var2 = node.children[1].value
            for var in var2:
                var2_type = env.lookup(var)
                if var2_type is not TypeEnum.NODE:
                    raise Exception(f"Identifier should be a node type, but was {var2_type}")

            kind = TypeEnum.EDGE
        else:
            var1 = node.children[0].value
            var1_type = env.lookup(var1)

            if var1_type is not TypeEnum.NODE:
                raise Exception(f"Identifier should be a node type, but was {var1_type}")

            var2 = node.children[1].value
            for var in var2:
                var2_type = env.lookup(var)
                if var2_type is not TypeEnum.NODE:
                    raise Exception(f"Identifier should be a node type, but was {var2_type}")

            weights = node.children
            weight_types = []
            for child in weights:
                weight_type = self.parse_expression(child, env)
                if weight_type not in self.arit_types:
                    raise Exception(f"Expression should return a arit type, but was {weight_type}")

                weight_types.append(weight_type)

            if len(var2) != len(weights):
                raise Exception("Not the same amount of nodes and weights")

            kind = TypeEnum.EDGE

        setattr(node, "type", kind)
        return kind

    def parse_statement(self, node: ASTNode, env: TypeEnv, curr_algo: TypeEnum) -> Tuple[TypeEnv, TypeEnum]:
        ekind: TypeEnum = TypeEnum.UNKNOWN
        match node:
            case Expression():
                self.parse_expression(node.children[0], env)
            case _:
                raise Exception("Unknown type")

        return (TypeEnv(), ekind)

    def parse_loop_modifier(self, node: ASTNode, env: TypeEnv) -> bool:
        return True

    def parse_type(self, node: ASTNode, env: TypeEnv) -> bool:
        return True

    def parse_type_arithmetic(self, node: ASTNode, env: TypeEnv) -> bool:
        return True

    def parse_graph_type(self, node: ASTNode, env: TypeEnv) -> bool:
        return True

    def parse_algorithm(self, node: ASTNode, env: TypeEnv) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def parse_declaration(self, node: ASTNode, env: TypeEnv) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def parse_declaration_list(self, node: ASTNode, env: TypeEnv) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def parse_dimensions(self, node: ASTNode, env: TypeEnv) -> bool:
        return True

    def parse_graph_declaration(self, node: ASTNode, env: TypeEnv) -> TypeEnv:
        return TypeEnv()

    def parse_graph_declaration_weight(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        return TypeEnum.UNKNOWN

if __name__ == "__main__":
    ast = ASTNode()
    checker = TypeChecker(ast)

    print(checker.parse_expression(ASTNode(), TypeEnv()))
