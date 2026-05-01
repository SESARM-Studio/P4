from typing import Tuple

from TypeEnv import TypeEnv, TypeEnum
from remove_l8ter import *

class TypeError(Exception):

        def __init__(self, message: str) -> None:
            super().__init__(message)

class TypeChecker():

    """
    Follows the type rules of type system and annotates the AST

    **Example**

    ```python
        program = ...
        type_checker = TypeChecker(program)
        well_typed = type_checker.check()
    ```
    """

    graph_types: set[TypeEnum] = { TypeEnum.GRAPH, TypeEnum.DIGRAPH, TypeEnum.TREE }
    arit_types: set[TypeEnum] = { TypeEnum.INT, TypeEnum.NAT, TypeEnum.REAL }

    def __init__(self, ast: ASTNode) -> None:
        self.ast = ast

    def check(self) -> bool:
        well_formed = self.parse_program(self.ast.children[0], TypeEnv())
        return well_formed

    def parse_program(self, node: ASTNode, env: TypeEnv) -> bool:
        """Annotates program"""

        well_formed = True
        if isinstance(node, (
            IfStatement, WhileStatement, RepeatStatement, Chaining,
            ForEachNormal, ForEachEdge, GraphDecl, DisplayStatement, Expression,
            ReturnStatement, FunctionCall, NodeDecl, ExprGraph, ExprNode, ExprEdge
        )):
            try:
                self.parse_statement(node, env, None)
            except TypeError as e:
                print(f"Error: {e}")
                well_formed = False
        else:
            print(f"Unknown statement")
            well_formed = False

        return well_formed

    def parse_expression(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN

        if isinstance(node, Term):
            match node.type:
                case "int":
                    kind = TypeEnum.INT

                case "nat":
                    kind = TypeEnum.NAT

                case "real":
                    kind = TypeEnum.REAL

                case "text":
                    kind = TypeEnum.TEXT

                case "bool":
                    kind = TypeEnum.BOOL

                case "identifier":
                    var = node.value
                    var_type = env.lookup(var)

                    if var_type is TypeEnum.UNKNOWN:
                        raise TypeError("Identifier is not bound")

                    kind = var_type
        elif isinstance(node, Expression):
            match node.operator:
                case "+" | "-" | "*" | "/" | "%" | "^":
                    expr1_type = self.parse_expression(node.arg1, env)
                    if expr1_type is TypeEnum.UNKNOWN:
                        raise TypeError("Left operand of arith was an unknown type")

                    expr2_type = self.parse_expression(node.arg2, env)
                    if expr2_type is TypeEnum.UNKNOWN:
                        raise TypeError("Right operand of arith was an unknown type")

                    if expr1_type != expr2_type:
                        raise TypeError("Type mismatch") # later they might not need to match

                    kind = expr1_type

            #     case "graph_expression":
            #         expr_type = self.parse_graph_expression(node.children[0], env)

            #         if expr_type not in self.graph_types:
            #             raise TypeError(f"Graph expression should return a graph type, but was {expr_type}")

            #         kind = expr_type

            #     case "node_expression":
            #         expr_type = self.parse_node_expression(node.children[0], env)

            #         if expr_type is TypeEnum.UNKNOWN:
            #             raise TypeError("Unknown type")

            #         kind = expr_type

            #     case "edge_expression":
            #         expr_type = self.parse_edge_expression(node.children[0], env)

            #         if expr_type is TypeEnum.UNKNOWN:
            #             raise TypeError("Unknown type")

            #         kind = expr_type

            #     case "abs":
            #         expr_type = self.parse_expression(node.children[0], env)

            #         if expr_type not in self.arit_types:
            #             raise TypeError(f"Expression should return a arit type, but was {expr_type}")

            #         kind = TypeEnum.NAT

            #     case "magnitude":
            #         expr_type = self.parse_expression(node.children[0], env)

            #         if expr_type not in { TypeEnum.TEXT }: # missing the list types
            #             raise TypeError("Expression is invalid type for magnitude operation")

            #         kind = TypeEnum.NAT

            #     case "function_call":
            #         pass

            #     case "array_access":
            #         pass

            #     case "attribute_access":
            #         var = node.value
            #         var_type = env.lookup(var)

            #         if var_type not in { *self.graph_types, TypeEnum.NODE, TypeEnum.EDGE }:
            #             raise TypeError("Identifier not of correct type")

            #         expr_type = self.parse_expression(node.children[0], env)

            #         if expr_type is not TypeEnum.UNKNOWN:
            #             raise TypeError("Expression of unknown type")

            #         kind = expr_type

            #     case "list_expression":
            #         list_types = []
            #         for child in node.children:
            #             list_types.append(self.parse_expression(child, env))

            #         if len(set(list_types)) > 1:
            #             raise TypeError("Mixing of types in list not allowed")

            #         kind = list_types[0] if len(list_types) > 0 else TypeEnum.UNKNOWN

            #     case "weight_of -->":
            #         pass

            #     case "weight_of ---":
            #         pass

                case "=" | "!=" | "<" | "<=" | ">" | ">=":
                    expr1_type = self.parse_expression(node.arg1, env)
                    if expr1_type is TypeEnum.UNKNOWN:
                        raise TypeError("Left operand of comparison was an unknown type")

                    expr2_type = self.parse_expression(node.arg2, env)
                    if expr2_type is TypeEnum.UNKNOWN:
                        raise TypeError("Right operand of comparison was an unknown type")

                    if expr1_type != expr2_type:
                        raise TypeError("Type mismatch") # later they might not need to match

                    kind = TypeEnum.BOOL

                case "neg":
                    expr_type = self.parse_expression(node.arg1, env)
                    if expr_type is not TypeEnum.BOOL:
                        raise TypeError("Type must be bool")

                    kind = expr_type

                case "and":
                    expr1_type = self.parse_expression(node.arg1, env)
                    if expr1_type is not TypeEnum.BOOL:
                        raise TypeError("Type must be bool")

                    expr2_type = self.parse_expression(node.arg2, env)
                    if expr2_type is not TypeEnum.BOOL:
                        raise TypeError("Type must be bool")

                    if expr1_type != expr2_type:
                        raise TypeError("Type mismatch") # later they might not need to match

                    kind = expr1_type

                case "or":
                    expr1_type = self.parse_expression(node.arg1, env)
                    if expr1_type is not TypeEnum.BOOL:
                        raise TypeError("Type must be bool")

                    expr2_type = self.parse_expression(node.arg2, env)
                    if expr2_type is not TypeEnum.BOOL:
                        raise TypeError("Type must be bool")

                    if expr1_type != expr2_type:
                        raise TypeError("Type mismatch") # later they might not need to match

                    kind = expr1_type

                case _:
                    raise TypeError("Unknown operator")

        # setattr(node, "type", kind)
        return kind

    def parse_graph_expression(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN

        # match node.token:
        #     case "adn":
        #         var1 = node.children[0].value
        #         var1_type = env.lookup(var1)

        #         if var1_type not in self.graph_types:
        #             raise TypeError(f"Identifier should be a graph type, but was {var1_type}")

        #         var2 = node.children[1].value
        #         var2_type = env.lookup(var2)

        #         if var2_type is not TypeEnum.NODE:
        #             raise TypeError(f"Identifier should be a node type, but was {var2_type}")

        #         kind = var1_type

        #     case "ade":
        #         var = node.children[0].value
        #         var_type = env.lookup(var)

        #         if var_type not in self.graph_types:
        #             raise TypeError(f"Identifier should be a graph type, but was {var_type}")

        #         expr_type = self.parse_edge_expression(node.children[0], env)
        #         if expr_type is not TypeEnum.EDGE:
        #             raise TypeError(f"Identifier should be a edge type, but was {expr_type}")

        #         kind = var_type

        #     case "rmn":
        #         var1 = node.children[0].value
        #         var1_type = env.lookup(var1)

        #         if var1_type not in self.graph_types:
        #             raise TypeError(f"Identifier should be a graph type, but was {var1_type}")

        #         var2 = node.children[1].value
        #         var2_type = env.lookup(var2)

        #         if var2_type is not TypeEnum.NODE:
        #             raise TypeError(f"Identifier should be a node type, but was {var2_type}")

        #         kind = var1_type

        #     case "rme":
        #         var = node.children[0].value
        #         var_type = env.lookup(var)

        #         if var_type not in self.graph_types:
        #             raise TypeError(f"Identifier should be a graph type, but was {var_type}")

        #         expr_type = self.parse_edge_expression(node.children[0], env)
        #         if expr_type is not TypeEnum.EDGE:
        #             raise TypeError(f"Identifier should be a edge type, but was {expr_type}")

        #         kind = var_type

        setattr(node, "type", kind)
        return kind

    def parse_node_expression(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        pass
        # expr_type = self.parse_edge_expression(node.children[0], env)
        # # if expr_type is not TypeEnum.NODE:
        # #     raise TypeError(f"Identifier should be a node type, but was {expr_type}")

        # list_expr_type = [expr_type] # unsure if this is the way
        # setattr(node, "type", list_expr_type)
        # return list_expr_type

    def parse_edge_expression(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN

        # if node.token == "with weight?":
        #     var1 = node.children[0].value
        #     var1_type = env.lookup(var1)

        #     if var1_type is not TypeEnum.NODE:
        #         raise TypeError(f"Identifier should be a node type, but was {var1_type}")

        #     var2 = node.children[1].value
        #     for var in var2:
        #         var2_type = env.lookup(var)
        #         if var2_type is not TypeEnum.NODE:
        #             raise TypeError(f"Identifier should be a node type, but was {var2_type}")

        #     kind = TypeEnum.EDGE
        # else:
        #     var1 = node.children[0].value
        #     var1_type = env.lookup(var1)

        #     if var1_type is not TypeEnum.NODE:
        #         raise TypeError(f"Identifier should be a node type, but was {var1_type}")

        #     var2 = node.children[1].value
        #     for var in var2:
        #         var2_type = env.lookup(var)
        #         if var2_type is not TypeEnum.NODE:
        #             raise TypeError(f"Identifier should be a node type, but was {var2_type}")

        #     weights = node.children
        #     weight_types = []
        #     for child in weights:
        #         weight_type = self.parse_expression(child, env)
        #         if weight_type not in self.arit_types:
        #             raise TypeError(f"Expression should return a arit type, but was {weight_type}")

        #         weight_types.append(weight_type)

        #     if len(var2) != len(weights):
        #         raise TypeError("Not the same amount of nodes and weights")

        #     kind = TypeEnum.EDGE

        setattr(node, "type", kind)
        return kind

    def parse_statement(self, node: ASTNode, env: TypeEnv, curr_algo: str | None) -> TypeEnv:
        return_env: TypeEnv = env

        match node:

            case Chaining():
                stmt1_env = self.parse_statement(node.variable, env, curr_algo)
                stmt2_env = self.parse_statement(node.chain_part, stmt1_env, curr_algo)
                return_env = stmt2_env

            case Assignment():
                if node.variable is None:
                    raise TypeError("Assignment variable cannot be none")
                var_type = env.lookup(node.variable)

                expr_type = self.parse_expression(node.expression[0], env)

                if var_type != expr_type:
                    raise TypeError(f"Cannot assign expression of type {expr_type} to variable of type {var_type}")

            case IfStatement():
                if_kind = self.parse_expression(node.if_part[0], env)
                if if_kind != TypeEnum.BOOL:
                    raise TypeError(f"If part should be bool but was {if_kind}")

                self.parse_statement(node.then_part[0], env, curr_algo)

                if len(node.else_part) != 0:
                    self.parse_statement(node.else_part[0], env, curr_algo)

            case WhileStatement():
                cond_kind = self.parse_expression(node.condition[0], env)
                if cond_kind != TypeEnum.BOOL:
                    raise TypeError(f"Condition part should be bool but was {cond_kind}")

                self.parse_statement(node.statements[0], env, curr_algo)

            case RepeatStatement():
                repeat_expression = self.parse_expression(node.repeat_expression[0], env)
                if repeat_expression != TypeEnum.NAT:
                    raise TypeError(f"Repeat expression should be NAT but was {repeat_expression}")

                self.parse_statement(node.repeat_statements[0], env, curr_algo)

            case ForEachNormal():
                iterable = self.parse_expression(node.iterable[0], env)

                env.enter_scope()
                env.bind(node.loop_variable, iterable)

                self.parse_statement(node.statements[0], env, curr_algo)

                env.exit_scope()

            case ForEachEdge():
                # edge_type = self.parse_expression(node.edge[0], env)
                # if edge_type is not TypeEnum.EDGE:
                #     raise TypeError(f"Edge part should be EDGE but was {edge_type}")
                pass

            case ReturnStatement():
                if curr_algo is None:
                    raise TypeError("Return cannot be used outside function")

                expected_return_type = env.lookup(curr_algo)
                return_type = self.parse_expression(node.expression[0], env)

                if expected_return_type != return_type:
                    raise TypeError("Return type does not match function")

            case Expression():
                self.parse_expression(node, env)

            case GraphDecl():
                pass

            case DisplayStatement():
                display_expr = self.parse_expression(node.expression[0], env)
                if display_expr is TypeEnum.UNKNOWN:
                    raise TypeError("Cannot display unknown type")

            case _:
                raise TypeError(f"Unknown statement type: {node.__class__.__name__}")

        return return_env

    def parse_loop_modifier(self, node: ASTNode, env: TypeEnv) -> bool:
        if node.token == "Loopmodifier":
            return True

        return False

    def parse_type(self, node: ASTNode, env: TypeEnv) -> bool:
        well_formed = False
        match node.token:
            case "bool" | "text" | "node" | "edge":
                well_formed = True
            case "tarit":
                well_formed = self.parse_type_arithmetic(node, env)
            case "graphtype":
                well_formed = self.parse_graph_type(node, env)

        return well_formed

    def parse_type_arithmetic(self, node: ASTNode, env: TypeEnv) -> bool:
        return node.token in { "int", "nat", "real" }

    def parse_graph_type(self, node: ASTNode, env: TypeEnv) -> bool:
        return node.token in { "graph", "digraph", "tree" }

    def parse_algorithm(self, node: ASTNode, env: TypeEnv) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def parse_declaration(self, node: ASTNode, env: TypeEnv) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def parse_declaration_list(self, node: ASTNode, env: TypeEnv) -> Tuple[TypeEnv, TypeEnum]:
        return (TypeEnv(), TypeEnum.UNKNOWN)

    def parse_dimensions(self, node: ASTNode, env: TypeEnv) -> bool:
        # if node.token == "Nd":
        #     kind = self.parse_expression(node, env)
        #     if kind != TypeEnum.NAT:
        #         return False

        return True

    def parse_graph_declaration(self, node: ASTNode, env: TypeEnv) -> TypeEnv:
        return TypeEnv()

    def parse_graph_declaration_weight(self, node: ASTNode, env: TypeEnv) -> TypeEnum:
        return TypeEnum.UNKNOWN

if __name__ == "__main__":
    program = ASTNode("")

    checker = TypeChecker(program)
    print(f"well formed: {checker.check()}")
