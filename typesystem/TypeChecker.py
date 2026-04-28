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
        well_formed = self.parse_program(self.ast)
        return well_formed

    def parse_program(self, node: ASTNode) -> bool:
        """Annotates program"""
        if str(node.token).upper() != "PROGRAM":
            raise Exception("parse_program: Implementation error")

        well_formed = False
        if node != None: # program can only be statement or none
            try:
                self.parse_statement(node.children[0], TypeEnv(), TypeEnv(), TypeEnv(), None, None)
                well_formed = True
            except TypeError as e:
                print(f"TypeError: {e}")
        else: # empty programs are also valid
            well_formed = True

        return well_formed

    def parse_expression(self,
                         node: ASTNode,
                         env_v: TypeEnv,
                         env_a: TypeEnv,
                         env_g: TypeEnv,
                         curr_graph: str | None
                         ) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN
        match node:
            case Term():
                match node.type:
                    case "int" | TypeEnum.INT:
                        kind = TypeEnum.INT

                    case "nat" | TypeEnum.NAT:
                        kind = TypeEnum.NAT

                    case "real" | TypeEnum.REAL:
                        kind = TypeEnum.REAL

                    case "text" | TypeEnum.TEXT:
                        kind = TypeEnum.TEXT

                    case "bool" | TypeEnum.BOOL:
                        kind = TypeEnum.BOOL

                    case "identifier":
                        ident = node.value
                        ident_type = env_v.lookup(ident)

                        if ident_type is TypeEnum.UNKNOWN:
                            raise TypeError("Identifier is not bound")

                        kind = ident_type

                    case _:
                        raise TypeError("Unknown term type")

            case GraphStatment():
                gexpr_type = self.parse_graph_expression(node, env_v, env_g)

                if gexpr_type not in self.graph_types:
                    raise TypeError(f"Graph expression should return a graph type, but was {gexpr_type}")

                kind = gexpr_type

            case ExprNode():
                nexpr_type = self.parse_node_expression(node, env_v)

                if (
                    isinstance(nexpr_type, list)
                    and nexpr_type
                    and not all(typ == TypeEnum.NODE for typ in nexpr_type)
                ):
                    raise TypeError(f"Type should be list of nodes but was {nexpr_type}")

                kind = nexpr_type # special type (list[TypeEnum])

            case EdgeDecl():
                eexpr_type = self.parse_edge_expression(node, env_v, env_g, curr_graph)

                if eexpr_type is not TypeEnum.EDGE:
                    raise TypeError(f"Type should be edge but was {eexpr_type}")

                kind = eexpr_type

            case AbsoluteValue():
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, curr_graph)

                if expr_type not in self.arit_types:
                    raise TypeError(f"Type should be one of {self.arit_types} but was {expr_type}")

                kind = TypeEnum.NAT

            case Magnitude():
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, curr_graph)

                if expr_type is not TypeEnum.TEXT and isinstance(expr_type, list):
                    raise TypeError("Expression is invalid type for the magnitude operation")

                kind = TypeEnum.NAT

            case FunctionCall():
                ident = node.variable
                algo_type = env_a.lookup(ident)

                arg_types_index = 0
                return_type_index = 1
                for idx, expr in enumerate(node.arguments):
                    expr_type = self.parse_expression(expr, env_v, env_a, env_g, curr_graph)
                    if algo_type[arg_types_index][idx] != expr_type: # algo_type = tuple[tuple[arg_type], return_type]
                        raise TypeError(
                            f"Arguments did not match the expected parameter type: {algo_type[arg_types_index][idx]} "
                            f"but was {expr_type}"
                        )

                kind = algo_type[return_type_index]

            case ArrayAccess():
                for index in node.indexes:
                    expr_type = self.parse_expression(index, env_v, env_a, env_g, curr_graph)

                    if expr_type is not TypeEnum.NAT:
                        raise TypeError(f"Array access index should be type nat but was {expr_type}")

                ident = node.variable
                array_type = env_v.lookup(ident)
                if array_type is not TypeEnum.UNKNOWN:
                    raise TypeError("Array type is not bound")

                kind = array_type

            case ExprChaining():
                ident = node.variable

                graph_type, graph_weight_type = env_g.lookup(ident)
                var_type = env_v.lookup(ident)
                if not (
                    graph_type not in self.graph_types
                    and graph_weight_type not in self.arit_types
                    or var_type not in { TypeEnum.NODE, TypeEnum.EDGE }
                ):
                    raise TypeError("Identifier not of correct type")

                expr_type = self.parse_expression(node.chain_part, env_v, env_a, env_g, curr_graph)
                if expr_type is not TypeEnum.UNKNOWN:
                    raise TypeError("Expression of unknown type")

                kind = expr_type

            # case "ListExpression": #how this? i think we are missing this rule
            #     list_types = []
            #     for child in node.children:
            #         list_types.append(self.parse_expression(child, env))

            #     if len(set(list_types)) > 1:
            #         raise TypeError("Mixing of types in list not allowed")

            #     kind = list_types[0] if len(list_types) > 0 else TypeEnum.UNKNOWN

            case Expression():
                match node.operator:
                    case "+" | "-" | "*" | "/" | "%" | "^":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, curr_graph)
                        if expr1_type is TypeEnum.UNKNOWN:
                            raise TypeError("Left operand of arith was an unknown type")

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, curr_graph)
                        if expr2_type is TypeEnum.UNKNOWN:
                            raise TypeError("Right operand of arith was an unknown type")

                        if expr1_type != expr2_type:
                            raise TypeError("Type mismatch") # later they might not need to match

                        kind = expr1_type

                    case EdgeDecl(): # this correct? (wot) or (woe)
                        ident = node.initial_node

                        graph_type, graph_weight_type = env_g.lookup(ident)
                        if node.direction == "-->":
                            if graph_type not in { TypeEnum.DIGRAPH, TypeEnum.TREE }:
                                raise TypeError(
                                    f"Graph type should be a directed graph type but was {graph_type}"
                                )
                        else: # ---
                            if graph_type not in { TypeEnum.DIGRAPH, TypeEnum.TREE }:
                                raise TypeError(
                                    f"Graph type should be a undirected graph type but was {graph_type}"
                                )

                        if graph_weight_type not in self.arit_types:
                            raise TypeError(
                                f"Graph weight type should be an arithmetic type but was {graph_weight_type}"
                            )

                        ident2 = node.nodes[0]
                        var_type = env_v.lookup(ident2)
                        if var_type is not TypeEnum.NODE:
                            raise TypeError(f"Variable should be the node type but was {var_type}")

                        ident3 = node.nodes[0]
                        var_type2 = env_v.lookup(ident3)
                        if var_type2 is not TypeEnum.NODE:
                            raise TypeError(f"Variable should be the node type but was {var_type2}")

                        kind = graph_weight_type

                    case "=" | "!=" | "<" | "<=" | ">" | ">=":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, curr_graph)
                        if expr1_type is TypeEnum.UNKNOWN:
                            raise TypeError("Left operand of comparison was an unknown type")

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, curr_graph)
                        if expr2_type is TypeEnum.UNKNOWN:
                            raise TypeError("Right operand of comparison was an unknown type")

                        if expr1_type != expr2_type:
                            raise TypeError("Type mismatch") # later they might not need to match

                        kind = TypeEnum.BOOL

                    case "neg":
                        expr_type = self.parse_expression(node.arg1, env_v, env_a, env_g, curr_graph)
                        if expr_type is not TypeEnum.BOOL:
                            raise TypeError("Type must be bool")

                        kind = expr_type

                    case "and":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, curr_graph)
                        if expr1_type is not TypeEnum.BOOL:
                            raise TypeError("Type must be bool")

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, curr_graph)
                        if expr2_type is not TypeEnum.BOOL:
                            raise TypeError("Type must be bool")

                        if expr1_type != expr2_type:
                            raise TypeError("Type mismatch") # later they might not need to match

                        kind = expr1_type

                    case "or":
                        print(expr1_type)
                        if expr1_type is not TypeEnum.BOOL:
                            raise TypeError("Type must be bool")

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, curr_graph)
                        if expr2_type is not TypeEnum.BOOL:
                            raise TypeError("Type must be bool")

                        if expr1_type != expr2_type:
                            raise TypeError("Type mismatch") # later they might not need to match

                        kind = expr1_type

                    case _:
                        raise TypeError("Unknown operator")

            case _:
                raise TypeError("Unknown expression type")

        setattr(node, "type", kind)
        return kind

    def parse_graph_expression(self, node: ASTNode, env_v: TypeEnv, env_g: TypeEnv) -> TypeEnum:
        if not isinstance(node, GraphStatment):
            raise Exception("parse_graph_expression: Implementation error")

        kind: TypeEnum = TypeEnum.UNKNOWN

        if node.operator == "add":
            if "identifier":
                graph_type, graph_weight_type = env_g.lookup(node.graph_variable)
                if graph_type not in self.graph_types:
                    raise TypeError(f"Identifier should be a graph type, but was {graph_type}")
                if graph_weight_type not in self.arit_types:
                    raise TypeError(f"Graph weight type should be a arithmetic type, but was {graph_weight_type}")

                ident = node.argument[0] # I_2
                ident_type = env_v.lookup(ident)
                if ident_type is not TypeEnum.NODE:
                    raise TypeError(f"Identifier should be a node type, but was {ident_type}")

                kind = graph_type
            else: # edge expr
                graph_type, graph_weight_type = env_g.lookup(node.graph_variable)
                if graph_type not in self.graph_types:
                    raise TypeError(f"Identifier should be a graph type, but was {graph_type}")
                if graph_weight_type not in self.arit_types:
                    raise TypeError(f"Graph weight type should be a arithmetic type, but was {graph_weight_type}")

                edge_expr = node.argument[0]
                expr_type = self.parse_edge_expression(edge_expr, env_v, env_g, None)
                if expr_type is not TypeEnum.EDGE:
                    raise TypeError(f"Edge expression type should be a edge type, but was {expr_type}")

                kind = graph_type
        else: # remove
            if "identfier":
                graph_type, graph_weight_type = env_g.lookup(node.graph_variable)
                if graph_type not in self.graph_types:
                    raise TypeError(f"Identifier should be a graph type, but was {graph_type}")
                if graph_weight_type not in self.arit_types:
                    raise TypeError(f"Graph weight type should be a arithmetic type, but was {graph_weight_type}")

                ident = node.argument[0] # I_2
                ident_type = env_v.lookup(ident)
                if ident_type is not TypeEnum.NODE:
                    raise TypeError(f"Identifier should be a node type, but was {ident_type}")

                kind = graph_type
            else: #edge expr
                graph_type, graph_weight_type = env_g.lookup(node.graph_variable)
                if graph_type not in self.graph_types:
                    raise TypeError(f"Identifier should be a graph type, but was {graph_type}")
                if graph_weight_type not in self.arit_types:
                    raise TypeError(f"Graph weight type should be a arithmetic type, but was {graph_weight_type}")

                edge_expr = node.argument[0]
                expr_type = self.parse_edge_expression(edge_expr, env_v, env_g, None)
                if expr_type is not TypeEnum.EDGE:
                    raise TypeError(f"Edge expression type should be a edge type, but was {expr_type}")

                kind = graph_type

        setattr(node, "type", kind)
        return kind

    def parse_node_expression(self,
                              node: ASTNode,
                              env_v: TypeEnv,
                              env_a: TypeEnv,
                              env_g: TypeEnv
                              ) -> list[TypeEnum]:
        if not isinstance(node, ExprNode):
            raise Exception("parse_node_expression: Implementation error")

        expr_type = self.parse_expression(node.variable, env_v, env_a, env_g, None)
        if expr_type is not TypeEnum.NODE:
            raise TypeError(f"Expression should be a node type, but was {expr_type}")

        list_expr_type = [expr_type]
        setattr(node, "type", list_expr_type)
        return list_expr_type

    def parse_edge_expression(self,
                              node: ASTNode,
                              env_v: TypeEnv,
                              env_g: TypeEnv,
                              curr_graph: str | None
                              ) -> TypeEnum:
        if not isinstance(node, EdgeDecl):
            raise Exception("parse_expression: Implementation error")

        kind: TypeEnum = TypeEnum.UNKNOWN

        if len(node.weight) == 0 :
            if curr_graph is None:
                raise TypeError("Edge expression cannot be made outside graph")

            graph_type = env_g.lookup(curr_graph)
            if graph_type is TypeEnum.UNKNOWN:
                raise TypeError("Graph identifier has no binding")

            graph_type, graph_weight_type = graph_type
            if node.direction == "---":
                if (
                    graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }
                    and graph_weight_type not in self.arit_types
                ):
                    raise TypeError("--- declaration cannot be made inside an undirected graph")
            else:
                if (
                    graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }
                    and graph_weight_type not in self.arit_types
                ):
                    raise TypeError(f"{node.direction} declaration cannot be made inside an directed graph")

            initial_node_ident = node.initial_node
            init_node_type = env_v.lookup(initial_node_ident)
            if init_node_type is not TypeEnum.NODE:
                raise TypeError(f"Type should be NODE but was {init_node_type}")

            for ident2 in node.nodes:
                if env_v.lookup(ident2) is not TypeEnum.NODE:
                    raise TypeError("Edge expression is made with nodes")

            kind = TypeEnum.EDGE
        else:
            if curr_graph is None:
                raise TypeError("Edge expression cannot be made outside graph")

            graph_type = env_g.lookup(curr_graph)
            if graph_type is TypeEnum.UNKNOWN:
                raise TypeError("Graph identifier has no binding")

            graph_type, graph_weight_type = graph_type
            if node.direction == "---":
                if (
                    graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }
                    and graph_weight_type not in self.arit_types
                ):
                    raise TypeError("--- declaration cannot be made inside an undirected graph")
            else:
                if (
                    graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }
                    and graph_weight_type not in self.arit_types
                ):
                    raise TypeError(f"{node.direction} declaration cannot be made inside an directed graph")

            initial_node_ident = node.initial_node
            init_node_type = env_v.lookup(initial_node_ident)
            if init_node_type is not TypeEnum.NODE:
                raise TypeError(f"Type should be NODE but was {init_node_type}")

            if len(node.nodes) != len(node.weight):
                raise TypeError("There must be as many identifier as weights")

            for ident2, expr in zip(node.nodes, node.weight):
                if env_v.lookup(ident2) is not TypeEnum.NODE:
                    raise TypeError("Edge expression is made with nodes")

                expr_type = self.parse_expression(expr, env_v, TypeEnv(), env_g, curr_graph)
                if expr_type is not graph_weight_type:
                    raise TypeError("Weight types must match the graph weight type")

            kind = TypeEnum.EDGE

        setattr(node, "type", kind)
        return kind

    def parse_statement(self,
                        node: ASTNode,
                        env_v: TypeEnv,
                        env_a: TypeEnv,
                        env_g: TypeEnv,
                        curr_algo: str | None,
                        curr_graph: str | None
                        ) -> tuple[TypeEnv, TypeEnv, TypeEnv]:
        match node:
            # case S NL S # doesnt exist and is just a list on the node noew

            case DeclarationInitialization():
                env_v, decl_type = self.parse_declaration(node, env_v)
                if len(node.expression) == 1:
                    expr_type = self.parse_expression(node.expression[0], env_v, env_a, env_g, curr_graph)
                    if expr_type != decl_type:
                        raise TypeError("expression type must match the declaration type")
                else:
                    for expr in node.expression:
                        expr_type = self.parse_expression(expr, env_v, env_a, env_g, curr_graph)
                        if expr_type != decl_type:
                            raise TypeError("expression type must match the declaration type")

            case Assignment():
                if node.variable is None:
                    raise TypeError("Assignment variable cannot be none")
                var_type = env_v.lookup(node.variable)
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, curr_graph)
                if var_type != expr_type:
                    raise TypeError(f"Cannot assign expression of type {expr_type} to variable of type {var_type}")

            case Declaration():
                env_v, _ = self.parse_declaration(node, env_v)

            case IfStatement():
                if_kind = self.parse_expression(node.if_part, env_v, env_a, env_g, curr_graph)
                if if_kind != TypeEnum.BOOL:
                    raise TypeError(f"If part should be bool but was {if_kind}")

                self.parse_statement(node.then_part[0], env_v, env_a, env_g, curr_algo, curr_graph)

                if len(node.else_part) != 0:
                    self.parse_statement(node.else_part[0], env_v, env_a, env_g, curr_algo, curr_graph)

            case WhileStatement():
                cond_kind = self.parse_expression(node.condition[0], env_v, env_a, env_g, curr_graph)
                if cond_kind != TypeEnum.BOOL:
                    raise TypeError(f"Condition part should be bool but was {cond_kind}")

                self.parse_statement(node.statements[0], env_v, env_a, env_g, curr_algo, curr_graph)

            case RepeatStatement():
                repeat_expression = self.parse_expression(node.repeat_expression, env_v, env_a, env_g, curr_graph)
                if repeat_expression != TypeEnum.NAT:
                    raise TypeError(f"Repeat expression should be NAT but was {repeat_expression}")

                self.parse_statement(node.repeat_statements[0], env_v, env_a, env_g, curr_algo, curr_graph)

            case ForEachNormal():
                iterable = self.parse_expression(node.iterable[0], env_v, env_a, env_g, curr_graph)
                if (
                    iterable is not TypeEnum.TEXT
                    and len(set(iterable)) > 1
                ):
                    raise TypeError("Expression has to return an iterable type")

                env_v.enter_scope()
                env_v.bind(node.loop_variable, iterable)

                self.parse_statement(node.statements[0], env_v, env_a, env_g, curr_algo, curr_graph)
                env_v.exit_scope()

            case ForEachEdge():
                edge_type = self.parse_expression(node.edge[0], env)
                if edge_type is not TypeEnum.EDGE:
                    raise TypeError(f"Edge part should be EDGE but was {edge_type}")

                graph_type, graph_weight_type = env_g.lookup(env.graph_identifier)
                if graph_type not in self.graph_types:
                    raise TypeError(f"Graph type is not a graph type but {graph_type}")
                if graph_weight_type not in self.arit_types:
                    # could also be none / unknown since they dont need weight
                    raise TypeError(f"Graph weight type was not an arithmetic type but {graph_weight_type}")

                if node.weight_identifier is None:
                    for statement in node.statements:
                        self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph)
                else:
                    env_v.bind(node.weight_identifier, graph_weight_type)
                    for statement in node.statements:
                        self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph)

            case ReturnStatement():
                if curr_algo is None:
                    raise TypeError("Return cannot be used outside function")

                _, expected_return_type = env_a.lookup(curr_algo)
                return_type = self.parse_expression(node.expression, env_v, env_a, env_g, curr_graph)

                if expected_return_type != return_type:
                    raise TypeError("Return type does not match function")

            case Algorithm():
                env_a = self.parse_algorithm(node, env_a)

            case Expression():
                self.parse_expression(node, env_v, env_a, env_g, curr_graph)

            case LoopModifier():
                self.parse_loop_modifier(node)

            case GraphDecl():
                env_g = self.parse_graph_declaration(node, env_g)

            case DisplayStatement():
                display_expr = self.parse_expression(node.expression[0], env_v, env_a, env_g, curr_graph)
                if display_expr is TypeEnum.UNKNOWN:
                    raise TypeError("Cannot display unknown type")

            case _:
                raise TypeError(f"Unknown statement type: {node.__class__.__name__}")

        return env_v, env_a, env_g

    def parse_loop_modifier(self, node: ASTNode) -> bool:
        well_formed = isinstance(node, LoopModifier) and node.modifier == "stop"
        return well_formed

    def parse_type(self, node: ASTNode) -> bool: # prob need to use martin type
        well_formed = False
        match node.token:
            case "bool" | "text" | "node" | "edge":
                well_formed = True
            case "TYPE_ARITH":
                well_formed = self.parse_type_arithmetic(node.children[0])
            case "TYPE_GRAPH":
                well_formed = self.parse_graph_type(node.children[0])

        return well_formed

    def parse_type_arithmetic(self, node: ASTNode) -> bool: # prob need to use martin type
        return node.token in self.arit_types

    def parse_graph_type(self, node: ASTNode) -> bool: # prob need to use martin type
        return node.token in self.graph_types

    def parse_algorithm(self, node: ASTNode, env_a: TypeEnv) -> TypeEnv:
        if not isinstance(node, Algorithm):
            raise Exception("parse_algorithm: Implementation error")

        env_v = TypeEnv()

        parameter_types = []
        for param in node.parameters:
            env_v, decl_type = self.parse_declaration(param, env_v)
            parameter_types.append(decl_type)

        self.parse_statement(node.statements[0], env_v, env_a, TypeEnv(), node.variable, None)

        if node.return_type is None:
            env_a.bind(node.variable, (tuple(parameter_types), None))
        else:
            if not self.parse_type(node): # unsure how to check this here because of structure
                raise TypeError("Invalid return type")

            env_a.bind(node.variable, (tuple(parameter_types), node.return_type))

        return env_a

    def parse_declaration(self, node: ASTNode, env_v: TypeEnv) -> tuple[TypeEnv, TypeEnum]:
        if not isinstance(node, Declaration):
            raise Exception("parse_declaration: Implementation error")

        decl_type = TypeEnum.UNKNOWN

        if node.is_list is False:
            if self.parse_type_arithmetic(node): # I in T
                decl_type = node.type
                for ident in node.variables:
                    env_v.bind(ident, decl_type)
            elif self.parse_type(node): # T I

                decl_type = node.type
                for ident in node.variables:
                    env_v.bind(ident, decl_type)
            else:
                raise TypeError("Unknown decl type")
        else:
            env_v, decl_type = self.parse_declaration_list(node, env_v)

        return (env_v, decl_type)

    def parse_declaration_list(self, node: ASTNode, env_v: TypeEnv) -> tuple[TypeEnv, TypeEnum]:
        if not isinstance(node, Declaration) or node.is_list is False:
            raise Exception("parse_declaration_list: IMplementation error")

        if not self.parse_dimensions(node.dimension):
            raise TypeError("Dimension err")

        list_type = node.type
        if not self.parse_type(list_type):
            raise TypeError("Decleration list type err")

        for identifier in node.variables:
            env_v.bind(identifier, list_type)

        return (env_v, list_type)

    def parse_dimensions(self, node: ASTNode) -> bool: # not sure about structure here
        well_formed = False
        if node.token == "Nd":
            kind = self.parse_expression(node, TypeEnv(), TypeEnv(), TypeEnv(), None)
            if kind != TypeEnum.NAT:
                return False

            well_formed = True
        else: # DIM can be empty
            well_formed = True

        return well_formed

    def parse_graph_declaration(self, node: ASTNode, env_g: TypeEnv) -> TypeEnv:
        if not isinstance(node, GraphDecl):
            raise Exception("parse_graph_decleeration: Implementation error")

        if node.weight_type is None:
            if not node.nodes and not node.edges:
                graph_type = node.graph_type
                if not self.parse_graph_type(graph_type):
                    raise TypeError("Graph type err")

                graph_ident = node.variable
                env_g.bind(graph_ident, (node.weight_type, None))
            else:
                graph_type = node.graph_type
                if not self.parse_graph_type(graph_type):
                    raise TypeError("Graph type err")

                graph_weight_type = node.weight_type
                if not self.parse_graph_type(graph_weight_type):
                    raise TypeError("Graph weight type err")

                graph_ident = node.variable
                env_g.bind(graph_ident, (graph_type, graph_weight_type))
        else: # graph decleration with Initialization
            if not node.nodes and not node.edges:
                graph_type = node.graph_type
                if not self.parse_graph_type(graph_type):
                    raise TypeError("Graph type err")

                graph_ident = node.variable
                self.parse_statement([*node.nodes, *node.edges], TypeEnv(), TypeEnv(), env_g, None, graph_ident)
                env_g.bind(graph_ident, (node.weight_type, None))
            else:
                graph_type = node.graph_type
                if not self.parse_graph_type(graph_type):
                    raise TypeError("Graph type err")

                graph_weight_type = node.weight_type
                if not self.parse_graph_type(graph_weight_type):
                    raise TypeError("Graph weight type err")

                graph_ident = node.variable
                self.parse_statement([*node.nodes, *node.edges], TypeEnv(), TypeEnv(), env_g, None, graph_ident)
                env_g.bind(graph_ident, (node.weight_type, graph_weight_type))

        return env_g

if __name__ == "__main__":
    # program = ASTNode("")
    program = build_ast()

    checker = TypeChecker(program)
    print(f"well formed: {checker.check()}")
    print_ast(program)
