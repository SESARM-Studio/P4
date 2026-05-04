from type_env import TypeEnv, TypeEnum
from remove_l8ter import *

class TypeCheckError(Exception):

    """
    Custom exception to make debugging of the type system easier

    Prints the function from which the type error occured
    """

    def __init__(self, type_rule, expected=None, actual=None):
        self.type_rule = type_rule
        self.expected = expected
        self.actual = actual

    def __str__(self):
        type_rule_function_name = self.type_rule.__name__ # maybe use the id from the inference rules
        return f"[{type_rule_function_name}] expected: {self.expected}, got: {self.actual}"

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
    arit_types: set[TypeEnum] = { TypeEnum.NAT, TypeEnum.INT, TypeEnum.REAL }

    def __init__(self, ast: ASTNode) -> None:
        self.ast = ast

    def check(self) -> bool:
        """Annotates the AST and return true if program is well formed"""
        well_formed = self.parse_program(self.ast)

        return well_formed

    def parse_program(self, node: ASTNode) -> bool:
        well_formed = False
        if node != None: # program can only be statement or none
            if str(node.token).upper() != "PROGRAM":
                raise Exception("parse_program: Implementation error")

            try: # create the initial environments and parse the program
                env_v = TypeEnv()
                env_a = TypeEnv()
                env_g = TypeEnv()

                for statement in node.children: # this might also catch no statements depending if None or []
                    self.parse_statement(statement, env_v, env_a, env_g, None, None)

                well_formed = True

            except TypeCheckError as e:
                print(f"TypeCheckError: {e}")

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
                            raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                        kind = ident_type

                    case _:
                        raise Exception("Unknown term type")

            case GraphStatement():
                graph_expr_type = self.parse_graph_statement(node, env_v, env_g)

                if graph_expr_type not in self.graph_types:
                    raise TypeCheckError(self.parse_expression, self.graph_types, graph_expr_type)

                kind = graph_expr_type

            case ExprNode():
                node_expr_type = self.parse_node_expression(node, env_v, env_a, env_g)

                if (
                    isinstance(node_expr_type, list)
                    and node_expr_type
                    and not all(typ == TypeEnum.NODE for typ in node_expr_type)
                ):
                    raise TypeCheckError(self.parse_expression, f"list of {TypeEnum.NODE}", node_expr_type)

                kind = node_expr_type # special type (list[TypeEnum])

            case EdgeDecl():
                edge_decl_type = self.parse_edge_expression(node, env_v, env_g, curr_graph)

                if edge_decl_type is not TypeEnum.EDGE:
                    raise TypeCheckError(self.parse_expression, TypeEnum.EDGE, edge_decl_type)

                kind = edge_decl_type

            case AbsoluteValue():
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, curr_graph)

                if expr_type not in self.arit_types:
                    raise TypeCheckError(self.parse_expression, self.arit_types, expr_type)

                kind = TypeEnum.NAT

            case Magnitude():
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, curr_graph)

                if (
                    expr_type is not TypeEnum.TEXT
                    and not isinstance(expr_type, list) and len(set(expr_type)) > 1
                ):
                    raise TypeCheckError(self.parse_expression, f"{TypeEnum.TEXT} or list", expr_type)

                kind = TypeEnum.NAT

            case AlgorithmCall():
                algo_type = env_a.lookup(node.variable)

                arguments_types_index = 0
                return_type_index = 1

                for idx, expr in enumerate(node.arguments):
                    expr_type = self.parse_expression(expr, env_v, env_a, env_g, curr_graph)

                    # algo_type = tuple[tuple[arg_type], return_type]
                    if algo_type[arguments_types_index][idx] != expr_type:
                        raise TypeCheckError(self.parse_expression, algo_type[arguments_types_index], expr_type)

                kind = algo_type[return_type_index]

            case ArrayAccess():
                for index in node.indexes:
                    expr_type = self.parse_expression(index, env_v, env_a, env_g, curr_graph)

                    if expr_type is not TypeEnum.NAT:
                        raise TypeCheckError(self.parse_expression, TypeEnum.NAT, expr_type)

                ident = node.variable
                array_type = env_v.lookup(ident)

                if array_type is not TypeEnum.UNKNOWN:
                    raise TypeCheckError(self.parse_expression, "not UNKNOWN", array_type)

                kind = array_type

            case ExprChaining():
                ident = node.variable

                graph_type, graph_weight_type = env_g.lookup(ident)
                ident_type = env_v.lookup(ident)

                if not (
                    graph_type not in self.graph_types
                    and graph_weight_type not in self.arit_types
                    or ident_type not in { TypeEnum.NODE, TypeEnum.EDGE }
                ):
                    raise TypeCheckError(self.parse_expression, f"chainable type", "non-chainable type")

                expr_type = self.parse_expression(node.chain_part, env_v, env_a, env_g, curr_graph)

                if expr_type is not TypeEnum.UNKNOWN:
                    raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                kind = expr_type

            # case "ListExpression": #how this? i think we are missing this rule
            #     list_types = []
            #     for child in node.children:
            #         list_types.append(self.parse_expression(child, env))

            #     if len(set(list_types)) > 1:
            #         raise TypeCheckError("Mixing of types in list not allowed")

            #     kind = list_types[0] if len(list_types) > 0 else TypeEnum.UNKNOWN

            case Expression():
                match node.operator:
                    case "+" | "-" | "*" | "/" | "%" | "^":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, curr_graph)

                        if expr1_type is TypeEnum.UNKNOWN:
                            raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, curr_graph)

                        if expr2_type is TypeEnum.UNKNOWN:
                            raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                        if expr1_type != expr2_type:
                            raise TypeCheckError("Type mismatch") # later they might not need to match

                        kind = expr1_type

                    case EdgeDecl(): # this correct? (wot) or (woe)
                        ident = node.initial_node

                        graph_type, graph_weight_type = env_g.lookup(ident)

                        if node.direction == "-->":
                            if graph_type not in { TypeEnum.DIGRAPH, TypeEnum.TREE }:
                                raise TypeCheckError(self.parse_expression,
                                                     f"{TypeEnum.DIGRAPH} or {TypeEnum.TEXT}",
                                                     graph_type)
                        else: # ---
                            if graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }:
                                raise TypeCheckError(self.parse_expression,
                                                     f"{TypeEnum.GRAPH} or {TypeEnum.TEXT}",
                                                     graph_type)

                        if graph_weight_type not in self.arit_types:
                            raise TypeCheckError(self.parse_expression, self.arit_types, graph_weight_type)

                        ident2 = node.nodes[0]
                        ident2_type = env_v.lookup(ident2)

                        if var_type is not TypeEnum.NODE:
                            raise TypeCheckError(self.parse_expression, TypeEnum.NODE, ident2_type)

                        ident3 = node.nodes[0]
                        ident3_type = env_v.lookup(ident3)

                        if ident3_type is not TypeEnum.NODE:
                            raise TypeCheckError(self.parse_expression, TypeEnum.NODE, ident3_type)

                        kind = graph_weight_type

                    case "=" | "!=" | "<" | "<=" | ">" | ">=":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, curr_graph)

                        if expr1_type is TypeEnum.UNKNOWN:
                            raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, curr_graph)

                        if expr2_type is TypeEnum.UNKNOWN:
                            raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                        if expr1_type != expr2_type:
                            raise TypeCheckError("Type mismatch") # later they might not need to match

                        kind = TypeEnum.BOOL

                    case "neg":
                        expr_type = self.parse_expression(node.arg1, env_v, env_a, env_g, curr_graph)

                        if expr_type is not TypeEnum.BOOL:
                            raise TypeCheckError(self.parse_expression, TypeEnum.BOOL, expr_type)

                        kind = expr_type

                    case "and" | "or":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, curr_graph)

                        if expr1_type is not TypeEnum.BOOL:
                            raise TypeCheckError(self.parse_expression, TypeEnum.BOOL, expr_type)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, curr_graph)

                        if expr2_type is not TypeEnum.BOOL:
                            raise TypeCheckError(self.parse_expression, TypeEnum.BOOL, expr_type)

                        if expr1_type != expr2_type:
                            raise TypeCheckError("Type mismatch") # later they might not need to match

                        kind = expr1_type

                    case _:
                        raise Exception("Unknown expression type")

            case _:
                raise Exception("Unknown expression or term type")

        setattr(node, "type", kind)
        return kind

    def parse_graph_statement(self, node: ASTNode, env_v: TypeEnv, env_g: TypeEnv) -> TypeEnum:
        if not isinstance(node, GraphStatement):
            raise Exception("parse_graph_expression: Implementation error")

        kind: TypeEnum = TypeEnum.UNKNOWN

        # same rule if it is add or remove mb also change in report
        if "identifier": # how check this?
            graph_type, graph_weight_type = env_g.lookup(node.graph_variable)

            if graph_type not in self.graph_types:
                raise TypeCheckError(self.parse_graph_statement, self.graph_types, graph_type)

            if graph_weight_type not in self.arit_types:
                raise TypeCheckError(self.parse_graph_statement, self.arit_types, graph_weight_type)

            ident = node.argument[0] # I_2
            ident_type = env_v.lookup(ident)

            if ident_type is not TypeEnum.NODE:
                raise TypeCheckError(self.parse_graph_statement, TypeEnum.NODE, ident_type)

            kind = graph_type
        else: # edge expr
            graph_type, graph_weight_type = env_g.lookup(node.graph_variable)

            if graph_type not in self.graph_types:
                raise TypeCheckError(self.parse_graph_statement, self.graph_types, graph_type)

            if graph_weight_type not in self.arit_types:
                raise TypeCheckError(self.parse_graph_statement, self.arit_types, graph_weight_type)

            edge_expr = node.argument[0]
            expr_type = self.parse_edge_expression(edge_expr, env_v, env_g, None)

            if expr_type is not TypeEnum.EDGE:
                raise TypeCheckError(self.parse_graph_statement, TypeEnum.EDGE, expr_type)

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
            raise TypeCheckError(self.parse_node_expression, TypeEnum.NODE, expr_type)

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


        if curr_graph is None:
            raise TypeCheckError(self.parse_edge_expression, "inside graph", "outside graph")

        kind: TypeEnum = TypeEnum.UNKNOWN

        if len(node.weight) == 0 :
            graph_type = env_g.lookup(curr_graph)

            if graph_type is TypeEnum.UNKNOWN:
                raise TypeCheckError(self.parse_edge_expression, "not UNKNOWN", "UNKNOWN")

            graph_type, graph_weight_type = graph_type
            if node.direction == "---":
                if (
                    graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }
                    and graph_weight_type not in self.arit_types
                ):
                    raise TypeCheckError(self.parse_edge_expression, "undirected graph type", "directed graph type")
            else:
                if (
                    graph_type not in { TypeEnum.DIGRAPH, TypeEnum.TREE }
                    and graph_weight_type not in self.arit_types
                ):
                    raise TypeCheckError(self.parse_edge_expression, "directed graph type", "undirected graph type")

            initial_node_ident = node.initial_node
            init_node_type = env_v.lookup(initial_node_ident)

            if init_node_type is not TypeEnum.NODE:
                raise TypeCheckError(self.parse_edge_expression, TypeEnum.NODE, init_node_type)

            for ident2 in node.nodes:
                ident2_type = env_v.lookup(ident2)

                if ident2_type is not TypeEnum.NODE:
                    raise TypeCheckError(self.parse_edge_expression, TypeEnum.NODE, ident2_type)

            kind = TypeEnum.EDGE
        else:
            graph_type = env_g.lookup(curr_graph)

            if graph_type is TypeEnum.UNKNOWN:
                raise TypeCheckError(self.parse_edge_expression, "not UNKNOWN", "UNKNOWN")

            graph_type, graph_weight_type = graph_type
            if node.direction == "---":
                if (
                    graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }
                    and graph_weight_type not in self.arit_types
                ):
                    raise TypeCheckError(self.parse_edge_expression, "undirected graph type", "directed graph type")
            else:
                if (
                    graph_type not in { TypeEnum.DIGRAPH, TypeEnum.TREE }
                    and graph_weight_type not in self.arit_types
                ):
                    raise TypeCheckError(self.parse_edge_expression, "directed graph type", "undirected graph type")

            initial_node_ident = node.initial_node
            init_node_type = env_v.lookup(initial_node_ident)

            if init_node_type is not TypeEnum.NODE:
                raise TypeCheckError(self.parse_edge_expression, TypeEnum.NODE, init_node_type)

            if len(node.nodes) != len(node.weight):
                raise TypeCheckError(self.parse_edge_expression, "a weight for each node", "not that")

            for ident2, expr in zip(node.nodes, node.weight):
                ident2_type = env_v.lookup(ident2)

                if ident2_type is not TypeEnum.NODE:
                    raise TypeCheckError(self.parse_edge_expression, TypeEnum.NODE, ident2_type)

                expr_type = self.parse_expression(expr, env_v, TypeEnv(), env_g, curr_graph)
                if expr_type is not graph_weight_type:
                    raise TypeCheckError(self.parse_edge_expression, graph_weight_type, expr_type)

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

            case DeclarationInit():
                env_v, decl_type = self.parse_declaration(node, env_v)

                if len(node.expression) == 1:
                    expr_type = self.parse_expression(node.expression[0], env_v, env_a, env_g, curr_graph)

                    if expr_type != decl_type:
                        raise TypeCheckError(self.parse_statement, decl_type, expr_type)
                else:
                    for expr in node.expression:
                        expr_type = self.parse_expression(expr, env_v, env_a, env_g, curr_graph)

                        if expr_type != decl_type:
                            raise TypeCheckError(self.parse_statement, decl_type, expr_type)

            case Assignment():
                ident_type = env_v.lookup(node.variable)
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, curr_graph)

                if ident_type != expr_type:
                    raise TypeCheckError(self.parse_statement, ident_type, expr_type)

            case Declaration():
                env_v, _ = self.parse_declaration(node, env_v)

            case IfStatement():
                if_kind = self.parse_expression(node.if_part, env_v, env_a, env_g, curr_graph)

                if if_kind != TypeEnum.BOOL:
                    raise TypeCheckError(self.parse_statement, TypeEnum.BOOL, if_kind)

                env_v.enter_scope()
                env_a.enter_scope() # objects are passed by reference so i use scope to avoid the updated env
                env_g.enter_scope()
                self.parse_statement(node.then_part[0], env_v, env_a, env_g, curr_algo, curr_graph)
                env_v.exit_scope()
                env_a.exit_scope()
                env_g.exit_scope()

                if len(node.else_part) != 0:
                    env_v.enter_scope()
                    env_a.enter_scope()
                    env_g.enter_scope()
                    self.parse_statement(node.else_part[0], env_v, env_a, env_g, curr_algo, curr_graph)
                    env_v.exit_scope()
                    env_a.exit_scope()
                    env_g.exit_scope()

            case WhileStatement():
                cond_kind = self.parse_expression(node.condition[0], env_v, env_a, env_g, curr_graph)

                if cond_kind != TypeEnum.BOOL:
                    raise TypeCheckError(self.parse_statement, TypeEnum.BOOL, cond_kind)

                env_v.enter_scope()
                env_a.enter_scope()
                env_g.enter_scope()
                self.parse_statement(node.statements[0], env_v, env_a, env_g, curr_algo, curr_graph)
                env_v.exit_scope()
                env_a.exit_scope()
                env_g.exit_scope()

            case RepeatStatement():
                repeat_expression = self.parse_expression(node.repeat_expression, env_v, env_a, env_g, curr_graph)

                if repeat_expression != TypeEnum.NAT:
                    raise TypeCheckError(self.parse_statement, TypeEnum.NAT, repeat_expression)

                env_v.enter_scope()
                env_a.enter_scope()
                env_g.enter_scope()
                self.parse_statement(node.repeat_statements[0], env_v, env_a, env_g, curr_algo, curr_graph)
                env_v.exit_scope()
                env_a.exit_scope()
                env_g.exit_scope()

            case ForEachNormal():
                iterable = self.parse_expression(node.iterable[0], env_v, env_a, env_g, curr_graph)

                if (
                    iterable is not TypeEnum.TEXT
                    and len(set(iterable)) > 1
                ):
                    raise TypeCheckError(self.parse_statement, "iterable type", iterable)

                env_v.enter_scope()
                env_v.bind(node.loop_variable, iterable)
                self.parse_statement(node.statements[0], env_v, env_a, env_g, curr_algo, curr_graph)
                env_v.exit_scope()

            case ForEachEdge():
                edge_type = self.parse_expression(node.edge[0], env)

                if edge_type is not TypeEnum.EDGE:
                    raise TypeCheckError(self.parse_statement, TypeEnum.EDGE, edge_type)

                graph_type, graph_weight_type = env_g.lookup(env.graph_identifier)

                if graph_type not in self.graph_types:
                    raise TypeCheckError(self.parse_statement, self.graph_types, graph_type)

                if graph_weight_type not in self.arit_types:
                    # could also be none / unknown since they dont need weight
                    raise TypeCheckError(self.parse_statement, self.arit_types, graph_weight_type)

                env_v.enter_scope()
                env_a.enter_scope()
                env_g.enter_scope()
                if node.weight_identifier is None:
                    for statement in node.statements:
                        self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph)
                else:
                    env_v.bind(node.weight_identifier, graph_weight_type)
                    for statement in node.statements:
                        self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph)
                env_v.exit_scope()
                env_a.exit_scope()
                env_g.exit_scope()

            case ReturnStatement():
                if curr_algo is None:
                    raise TypeCheckError(self.parse_statement, "inside function", "outside function")

                _, expected_return_type = env_a.lookup(curr_algo)
                return_type = self.parse_expression(node.expression, env_v, env_a, env_g, curr_graph)

                if expected_return_type != return_type:
                    raise TypeCheckError(self.parse_statement, expected_return_type, return_type)

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
                    raise TypeCheckError(self.parse_statement, "not UNKNOWN", "UNKNOWN")

            case _:
                raise Exception(f"Unknown statement type")

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
                well_formed = self.parse_type_arithmetic(node)

            case "TYPE_GRAPH":
                well_formed = self.parse_graph_type(node)

        return well_formed

    def parse_type_arithmetic(self, node: ASTNode) -> bool:
        return node.token.upper() in { "NAT", "INT", "REAL"} # throw error instead?

    def parse_graph_type(self, node: ASTNode) -> bool:
        return node.token.upper in { "GRAPH", "DIGRAPH", "TREE" }

    def parse_algorithm(self, node: ASTNode, env_a: TypeEnv) -> TypeEnv:
        if not isinstance(node, Algorithm):
            raise Exception("parse_algorithm: Implementation error")

        env_v = TypeEnv()
        env_g = TypeEnv()
        parameter_types = []

        for param in node.parameters:
            env_v, decl_type = self.parse_declaration(param, env_v)
            parameter_types.append(decl_type)

        env_a.enter_scope()
        self.parse_statement(node.statements[0], env_v, env_a, env_g, node.variable, None)
        env_a.exit_scope()

        if node.return_type is None:
            env_a.bind(node.variable, (tuple(parameter_types), None))
        else:
            if not self.parse_type(node): # unsure how to check this here because of structure
                raise TypeCheckError(self.parse_statement, "valid return type", "Invalid return type")

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
                raise Exception("Unknown decl type")
        else:
            env_v, decl_type = self.parse_declaration_list(node, env_v)

        return (env_v, decl_type)

    def parse_declaration_list(self, node: ASTNode, env_v: TypeEnv) -> tuple[TypeEnv, TypeEnum]:
        if not isinstance(node, Declaration) or node.is_list is False:
            raise Exception("parse_declaration_list: IMplementation error")

        if not self.parse_dimensions(node.dimension):
            raise TypeCheckError(self.parse_declaration_list, "valid dimension", "dimension err")

        if not self.parse_type(node.type):
            raise TypeCheckError(self.parse_declaration_list, "valid type", "invalid type")

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
            raise Exception("parse_graph_declaration: Implementation error")

        if node.weight_type is None:
            if not node.nodes and not node.edges:
                graph_type = node.graph_type

                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                graph_ident = node.variable
                env_g.bind(graph_ident, (node.weight_type, None))
            else:
                graph_type = node.graph_type

                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                graph_weight_type = node.weight_type
                if not self.parse_graph_type(graph_weight_type):
                    raise TypeCheckError(self.parse_graph_declaration, self.arit_types, graph_weight_type)

                graph_ident = node.variable
                env_g.bind(graph_ident, (graph_type, graph_weight_type))
        else: # graph decleration with Initialization
            if not node.nodes and not node.edges:
                graph_type = node.graph_type

                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                graph_ident = node.variable
                self.parse_statement([*node.nodes, *node.edges], TypeEnv(), TypeEnv(), env_g, None, graph_ident)
                env_g.bind(graph_ident, (node.weight_type, None))
            else:
                graph_type = node.graph_type

                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                graph_weight_type = node.weight_type

                if not self.parse_graph_type(graph_weight_type):
                    raise TypeCheckError(self.parse_graph_declaration, self.arit_types, graph_weight_type)

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
