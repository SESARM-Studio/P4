from typesystem.type_env import TypeEnv
from typesystem.data_types import TypeEnum, resolve_type
from parser.ast_builder import *
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
        return f"in [{type_rule_function_name}] expected: {self.expected}, got: {self.actual}"

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
        if str(node.token).upper() != "PROGRAM":
            raise Exception("parse_program: Implementation error")

        if len(node.children) > 1:
            try: # create the initial environments and parse the program
                env_v = TypeEnv()
                env_a = TypeEnv()
                env_g = TypeEnv()

                for statement in node.children[:-1]: # does not really follow rule, but (com) doesn't exist
                    self.parse_statement(statement, env_v, env_a, env_g, None, None, False)

                well_formed = True

            except TypeCheckError as e:
                print(f"TypeCheckError: {e}")

        else: # empty programs are also valid
            end_of_file = node.children[-1]
            if end_of_file.token == "EOF":
                well_formed = True

        return well_formed

    def parse_expression(self,
                         node: ASTNode,
                         env_v: TypeEnv,
                         env_a: TypeEnv,
                         env_g: TypeEnv,
                         ) -> TypeEnum:
        kind: TypeEnum = TypeEnum.UNKNOWN

        match node:
            case Term():
                match node.type:
                    case "INTEGER_NUMBER" | TypeEnum.INT:
                        kind = TypeEnum.INT

                    case "NATURAL_NUMBER" | TypeEnum.NAT:
                        kind = TypeEnum.NAT

                    case "REAL_NUMBER" | TypeEnum.REAL:
                        kind = TypeEnum.REAL

                    case "TEXT" | TypeEnum.TEXT:
                        kind = TypeEnum.TEXT

                    case "BOOL_VALUE" | TypeEnum.BOOL:
                        kind = TypeEnum.BOOL

                    case "IDENTIFIER":
                        ident = node.value
                        ident_type = env_v.lookup(ident)

                        if ident_type is TypeEnum.UNKNOWN:
                            raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                        kind = ident_type

                    case _:
                        raise Exception("Unknown term type")

            case ExprNode():
                node_expr_type = self.parse_node_expression(node, env_v, env_a, env_g)

                if (
                    isinstance(node_expr_type, list)
                    and not all(typ == TypeEnum.NODE for typ in node_expr_type)
                ):
                    raise TypeCheckError(self.parse_expression, f"list of {TypeEnum.NODE}", node_expr_type)

                kind = node_expr_type # special type (list[TypeEnum])

            case AbsoluteValue():
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)

                if expr_type not in self.arit_types:
                    raise TypeCheckError(self.parse_expression, self.arit_types, expr_type)

                kind = TypeEnum.NAT

            case Magnitude():
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)

                if (
                    expr_type is not TypeEnum.TEXT
                    and not isinstance(expr_type, list) and len(set(expr_type)) > 1
                ):
                    raise TypeCheckError(self.parse_expression, f"{TypeEnum.TEXT} or list", expr_type)

                kind = TypeEnum.NAT

            case AlgorithmCall():
                algo_type = env_a.lookup(node.identifier)

                if algo_type is None:
                    raise TypeCheckError(self.parse_expression, "bound algorithm", "unknown algorithm")

                parameter_types_index = 0
                return_type_index = 1
                arguments = node.arguments if node.arguments is not None else []

                if len(algo_type[parameter_types_index]) != len(arguments):
                    raise TypeCheckError(self.parse_expression, "same number of parameters and arguments", "not that")

                for param_type, arg in zip(algo_type[parameter_types_index], arguments):
                    arg_type = self.parse_expression(arg, env_v, env_a, env_g)

                    # algo_type = tuple[tuple[arg_type], return_type]
                    if arg_type != param_type:
                        raise TypeCheckError(self.parse_expression, param_type, arg_type)

                kind = algo_type[return_type_index]

            case ArrayAccess():
                for index in node.indexes:
                    expr_type = self.parse_expression(index, env_v, env_a, env_g)

                    if expr_type is not TypeEnum.NAT:
                        raise TypeCheckError(self.parse_expression, TypeEnum.NAT, expr_type)

                array_type = env_v.lookup(node.identifier)

                if array_type is TypeEnum.UNKNOWN:
                    raise TypeCheckError(self.parse_expression, "not UNKNOWN", array_type)

                kind = array_type

            case IdentifierAccess():
                # i find a bit difficult to follow the rules bcuz of structure
                # help appreciated
                for identifier in node.identifiers:
                    if isinstance(identifier, str):
                        if env_v.lookup(identifier) is not TypeEnum.NODE: # (dt1)
                            graph_type, graph_weight_type = env_g.lookup(identifier)

                            if graph_type not in self.graph_types:
                                raise TypeCheckError(self.parse_expression, self.graph_types, graph_type)

                            if graph_weight_type not in self.arit_types and graph_weight_type is not None: # weight type can be none
                                raise TypeCheckError(self.parse_expression, self.arit_types, graph_weight_type)

                            kind = graph_type
                        else: # (dt2)
                            node_type = env_v.lookup(identifier)

                            if node_type is not TypeEnum.NODE:
                                raise TypeCheckError(self.parse_expression, TypeEnum.NODE, node_type)

                            kind = node_type
                    elif isinstance(identifier, AlgorithmCall) or isinstance(identifier, ArrayAccess):
                        kind = self.parse_expression(identifier, env_v, env_a, env_g)
                    else:
                        raise Exception("grammer error")

            case ListExpression():
                list_types = []
                for child in node.expressions:
                    list_types.append(self.parse_expression(child, env_v, env_a, env_g))

                if len(set(list_types)) > 1:
                    raise TypeCheckError(self.parse_expression, "list of one type", list_types)

                kind = list_types[0] if len(list_types) > 0 else TypeEnum.UNKNOWN

            case Expression():
                match node.operator:
                    case "+" | "-" | "*" | "/":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)

                        if expr1_type is TypeEnum.UNKNOWN:
                            raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)

                        if expr2_type is TypeEnum.UNKNOWN:
                            raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                        kind = self.lub_arit(expr1_type, expr2_type)

                    case "%":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)

                        if expr1_type not in { TypeEnum.NAT, TypeEnum.INT }:
                            raise TypeCheckError(self.parse_expression, "nat or int", expr1_type)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)

                        if expr2_type not in { TypeEnum.NAT, TypeEnum.INT }:
                            raise TypeCheckError(self.parse_expression, "nat or it", expr2_type)

                        kind = self.lub_arit(expr1_type, expr2_type)

                    case "^":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)

                        if expr1_type is TypeEnum.UNKNOWN:
                            raise TypeCheckError(self.parse_expression, "not UNKNOWN", "UNKNOWN")

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)

                        if expr2_type not in { TypeEnum.NAT, TypeEnum.INT }:
                            raise TypeCheckError(self.parse_expression, "nat or it", expr2_type)

                        kind = expr1_type

                    case "weight of":
                        if "-->" in node.arg1: # (wot)
                            ident1n2, ident3 = node.arg1.split("-->")
                            ident1, ident2 = ident1n2.split(".")

                            graph_type, graph_weight_type = env_g.lookup(ident1)

                            if graph_type not in { TypeEnum.DIGRAPH, TypeEnum.TREE }:
                                raise TypeCheckError(self.parse_expression,
                                                     f"{TypeEnum.DIGRAPH} or {TypeEnum.TREE}",
                                                     graph_type)

                            if graph_weight_type not in self.arit_types:
                                raise TypeCheckError(self.parse_expression, self.arit_types, graph_weight_type)

                            # ident2_type = env_v.lookup(ident2)
                            ident2_type = TypeEnum.NODE # need some change to find these node in graph

                            if ident2_type is not TypeEnum.NODE:
                                raise TypeCheckError(self.parse_expression, TypeEnum.NODE, ident2_type)

                            # ident3_type = env_v.lookup(ident3)
                            ident3_type = TypeEnum.NODE # need some change to find these node in graph

                            if ident3_type is not TypeEnum.NODE:
                                raise TypeCheckError(self.parse_expression, TypeEnum.NODE, ident3_type)

                            kind = graph_weight_type
                        else: # (woe)
                            ident1n2, ident3 = node.arg1.split("---")
                            ident1, ident2 = ident1n2.split(".")

                            graph_type, graph_weight_type = env_g.lookup(ident1)

                            if graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }:
                                raise TypeCheckError(self.parse_expression,
                                                     f"{TypeEnum.GRAPH} or {TypeEnum.TREE}",
                                                     graph_type)

                            if graph_weight_type not in self.arit_types:
                                raise TypeCheckError(self.parse_expression, self.arit_types, graph_weight_type)

                            # ident2_type = env_v.lookup(ident2)
                            ident2_type = TypeEnum.NODE # need some change to find these node in graph

                            if ident2_type is not TypeEnum.NODE:
                                raise TypeCheckError(self.parse_expression, TypeEnum.NODE, ident2_type)

                            # ident3_type = env_v.lookup(ident3)
                            ident3_type = TypeEnum.NODE # need some change to find these node in graph

                            if ident3_type is not TypeEnum.NODE:
                                raise TypeCheckError(self.parse_expression, TypeEnum.NODE, ident3_type)

                            kind = graph_weight_type

                    case "=" | "!=" | "<" | "<=" | ">" | ">=":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)

                        if expr1_type not in self.arit_types:
                            raise TypeCheckError(self.parse_expression, self.arit_types, expr1_type)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)

                        if expr2_type not in self.arit_types:
                            raise TypeCheckError(self.parse_expression, self.arit_types, expr2_type)

                        kind = TypeEnum.BOOL

                    case "neg":
                        expr_type = self.parse_expression(node.arg1, env_v, env_a, env_g)

                        if expr_type is not TypeEnum.BOOL:
                            raise TypeCheckError(self.parse_expression, TypeEnum.BOOL, expr_type)

                        kind = expr_type

                    case "and":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)

                        if expr1_type is not TypeEnum.BOOL:
                            raise TypeCheckError(self.parse_expression, TypeEnum.BOOL, expr_type)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)

                        if expr2_type is not TypeEnum.BOOL:
                            raise TypeCheckError(self.parse_expression, TypeEnum.BOOL, expr_type)

                        kind = expr1_type

                    case "or":
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)

                        if expr1_type is not TypeEnum.BOOL:
                            raise TypeCheckError(self.parse_expression, TypeEnum.BOOL, expr_type)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)

                        if expr2_type is not TypeEnum.BOOL:
                            raise TypeCheckError(self.parse_expression, TypeEnum.BOOL, expr_type)

                        kind = expr1_type

                    case None | "":
                        kind = self.parse_expression(node.arg1, env_v, env_a, env_g)

                    case _:
                        raise Exception("Unknown operator")

            case _:
                raise Exception("Unknown expression type")

        setattr(node, "type", kind)
        return kind

    def parse_graph_statement(self, node: ASTNode, env_v: TypeEnv, env_g: TypeEnv) -> bool:
        if not isinstance(node, GraphStatement):
            raise Exception("parse_graph_expression: Implementation error")

        if not isinstance(node.argument, EdgeDecl):
            graph_type, graph_weight_type = env_g.lookup(node.graph_identifier)

            if graph_type not in self.graph_types:
                raise TypeCheckError(self.parse_graph_statement, self.graph_types, graph_type)

            if graph_weight_type not in self.arit_types and graph_weight_type is not None: # weight type can be none
                raise TypeCheckError(self.parse_graph_statement, self.arit_types, graph_weight_type)

            env_v.enter_scope()
            def fake_lookup(identifier):
                return TypeEnum.NODE
            fake_env_v = TypeEnv()
            fake_env_v.lookup = fake_lookup
            env_v, decl_type = self.parse_declaration(node.argument[0], fake_env_v)
            env_v.exit_scope()

            if decl_type is not TypeEnum.NODE:
                raise TypeCheckError(self.parse_graph_statement, TypeEnum.NODE, decl_type)
        else: # edge expr
            graph_type, graph_weight_type = env_g.lookup(node.graph_identifier)

            if graph_type not in self.graph_types:
                raise TypeCheckError(self.parse_graph_statement, self.graph_types, graph_type)

            if graph_weight_type not in self.arit_types and graph_weight_type is not None: # weight type can be none
                raise TypeCheckError(self.parse_graph_statement, self.arit_types, graph_weight_type)

            env_g.bind(0, (TypeEnum.TREE, TypeEnum.NAT))
            # judgment might need to change since edge decl suddently also can happen outside graph
            expr_type = self.parse_edge_declaration(node.argument, env_v, env_g, 0)

            if expr_type is not TypeEnum.EDGE:
                raise TypeCheckError(self.parse_graph_statement, TypeEnum.EDGE, expr_type)

        return True

    def parse_node_expression(self,
                              node: ASTNode,
                              env_v: TypeEnv,
                              env_a: TypeEnv,
                              env_g: TypeEnv
                              ) -> list[TypeEnum]:
        if not isinstance(node, ExprNode):
            raise Exception("parse_node_expression: Implementation error")

        expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)

        if expr_type is not TypeEnum.NODE:
            raise TypeCheckError(self.parse_node_expression, TypeEnum.NODE, expr_type)

        list_expr_type = [expr_type]
        setattr(node, "type", list_expr_type)
        return list_expr_type

    def parse_edge_declaration(self,
                              node: ASTNode,
                              env_v: TypeEnv,
                              env_g: TypeEnv,
                              curr_graph: str | None
                              ) -> TypeEnum:
        if not isinstance(node, EdgeDecl):
            raise Exception("parse_expression: Implementation error")

        kind: TypeEnum = TypeEnum.UNKNOWN

        if len(node.weight) == 0:
            if node.direction == "---":
                curr_graph_type = env_g.lookup(curr_graph)

                if curr_graph_type is TypeEnum.UNKNOWN:
                    raise TypeCheckError(self.parse_edge_declaration,
                                         "edge declaration only inside graph",
                                         "edge declaration outside graph")

                graph_type, graph_weight_type = curr_graph_type

                if graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }:
                    raise TypeCheckError(self.parse_edge_declaration, "undirected graph type", "directed graph type")
                if graph_weight_type not in self.arit_types and graph_weight_type is not None: # graph doesnt need type
                    raise TypeCheckError(self.parse_edge_declaration, self.arit_types, graph_weight_type)

                identifier1_type = env_v.lookup(node.initial_node.identifiers[0])
                if identifier1_type is not TypeEnum.NODE:
                    raise TypeCheckError(self.parse_edge_declaration, TypeEnum.NODE, identifier1_type)

                for _node in node.nodes:
                    _node_type = env_v.lookup(_node.identifiers[0])
                    if _node_type is not TypeEnum.NODE:
                        raise TypeCheckError(self.parse_edge_declaration, TypeEnum.NODE, _node_type)

                kind = TypeEnum.EDGE
            else:
                curr_graph_type = env_g.lookup(curr_graph)

                if curr_graph_type is TypeEnum.UNKNOWN:
                    raise TypeCheckError(self.parse_edge_declaration,
                                         "edge declaration only inside graph",
                                         "edge declaration outside graph")

                graph_type, graph_weight_type = curr_graph_type

                if graph_type not in { TypeEnum.DIGRAPH, TypeEnum.TREE }:
                    raise TypeCheckError(self.parse_edge_declaration, "directed graph type", "undirected graph type")
                if graph_weight_type not in self.arit_types and graph_weight_type is not None: # graph doesnt need type
                    raise TypeCheckError(self.parse_edge_declaration, self.arit_types, graph_weight_type)

                identifier1_type = env_v.lookup(node.initial_node.identifiers[0])
                if identifier1_type is not TypeEnum.NODE:
                    raise TypeCheckError(self.parse_edge_declaration, TypeEnum.NODE, identifier1_type)

                for _node in node.nodes:
                    _node_type = env_v.lookup(_node.identifiers[0])
                    if _node_type is not TypeEnum.NODE:
                        raise TypeCheckError(self.parse_edge_declaration, TypeEnum.NODE, _node_type)

                kind = TypeEnum.EDGE
        else:
            if node.direction == "---":
                curr_graph_type = env_g.lookup(curr_graph)

                if curr_graph_type is TypeEnum.UNKNOWN:
                    raise TypeCheckError(self.parse_edge_declaration,
                                         "edge declaration only inside graph",
                                         "edge declaration outside graph")

                graph_type, graph_weight_type = curr_graph_type

                if graph_type not in { TypeEnum.GRAPH, TypeEnum.TREE }:
                    raise TypeCheckError(self.parse_edge_declaration, "undirected graph type", "directed graph type")
                if graph_weight_type not in self.arit_types and graph_weight_type is not None: # graph doesnt need type
                    raise TypeCheckError(self.parse_edge_declaration, self.arit_types, graph_weight_type)

                identifier1_type = env_v.lookup(node.initial_node.identifiers[0])
                if identifier1_type is not TypeEnum.NODE:
                    raise TypeCheckError(self.parse_edge_declaration, TypeEnum.NODE, identifier1_type)

                if len(node.nodes) != len(node.weight):
                    raise TypeCheckError(self.parse_edge_declaration,
                                         "matching number of nodes and weights",
                                         "uneven amount of nodes and weigths")

                for _node, weight in zip(node.nodes, node.weight):
                    _node_type = env_v.lookup(_node.identifiers[0])
                    if _node_type is not TypeEnum.NODE:
                        raise TypeCheckError(self.parse_edge_declaration, TypeEnum.NODE, _node_type)

                    weight_type = self.parse_expression(weight, env_v, TypeEnv(), env_g)
                    # might need to add env_a to this

                    if weight_type not in self.arit_types:
                        raise TypeCheckError(self.parse_edge_declaration, self.arit_types, weight_type)

                kind = TypeEnum.EDGE
            else:
                curr_graph_type = env_g.lookup(curr_graph)

                if curr_graph_type is TypeEnum.UNKNOWN:
                    raise TypeCheckError(self.parse_edge_declaration,
                                         "edge declaration only inside graph",
                                         "edge declaration outside graph")

                graph_type, graph_weight_type = curr_graph_type

                if graph_type not in { TypeEnum.DIGRAPH, TypeEnum.TREE }:
                    raise TypeCheckError(self.parse_edge_declaration, "directed graph type", "undirected graph type")
                if graph_weight_type not in self.arit_types and graph_weight_type is not None: # graph doesnt need type
                    raise TypeCheckError(self.parse_edge_declaration, self.arit_types, graph_weight_type)

                identifier1_type = env_v.lookup(node.initial_node.identifiers[0])
                if identifier1_type is not TypeEnum.NODE:
                    raise TypeCheckError(self.parse_edge_declaration, TypeEnum.NODE, identifier1_type)

                if len(node.nodes) != len(node.weight):
                    raise TypeCheckError(self.parse_edge_declaration,
                                         "matching number of nodes and weights",
                                         "uneven amount of nodes and weigths")

                for _node, weight in zip(node.nodes, node.weight):
                    _node_type = env_v.lookup(_node.identifiers[0])
                    if _node_type is not TypeEnum.NODE:
                        raise TypeCheckError(self.parse_edge_declaration, TypeEnum.NODE, _node_type)

                    weight_type = self.parse_expression(weight, env_v, TypeEnv(), env_g)
                    # might need to add env_a to this

                    if weight_type not in self.arit_types:
                        raise TypeCheckError(self.parse_edge_declaration, self.arit_types, weight_type)

                kind = TypeEnum.EDGE

        setattr(node, "type", kind)
        return kind

    def parse_statement(self,
                        node: ASTNode,
                        env_v: TypeEnv,
                        env_a: TypeEnv,
                        env_g: TypeEnv,
                        curr_algo: str | None,
                        curr_graph: str | None,
                        inside_loop: bool
                        ) -> tuple[TypeEnv, TypeEnv, TypeEnv]:
        match node:
            # case S NL S # doesnt exist and is just a list on the node noew

            case DeclarationInit():
                env_v, decl_type = self.parse_declaration(node, env_v)

                if not isinstance(node.expression, list) or len(node.expression) != 1: # (dcl)
                    expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)

                    if expr_type != decl_type:
                        raise TypeCheckError(self.parse_statement, decl_type, expr_type)
                else: # (las) # not sure if i check matching length :/
                    for expr in node.expression:
                        expr_type = self.parse_expression(expr, env_v, env_a, env_g)

                        if expr_type != decl_type:
                            raise TypeCheckError(self.parse_statement, decl_type, expr_type)

            case Assignment():
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)

                for identifier in node.identifiers:
                    ident_type = env_v.lookup(identifier)

                    if ident_type != expr_type:
                        raise TypeCheckError(self.parse_statement, ident_type, expr_type)

            case Declaration() | NodeDecl():
                env_v, _ = self.parse_declaration(node, env_v)

            case IfStatement():
                if len(node.else_statements) == 0: # (ift)
                    if_kind = self.parse_expression(node.condition, env_v, env_a, env_g)

                    if if_kind != TypeEnum.BOOL:
                        raise TypeCheckError(self.parse_statement, TypeEnum.BOOL, if_kind)

                    env_v.enter_scope()
                    env_a.enter_scope() # objects are passed by reference so i use scope to avoid the updated env
                    env_g.enter_scope()
                    for statement in node.then_statements:
                        self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph, inside_loop)
                    env_v.exit_scope()
                    env_a.exit_scope()
                    env_g.exit_scope()
                else: # (ife)
                    if_kind = self.parse_expression(node.condition, env_v, env_a, env_g)

                    if if_kind != TypeEnum.BOOL:
                        raise TypeCheckError(self.parse_statement, TypeEnum.BOOL, if_kind)

                    env_v.enter_scope()
                    env_a.enter_scope() # objects are passed by reference so i use scope to avoid the updated env
                    env_g.enter_scope()
                    for statement in node.then_statements:
                        self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph, inside_loop)
                    env_v.exit_scope()
                    env_a.exit_scope()
                    env_g.exit_scope()

                    env_v.enter_scope()
                    env_a.enter_scope()
                    env_g.enter_scope()
                    for statement in node.else_statements:
                        self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph, inside_loop)
                    env_v.exit_scope()
                    env_a.exit_scope()
                    env_g.exit_scope()

            case WhileStatement():
                cond_kind = self.parse_expression(node.condition, env_v, env_a, env_g)

                if cond_kind != TypeEnum.BOOL:
                    raise TypeCheckError(self.parse_statement, TypeEnum.BOOL, cond_kind)

                env_v.enter_scope()
                env_a.enter_scope()
                env_g.enter_scope()
                for statement in node.statements:
                    self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph, inside_loop=True)
                env_v.exit_scope()
                env_a.exit_scope()
                env_g.exit_scope()

            case RepeatStatement():
                repeat_expression = self.parse_expression(node.repeat_expression, env_v, env_a, env_g)

                if repeat_expression != TypeEnum.NAT:
                    raise TypeCheckError(self.parse_statement, TypeEnum.NAT, repeat_expression)

                env_v.enter_scope()
                env_a.enter_scope()
                env_g.enter_scope()
                for statement in node.repeat_statements:
                    self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph, inside_loop=True)
                env_v.exit_scope()
                env_a.exit_scope()
                env_g.exit_scope()

            case ForEachNormal():
                iterable_type = self.parse_expression(node.iterable, env_v, env_a, env_g)

                if (
                    iterable_type is not TypeEnum.TEXT
                    and len(set(iterable_type)) > 1
                ):
                    raise TypeCheckError(self.parse_statement, "iterable type", iterable_type)

                env_v.enter_scope()
                env_v.bind(node.loop_identifier, iterable_type)
                for statement in node.statements:
                    self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph, inside_loop=True)
                env_v.exit_scope()

            case ForEachEdge():
                if node.weight_identifier is None: # (fre)
                    graph_type, graph_weight_type = env_g.lookup(node.graph_identifier)

                    if graph_type not in self.graph_types:
                        raise TypeCheckError(self.parse_statement, self.graph_types, graph_type)

                    if graph_weight_type not in self.arit_types and graph_weight_type is not None:
                        # could also be none / unknown since they dont need weight
                        raise TypeCheckError(self.parse_statement, f"{self.arit_types} or {None}", graph_weight_type)

                    # small problem, is that the edge declaration doesnt happen inside a graph so there is no nodes in env
                    def fake_lookup(identifier):
                        return TypeEnum.NODE
                    fake_env_v = TypeEnv()
                    fake_env_v.lookup = fake_lookup
                    edge_type = self.parse_edge_declaration(node.edge, fake_env_v, env_g, node.graph_identifier)

                    if edge_type is not TypeEnum.EDGE:
                        raise TypeCheckError(self.parse_statement, TypeEnum.EDGE, edge_type)

                    env_v.enter_scope()
                    env_a.enter_scope()
                    env_g.enter_scope()
                    for statement in node.statements:
                        self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph, inside_loop=True)
                    env_v.exit_scope()
                    env_a.exit_scope()
                    env_g.exit_scope()
                else: # (frw)
                    graph_type, graph_weight_type = env_g.lookup(node.graph_identifier)

                    if graph_type not in self.graph_types:
                        raise TypeCheckError(self.parse_statement, self.graph_types, graph_type)

                    if graph_weight_type not in self.arit_types:
                        raise TypeCheckError(self.parse_statement, self.arit_types, graph_weight_type)

                    # small problem, is that the edge declaration doesnt happen inside a graph so there is no nodes in env
                    def fake_lookup(identifier):
                        return TypeEnum.NODE
                    fake_env_v = TypeEnv()
                    fake_env_v.lookup = fake_lookup
                    edge_type = self.parse_edge_declaration(node.edge, fake_env_v, env_g, node.graph_identifier)

                    if edge_type is not TypeEnum.EDGE:
                        raise TypeCheckError(self.parse_statement, TypeEnum.EDGE, edge_type)

                    env_v.enter_scope()
                    env_a.enter_scope()
                    env_g.enter_scope()
                    env_v.bind(node.weight_identifier, graph_weight_type)
                    for statement in node.statements:
                        self.parse_statement(statement, env_v, env_a, env_g, curr_algo, curr_graph, inside_loop=True)
                    env_v.exit_scope()
                    env_a.exit_scope()
                    env_g.exit_scope()

            case ReturnStatement():
                if curr_algo is None:
                    raise TypeCheckError(self.parse_statement, "inside function", "outside function")

                _, expected_return_type = env_a.lookup(curr_algo)
                return_type = self.parse_expression(node.expression, env_v, env_a, env_g)

                if resolve_type(expected_return_type) != return_type:
                    raise TypeCheckError(self.parse_statement, expected_return_type, return_type)

            case Algorithm():
                env_a = self.parse_algorithm(node, env_a)

            case Expression():
                self.parse_expression(node, env_v, env_a, env_g)

            case LoopModifier():
                self.parse_loop_modifier(node, inside_loop)

            case GraphDecl():
                env_g = self.parse_graph_declaration(node, env_g)

            case EdgeDecl():
                edge_decl_type = self.parse_edge_declaration(node, env_v, env_g, curr_graph)

                if edge_decl_type is not TypeEnum.EDGE:
                    raise TypeCheckError(self.parse_expression, TypeEnum.EDGE, edge_decl_type)

            case GraphStatement():
                env_v.enter_scope()
                env_g.enter_scope()
                self.parse_graph_statement(node, env_v, env_g)
                env_v.exit_scope()
                env_g.exit_scope()

            case DisplayStatement():
                display_expr = self.parse_expression(node.expression, env_v, env_a, env_g)

                if display_expr is TypeEnum.UNKNOWN:
                    raise TypeCheckError(self.parse_statement, "not UNKNOWN", "UNKNOWN")

            case _:
                raise Exception(f"Unknown statement type")

        return env_v, env_a, env_g

    def parse_loop_modifier(self, node: ASTNode, inside_loop: bool) -> bool:
        if not isinstance(node, LoopModifier):
            raise Exception("parse_loop_modifier: Implementation error")

        if inside_loop is False:
            raise TypeCheckError(self.parse_loop_modifier, True, inside_loop)

        return True

    def parse_type(self, type_str: TypeEnum | str) -> bool:
        well_formed = False

        node_type = type_str if isinstance(type_str, TypeEnum) else resolve_type(type_str)

        match node_type:
            case TypeEnum.NAT | TypeEnum.INT | TypeEnum.REAL:
                well_formed = self.parse_type_arithmetic(node_type)

            case TypeEnum.GRAPH | TypeEnum.DIGRAPH | TypeEnum.TREE:
                well_formed = self.parse_graph_type(node_type)

            case TypeEnum.TEXT | TypeEnum.BOOL | TypeEnum.NODE:
                well_formed = True

        return well_formed

    def parse_type_arithmetic(self, type_arit: TypeEnum | str) -> bool:
        # elements gotten from the ast is in string form and needs to be converted
        node_type = type_arit if isinstance(type_arit, TypeEnum) else resolve_type(type_arit)

        return node_type in self.arit_types

    def parse_graph_type(self, graph_type: TypeEnum | str) -> bool:
        # elements gotten from the ast is in string form and needs to be converted
        node_type = graph_type if isinstance(graph_type, TypeEnum) else resolve_type(graph_type)
        return node_type in self.graph_types

    def parse_algorithm(self, node: ASTNode, env_a: TypeEnv) -> TypeEnv:
        if not isinstance(node, Algorithm):
            raise Exception("parse_algorithm: Implementation error")

        if node.return_type is None:
            env_v = TypeEnv()
            env_g = TypeEnv()
            parameter_types = []

            for param in node.parameters:
                env_v, decl_type = self.parse_declaration(param, env_v)
                parameter_types.append(decl_type)

            env_a.bind(node.identifier, (tuple(parameter_types), None))
            env_a.enter_scope()
            for statement in node.statements:
                self.parse_statement(statement, env_v, env_a, env_g, node.identifier, None, False)
            env_a.exit_scope()
        else:
            env_v = TypeEnv()
            env_g = TypeEnv()
            parameter_types = []

            for param in node.parameters:
                env_v, decl_type = self.parse_declaration(param, env_v)
                parameter_types.append(decl_type)

            if not self.parse_type(node.return_type):
                raise TypeCheckError(self.parse_statement, "valid return type", "Invalid return type")

            env_a.bind(node.identifier, (tuple(parameter_types), node.return_type))
            env_a.enter_scope()
            for statement in node.statements:
                self.parse_statement(statement, env_v, env_a, env_g, node.identifier, None, False)
            env_a.exit_scope()

        return env_a

    def parse_declaration(self, node: ASTNode, env_v: TypeEnv) -> tuple[TypeEnv, TypeEnum]:
        if (
            not isinstance(node, Declaration)
            and not isinstance(node, Parameter)
            and not isinstance(node, NodeDecl)
        ):
            raise Exception("parse_declaration: Implementation error")

        decl_type = TypeEnum.UNKNOWN

        # The parameter class is also treated as declaration but does not have is_list attr
        if getattr(node, "is_list", False) is False:
            if isinstance(node, Parameter):
                # parameter is not a list type like normal decl's, so it is converted
                setattr(node, "identifiers", [node.identifier])
            if isinstance(node, NodeDecl):
                # NodeDecl does not have type so its added
                setattr(node, "type", "node")

            if self.parse_type_arithmetic(node.type): # (dca)
                decl_type = resolve_type(node.type)
                for identifier in node.identifiers:
                    env_v.bind(identifier, decl_type)
            else: # (dti)
                if not self.parse_type(node.type):
                    raise TypeCheckError(self.parse_declaration, "valid type", "invalid type")

                decl_type = resolve_type(node.type)

                if decl_type not in { TypeEnum.NODE, TypeEnum.TEXT }:
                    raise TypeCheckError(self.parse_declaration, { TypeEnum.NODE, TypeEnum.TEXT }, decl_type)

                for identifier in node.identifiers:
                    env_v.bind(identifier, decl_type)
        else:
            env_v, decl_type = self.parse_declaration_list(node, env_v)

        return (env_v, decl_type)

    def parse_declaration_list(self, node: ASTNode, env_v: TypeEnv) -> tuple[TypeEnv, TypeEnum]:
        if not isinstance(node, Declaration) or node.is_list is False:
            raise Exception("parse_declaration_list: Implementation error")

        if not self.parse_dimensions(node.dimension):
            raise TypeCheckError(self.parse_declaration_list, "valid dimension", "invalid dimension")

        if not self.parse_type(node.type):
            raise TypeCheckError(self.parse_declaration_list, "valid type", "invalid type")

        env_v.bind(node.identifiers[0], node.type)

        return (env_v, node.type)

    def parse_dimensions(self, dimensions: str) -> bool:
        well_formed = False

        if dimensions is not None:
            dimension = dimensions.strip("d")
            dimension_type = ""
            try:
                dimension = int(dimension)
                if dimension >= 0:
                    dimension_type ="NATURAL_NUMBER"
            except Exception: # lazy catch of all errors from the trying the int() function
                raise TypeCheckError(self.parse_dimensions, "dimension is nat", "not nat")
            #^^ no node for the dimension and rule said to pass to expression, so faked ^^#

            fake_dimension_node = Term("Dimension")
            fake_dimension_node.type = dimension_type
            kind = self.parse_expression(fake_dimension_node, TypeEnv(), TypeEnv(), TypeEnv())

            if kind != TypeEnum.NAT:
                return False

            well_formed = True
        else: # DIM can be empty
            well_formed = True

        return well_formed

    def parse_graph_declaration(self, node: ASTNode, env_g: TypeEnv) -> TypeEnv:
        if not isinstance(node, GraphDecl):
            raise Exception("parse_graph_declaration: Implementation error")

        if node.nodes is None and node.edges is None:
            if node.weight_type is None:
                graph_type = resolve_type(node.graph_type)

                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                env_g.bind(node.identifier, (graph_type, None))
            else:
                graph_type = resolve_type(node.graph_type)
                weight_type = resolve_type(node.weight_type)

                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                if not self.parse_type_arithmetic(weight_type):
                    raise TypeCheckError(self.parse_graph_declaration, self.arit_types, weight_type)

                env_g.bind(node.identifier, (graph_type, weight_type))
        else: # graph declaration with body
            if node.weight_type is None:
                graph_type = resolve_type(node.graph_type)

                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                env_g.bind(node.identifier, (graph_type, None))

                env_g.enter_scope() # as the rules show we dont want the update
                env_v = TypeEnv()
                env_a = TypeEnv()
                for _node in [*node.nodes, *node.edges]:
                    env_v, env_a, env_g = self.parse_statement(_node, env_v, env_a, env_g, None, node.identifier, False)
                env_g.exit_scope()
            else:
                graph_type = resolve_type(node.graph_type)
                weight_type = resolve_type(node.weight_type)

                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                if not self.parse_type_arithmetic(weight_type):
                    raise TypeCheckError(self.parse_graph_declaration, self.arit_types, weight_type)

                env_g.bind(node.identifier, (graph_type, weight_type))

                env_g.enter_scope() # as the rules show we dont want the update
                env_v = TypeEnv()
                env_a = TypeEnv()
                for _node in [*node.nodes, *node.edges]:
                    env_v, env_a, env_g = self.parse_statement(_node, env_v, env_a, env_g, None, node.identifier, False)
                env_g.exit_scope()

        return env_g

    def lub_arit(self, type_1: TypeEnum, type_2: TypeEnum) -> TypeEnum:
        """Largest upper bound helper function""" # explicit on purpose
        arit_order = {
            TypeEnum.NAT: 1,
            TypeEnum.INT: 2,
            TypeEnum.REAL: 3
        }

        _type_1 = arit_order.get(type_1, None)
        _type_2 = arit_order.get(type_2, None)

        if _type_1 is None or _type_2 is None:
            raise Exception("Types must be arithmetic types")

        if _type_1 == _type_2:
            return type_1
        elif _type_1 < _type_2:
            return type_2
        else: # _type_2 < _type_1
            return type_1