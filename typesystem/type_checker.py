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

    # comments for each type rule of the type: '# (xxx)'
    # are added to the case where they are handled

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

        if len(node.children) > 1: # (pgm)
            try: # create the initial environments and parse the program
                env_v = TypeEnv(); env_a = TypeEnv(); env_g = TypeEnv(); env_i = TypeEnv()
                for statement in node.children[:-1]: # does not follow rule, but (com) doesn't exist
                    env_v, env_a, env_g, env_i = self.parse_statement(statement, env_v, env_a, env_g, env_i,
                                                                      None, None, False)
                well_formed = True
            except TypeCheckError as e:
                print(f"TypeCheckError: {e}")
        else: # (pgn)
            # last element is always expected to be EOF
            end_of_file = node.children[-1]
            if end_of_file.token == "EOF":
                well_formed = True

        return well_formed

    def parse_expression(self,
                         node: ASTNode,
                         env_v: TypeEnv,
                         env_a: TypeEnv,
                         env_g: TypeEnv,
                         env_i: TypeEnv
                         ) -> TypeEnum | list[TypeEnum]:
        kind: TypeEnum | list[TypeEnum] = TypeEnum.UNKNOWN
        match node:
            case Term():
                match node.type:
                    case "INTEGER_NUMBER" | TypeEnum.INT: # (int)
                        kind = TypeEnum.INT

                    case "NATURAL_NUMBER" | TypeEnum.NAT: # (nat)
                        kind = TypeEnum.NAT

                    case "REAL_NUMBER" | TypeEnum.REAL: # (rea)
                        kind = TypeEnum.REAL

                    case "TEXT" | TypeEnum.TEXT: # (str)
                        kind = TypeEnum.TEXT

                    case "BOOL_VALUE" | TypeEnum.BOOL: # (boo)
                        kind = TypeEnum.BOOL

                    case "IDENTIFIER": # (var)
                        ident_type = env_v.lookup(node.value)
                        self.reject_type(ident_type, TypeEnum.UNKNOWN, self.parse_expression)
                        kind = ident_type

                    case _:
                        raise Exception("Unknown term type")

            case ExprNode(): # (new)
                node_expr_type = self.parse_node_expression(node, env_v, env_a, env_g, env_i)
                self.expect_type_list_of(node_expr_type, TypeEnum.NODE, self.parse_expression)
                kind = node_expr_type # special type (list[TypeEnum])

            case AbsoluteValue(): # (abs)
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, env_i)
                self.expect_type_one_of(expr_type, self.arit_types, self.parse_expression)
                kind = TypeEnum.NAT

            case Magnitude(): # (mag)
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, env_i)
                if (
                    expr_type is not TypeEnum.TEXT
                    and not isinstance(expr_type, list) and len(set(expr_type)) > 1
                ):
                    raise TypeCheckError(self.parse_expression, f"{TypeEnum.TEXT} or list", expr_type)
                kind = TypeEnum.NAT

            case AlgorithmCall(): # (agc)
                algo_type = env_a.lookup(node.identifier)
                self.reject_type(algo_type, TypeEnum.UNKNOWN, self.parse_expression)

                arguments = node.arguments if node.arguments is not None else []
                if len(algo_type["parameters"]) != len(arguments):
                    raise TypeCheckError(self.parse_expression, "same number of parameters and arguments", "not that")

                for param_type, arg in zip(algo_type["parameters"], arguments):
                    arg_type = self.parse_expression(arg, env_v, env_a, env_g, env_i)
                    self.expect_type(arg_type, param_type, self.parse_expression)

                kind = algo_type["return_type"]

            case ArrayAccess(): # (arr)
                for index in node.indexes:
                    expr_type = self.parse_expression(index, env_v, env_a, env_g, env_i)
                    self.expect_type(expr_type, TypeEnum.NAT, self.parse_expression)

                array_type = env_v.lookup(node.identifier)
                self.reject_type(array_type, TypeEnum.UNKNOWN, self.parse_expression)

                kind = array_type

            case IdentifierAccess():
                for identifier in node.identifiers:
                    if isinstance(identifier, str):
                        if env_v.lookup(identifier) is not TypeEnum.NODE: # (dt1)
                            graph = env_g.lookup(env_i.lookup(identifier))
                            self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_expression)

                            kind = graph[0] # GT
                        else: # (dt2)
                            node_type = env_v.lookup(identifier)
                            self.expect_type(node_type, TypeEnum.NODE, self.parse_expression)

                            kind = node_type
                    elif isinstance(identifier, AlgorithmCall) or isinstance(identifier, ArrayAccess):
                        kind = self.parse_expression(identifier, env_v, env_a, env_g, env_i)

            case ListExpression(): # (arl)
                list_types = []
                for child in node.expressions:
                    list_types.append(self.parse_expression(child, env_v, env_a, env_g, env_i))
                self.expect_list_of_one_type(list_types, self.parse_expression)

                kind = list_types[0] if len(list_types) > 0 else TypeEnum.UNKNOWN

            case Expression():
                match node.operator:
                    case "+" | "-" | "*" | "/": # (ope)
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, env_i)
                        self.reject_type(expr1_type, TypeEnum.UNKNOWN, self.parse_expression)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, env_i)
                        self.reject_type(expr2_type, TypeEnum.UNKNOWN, self.parse_expression)

                        kind = self.lub_arit(expr1_type, expr2_type)

                    case "%": # (mod)
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, env_i)
                        self.expect_type_one_of(expr1_type, { TypeEnum.NAT, TypeEnum.INT }, self.parse_expression)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, env_i)
                        self.expect_type_one_of(expr2_type, { TypeEnum.NAT, TypeEnum.INT }, self.parse_expression)

                        kind = self.lub_arit(expr1_type, expr2_type)

                    case "^": # (pow)
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, env_i)
                        self.reject_type(expr1_type, TypeEnum.UNKNOWN, self.parse_expression)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, env_i)
                        self.expect_type_one_of(expr2_type, { TypeEnum.NAT, TypeEnum.INT }, self.parse_expression)

                        kind = expr1_type

                    case "weight of":
                        if "-->" in node.arg1: # (wot)
                            ident1n2, ident3 = node.arg1.split("-->")
                            ident1, ident2 = ident1n2.split(".")

                            graph_type, graph_weight_type, graph_env_v = env_g.lookup(env_i.lookup(ident1))
                            self.expect_type_one_of(graph_type, { TypeEnum.DIGRAPH, TypeEnum.TREE },
                                                    self.parse_expression)
                            self.expect_type_one_of(graph_weight_type, self.arit_types, self.parse_expression)

                            ident2_type = graph_env_v.lookup(ident2)
                            self.expect_type(ident2_type, TypeEnum.NODE, self.parse_expression)

                            ident3_type = graph_env_v.lookup(ident3)
                            self.expect_type(ident3_type, TypeEnum.NODE, self.parse_expression)

                            kind = graph_weight_type
                        else: # (woe)
                            ident1n2, ident3 = node.arg1.split("---")
                            ident1, ident2 = ident1n2.split(".")

                            graph_type, graph_weight_type, graph_env_v = env_g.lookup(env_i.lookup(ident1))
                            self.expect_type_one_of(graph_type, { TypeEnum.GRAPH, TypeEnum.TREE },
                                                    self.parse_expression)
                            self.expect_type_one_of(graph_weight_type, self.arit_types, self.parse_expression)

                            ident2_type = graph_env_v.lookup(ident2)
                            self.expect_type(ident2_type, TypeEnum.NODE, self.parse_expression)

                            ident3_type = graph_env_v.lookup(ident3)
                            self.expect_type(ident2_type, TypeEnum.NODE, self.parse_expression)

                            kind = graph_weight_type

                    case "=" | "!=" | "<" | "<=" | ">" | ">=": # (cmp)
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, env_i)
                        self.expect_type_one_of(expr1_type, self.arit_types, self.parse_expression)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, env_i)
                        self.expect_type_one_of(expr2_type, self.arit_types, self.parse_expression)

                        kind = TypeEnum.BOOL

                    case "neg": # (neg)
                        expr_type = self.parse_expression(node.arg1, env_v, env_a, env_g, env_i)
                        self.expect_type(expr_type, TypeEnum.BOOL, self.parse_expression)

                        kind = expr_type

                    case "and": # (and)
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, env_i)
                        self.expect_type(expr1_type, TypeEnum.BOOL, self.parse_expression)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, env_i)
                        self.expect_type(expr2_type, TypeEnum.BOOL, self.parse_expression)

                        kind = expr1_type

                    case "or": # (ore)
                        expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g, env_i)
                        self.expect_type(expr1_type, TypeEnum.BOOL, self.parse_expression)

                        expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g, env_i)
                        self.expect_type(expr2_type, TypeEnum.BOOL, self.parse_expression)

                        kind = expr1_type

                    case None | "":
                        kind = self.parse_expression(node.arg1, env_v, env_a, env_g, env_i)

                    case _:
                        raise Exception("Unknown operator")

            case _:
                raise Exception("Unknown expression type")

        setattr(node, "type", kind)
        return kind

    def parse_graph_statement(self,
                              node: ASTNode,
                              env_v: TypeEnv,
                              env_g: TypeEnv,
                              env_i: TypeEnv
                              ) -> TypeEnv:
        if not isinstance(node, GraphStatement):
            raise Exception("parse_graph_expression: Implementation error")

        if not isinstance(node.argument, EdgeDecl):
            if node.operator == "add": # (gan)
                graph = env_g.lookup(env_i.lookup(node.graph_identifier))
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_graph_statement)

                env_v1, env_g1, decl_type = self.parse_declaration(node.argument, env_v, env_g, env_i,
                                                                   node.graph_identifier)
                env_g = env_g1

                self.expect_type(decl_type, TypeEnum.NODE, self.parse_graph_statement)
            else: # (grn)
                graph_type, graph_weight_type, graph_env_v = env_g.lookup(env_i.lookup(node.graph_identifier))
                self.expect_type_one_of(graph_type, self.graph_types, self.parse_graph_statement)

                ident2_type = graph_env_v.lookup(node.argument)
                self.expect_type(ident2_type, TypeEnum.NODE, self.parse_graph_statement)

                env_v1, env_g1, decl_type = self.parse_declaration(node.argument, env_v, env_g, env_i,
                                                                   node.graph_identifier)
                env_g = env_g1

                self.expect_type(decl_type, TypeEnum.NODE, self.parse_graph_statement)
        else: # (are)
            graph = env_i.lookup(node.graph_identifier)
            self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_graph_statement)

            expr_type = self.parse_edge_declaration(node.argument, env_g, env_i, node.graph_identifier)
            self.expect_type(expr_type, TypeEnum.EDGE, self.parse_graph_statement)

        return env_g

    def parse_node_expression(self,
                              node: ASTNode,
                              env_v: TypeEnv,
                              env_a: TypeEnv,
                              env_g: TypeEnv,
                              env_i: TypeEnv
                              ) -> list[TypeEnum]:
        if not isinstance(node, ExprNode):
            raise Exception("parse_node_expression: Implementation error")

        # (ind)
        expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, env_i)
        self.expect_type(expr_type, TypeEnum.NODE, self.parse_node_expression)

        list_expr_type = [TypeEnum.NODE]
        setattr(node, "type", list_expr_type)
        return list_expr_type

    def parse_edge_declaration(self,
                              node: ASTNode,
                              env_g: TypeEnv,
                              env_i: TypeEnv,
                              curr_graph: str | None
                              ) -> TypeEnum:
        if not isinstance(node, EdgeDecl):
            raise Exception("parse_expression: Implementation error")

        kind: TypeEnum = TypeEnum.UNKNOWN

        if len(node.weight) == 0:
            if node.direction == "---": # (edu)
                curr_graph_type = env_g.lookup(env_i.lookup(curr_graph))
                self.reject_type(curr_graph_type, TypeEnum.UNKNOWN, self.parse_edge_declaration)

                graph_type, graph_weight_type, graph_env_v = curr_graph_type
                self.expect_type_one_of(graph_type, { TypeEnum.GRAPH, TypeEnum.TREE }, self.parse_edge_declaration)

                identifier1_type = graph_env_v.lookup(
                    node.initial_node.identifiers[0]
                    if isinstance(node.initial_node, IdentifierAccess)
                    else node.initial_node
                )
                self.expect_type(identifier1_type, TypeEnum.NODE, self.parse_edge_declaration)

                for _node in node.nodes:
                    _node_type = graph_env_v.lookup(
                        _node.identifiers[0]
                        if isinstance(_node, IdentifierAccess)
                        else _node
                    )
                    self.expect_type(_node_type, TypeEnum.NODE, self.parse_edge_declaration)

                kind = TypeEnum.EDGE
            else: # (edd)
                curr_graph_type = env_g.lookup(env_i.lookup(curr_graph))
                self.reject_type(curr_graph_type, TypeEnum.UNKNOWN, self.parse_edge_declaration)

                graph_type, graph_weight_type, graph_env_v = curr_graph_type
                self.expect_type_one_of(graph_type, { TypeEnum.DIGRAPH, TypeEnum.TREE }, self.parse_edge_declaration)

                identifier1_type = graph_env_v.lookup(
                    node.initial_node.identifiers[0]
                    if isinstance(node.initial_node, IdentifierAccess)
                    else node.initial_node
                )
                self.expect_type(identifier1_type, TypeEnum.NODE, self.parse_edge_declaration)

                for _node in node.nodes:
                    _node_type = graph_env_v.lookup(
                        _node.identifiers[0]
                        if isinstance(_node, IdentifierAccess)
                        else _node
                    )
                    self.expect_type(_node_type, TypeEnum.NODE, self.parse_edge_declaration)

                kind = TypeEnum.EDGE
        else:
            if node.direction == "---": # (ewu)
                curr_graph_type = env_g.lookup(env_i.lookup(curr_graph))
                self.reject_type(curr_graph_type, TypeEnum.UNKNOWN, self.parse_edge_declaration)

                graph_type, graph_weight_type, graph_env_v = curr_graph_type
                self.expect_type_one_of(graph_type, { TypeEnum.GRAPH, TypeEnum.TREE }, self.parse_edge_declaration)
                self.expect_type_one_of(graph_weight_type, self.arit_types, self.parse_edge_declaration)

                identifier1_type = graph_env_v.lookup(
                    node.initial_node.identifiers[0]
                    if isinstance(node.initial_node, IdentifierAccess)
                    else node.initial_node
                )
                self.expect_type(identifier1_type, TypeEnum.NODE, self.parse_edge_declaration)

                if len(node.nodes) != len(node.weight):
                    raise TypeCheckError(self.parse_edge_declaration,
                                         "matching number of nodes and weights",
                                         "uneven amount of nodes and weigths")

                for _node, weight in zip(node.nodes, node.weight):
                    _node_type = graph_env_v.lookup(
                        _node.identifiers[0]
                        if isinstance(_node, IdentifierAccess)
                        else _node
                    )
                    self.expect_type(_node_type, TypeEnum.NODE, self.parse_edge_declaration)

                    weight_type = self.parse_expression(weight, TypeEnv(), TypeEnv(), env_g, env_i)
                    self.expect_type_one_of(weight_type, self.arit_types, self.parse_edge_declaration)

                kind = TypeEnum.EDGE
            else: # (ewd)
                curr_graph_type = env_g.lookup(env_i.lookup(curr_graph))
                self.reject_type(curr_graph_type, TypeEnum.UNKNOWN, self.parse_edge_declaration)

                graph_type, graph_weight_type, graph_env_v = curr_graph_type
                self.expect_type_one_of(graph_type, { TypeEnum.DIGRAPH, TypeEnum.TREE }, self.parse_edge_declaration)
                self.expect_type_one_of(graph_weight_type, self.arit_types, self.parse_edge_declaration)

                identifier1_type = graph_env_v.lookup(
                    node.initial_node.identifiers[0]
                    if isinstance(node.initial_node, IdentifierAccess)
                    else node.initial_node
                )
                self.expect_type(identifier1_type, TypeEnum.NODE, self.parse_edge_declaration)

                if len(node.nodes) != len(node.weight):
                    raise TypeCheckError(self.parse_edge_declaration,
                                         "matching number of nodes and weights",
                                         "uneven amount of nodes and weigths")

                for _node, weight in zip(node.nodes, node.weight):
                    _node_type = graph_env_v.lookup(
                        _node.identifiers[0]
                        if isinstance(_node, IdentifierAccess)
                        else _node
                    )
                    self.expect_type(_node_type, TypeEnum.NODE, self.parse_edge_declaration)

                    weight_type = self.parse_expression(weight, TypeEnv(), TypeEnv(), env_g, env_i)
                    self.expect_type_one_of(weight_type, self.arit_types, self.parse_edge_declaration)

                kind = TypeEnum.EDGE

        setattr(node, "type", kind)
        return kind

    def parse_edge_loop(self, node: ASTNode, env_v: TypeEnv) -> TypeEnv:
        if not isinstance(node, EdgeLoop):
            raise Exception("parse_expression: Implementation error")
        # (eel)
        return env_v.bind(node.initial_node, TypeEnum.NODE).bind(node.last_node, TypeEnum.NODE)

    def parse_statement(self,
                        node: ASTNode,
                        env_v: TypeEnv,
                        env_a: TypeEnv,
                        env_g: TypeEnv,
                        env_i: TypeEnv,
                        curr_algo: str | None,
                        curr_graph: str | None,
                        inside_loop: bool
                        ) -> tuple[TypeEnv, TypeEnv, TypeEnv, TypeEnv]:
        match node:
            # case S NL S # (com) # doesnt exist and is just a list on the node noew

            case DeclarationInit():
                if not isinstance(node.expression, list) or len(node.expression) != 1: # (dcl)
                    env_v1, env_g1, decl_type = self.parse_declaration(node, env_v, env_g, env_i, curr_graph)
                    expr_type = self.parse_expression(node.expression, env_v1, env_a, env_g1, env_i)
                    self.expect_type(expr_type, decl_type, self.parse_statement)

                    env_v = env_v1
                    env_g = env_g1
                else: # (las) # not sure if i check matching length :/
                    env_v1, decl_type = self.parse_declaration_list(node, env_v)
                    for expr in node.expression:
                        expr_type = self.parse_expression(expr, env_v1, env_a, env_g, env_i)
                        self.expect_type(expr_type, decl_type, self.parse_statement)

                    env_v = env_v1

            case Assignment(): # (ass)
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g, env_i)
                for identifier in node.identifiers:
                    ident_type = env_v.lookup(identifier)
                    self.expect_type(ident_type, expr_type, self.parse_statement)

            case Declaration() | NodeDecl(): # (std)
                env_v1, env_g1, _ = self.parse_declaration(node, env_v, env_g, env_i, curr_graph)
                env_v = env_v1
                env_g = env_g1

            case IfStatement():
                if len(node.else_statements) == 0: # (ift)
                    if_kind = self.parse_expression(node.condition, env_v, env_a, env_g, env_i)
                    self.expect_type(if_kind, TypeEnum.BOOL, self.parse_statement)

                    env_v1 = env_v; env_a1 = env_a; env_g1 = env_g; env_i1 = env_i
                    for statement in node.then_statements:
                        env_v1, env_a1, env_g1, env_i1 = self.parse_statement(statement, env_v1, env_a1, env_g1, env_i1,
                                                                              curr_algo, curr_graph, inside_loop)
                    env_g = env_g1 # only update env_g as rule states
                else: # (ife)
                    if_kind = self.parse_expression(node.condition, env_v, env_a, env_g, env_i)
                    self.expect_type(if_kind, TypeEnum.BOOL, self.parse_statement)

                    env_v1 = env_v; env_a1 = env_a; env_g1 = env_g; env_i1 = env_i
                    for statement in node.then_statements:
                        env_v1, env_a1, env_g1, env_i1 = self.parse_statement(statement, env_v1, env_a1, env_g1, env_i1,
                                                                              curr_algo, curr_graph, inside_loop)

                    env_v2 = env_v; env_a2 = env_a; env_g2 = env_g1; env_i2 = env_i
                    for statement in node.else_statements:
                        env_v2, env_a2, env_g2, env_i2 = self.parse_statement(statement, env_v2, env_a2, env_g2, env_i2,
                                                                              curr_algo, curr_graph, inside_loop)
                    env_g = env_g2 # only update env_g as rule states

            case WhileStatement(): # (whl)
                cond_kind = self.parse_expression(node.condition, env_v, env_a, env_g, env_i)
                self.expect_type(cond_kind, TypeEnum.BOOL, self.parse_statement)

                env_v1 = env_v; env_a1 = env_a; env_g1 = env_g; env_i1 = env_i
                for statement in node.statements:
                    env_v1, env_a1, env_g1, env_i1 = self.parse_statement(statement, env_v1, env_a1, env_g1, env_i1,
                                                                          curr_algo, curr_graph, inside_loop=True)
                env_g = env_g1 # only update env_g as rule states

            case RepeatStatement(): # (rpt)
                repeat_expression = self.parse_expression(node.repeat_expression, env_v, env_a, env_g, env_i)
                self.expect_type(repeat_expression, TypeEnum.NAT, self.parse_statement)

                env_v1 = env_v; env_a1 = env_a; env_g1 = env_g; env_i1 = env_i
                for statement in node.repeat_statements:
                    env_v1, env_a1, env_g1, env_i1 = self.parse_statement(statement, env_v1, env_a1, env_g1, env_i1,
                                                                          curr_algo, curr_graph, inside_loop=True)
                env_g = env_g1 # only update env_g as rule states

            case ForEachNormal(): # (for)
                iterable_type = self.parse_expression(node.iterable, env_v, env_a, env_g, env_i)
                if (
                    iterable_type is not TypeEnum.TEXT
                    and len(set(iterable_type)) > 1
                ):
                    raise TypeCheckError(self.parse_statement, "iterable type", iterable_type)

                env_v1 = env_v.bind(node.loop_identifier, iterable_type)
                env_a1 = env_a; env_g1 = env_g; env_i1 = env_i
                for statement in node.statements:
                    env_v1, env_a1, env_g1, env_i1 = self.parse_statement(statement, env_v1, env_a1, env_g1, env_i1,
                                                                          curr_algo, curr_graph, inside_loop=True)
                env_g = env_g1 # only update env_g as rule states

            case ForEachEdge():
                if node.weight_identifier is None: # (fre)
                    graph = env_i.lookup(node.graph_identifier)
                    self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_statement)

                    env_v1 = self.parse_edge_loop(node.edge, env_v)

                    env_v2 = env_v1; env_a1 = env_a; env_g1 = env_g; env_i1 = env_i
                    for statement in node.statements:
                        env_v2, env_a1, env_g1, env_i1 = self.parse_statement(statement, env_v2, env_a1, env_g1, env_i1,
                                                                              curr_algo, curr_graph, inside_loop=True)
                    env_g = env_g1 # only update env_g as rule states
                else: # (frw)
                    graph_type, graph_weight_type, graph_env_v = env_g.lookup(env_i.lookup(node.graph_identifier))
                    self.expect_type_one_of(graph_type, self.graph_types, self.parse_statement)
                    self.expect_type_one_of(graph_weight_type, self.arit_types, self.parse_statement)

                    env_v1 = self.parse_edge_loop(node.edge, env_v)

                    env_v2 = env_v.bind(node.weight_identifier, graph_weight_type)
                    env_a1 = env_a; env_g1 = env_g; env_i1 = env_i
                    for statement in node.statements:
                        env_v2, env_a1, env_g1, env_i1 = self.parse_statement(statement, env_v2, env_a1, env_g1, env_i1,
                                                                              curr_algo, curr_graph, inside_loop=True)
                    env_g = env_g1 # only update env_g as rule states

            case ReturnStatement(): # (ret)
                if curr_algo is None:
                    raise TypeCheckError(self.parse_statement, "inside function", "outside function")

                algorithm = env_a.lookup(curr_algo)
                return_type = self.parse_expression(node.expression, env_v, env_a, env_g, env_i)
                self.expect_type(algorithm["return_type"], return_type, self.parse_statement)

            case Algorithm(): # (alg)
                env_a1 = self.parse_algorithm(node, env_a)
                env_a = env_a1

            case Expression(): # (exp)
                self.parse_expression(node, env_v, env_a, env_g, env_i)

            case LoopModifier(): # (lop)
                self.parse_loop_modifier(node, inside_loop)

            case GraphDecl(): # (grt)
                env_g1, env_i1 = self.parse_graph_declaration(node, env_g, env_i)
                env_g = env_g1
                env_i = env_i1

            case EdgeDecl(): # (edc)
                edge_decl_type = self.parse_edge_declaration(node, env_g, env_i, curr_graph)
                self.expect_type(edge_decl_type, TypeEnum.EDGE, self.parse_expression)

            case GraphStatement(): # (gst)
                env_g1 = self.parse_graph_statement(node, env_v, env_g, env_i)
                env_g = env_g1

            case DisplayStatement(): # (dis)
                display_expr = self.parse_expression(node.expression, env_v, env_a, env_g, env_i)
                self.reject_type(display_expr, TypeEnum.UNKNOWN, self.parse_statement)

            case _:
                raise Exception(f"Unknown statement type")

        return env_v, env_a, env_g, env_i

    def parse_loop_modifier(self, node: ASTNode, inside_loop: bool) -> bool:
        if not isinstance(node, LoopModifier):
            raise Exception("parse_loop_modifier: Implementation error")

        # (stp)
        if inside_loop is False:
            raise TypeCheckError(self.parse_loop_modifier, True, inside_loop)

        return True

    def parse_type(self, type_str: TypeEnum | str) -> bool:
        well_formed = False
        node_type = type_str if isinstance(type_str, TypeEnum) else resolve_type(type_str)
        match node_type:
            case TypeEnum.BOOL: # (bol)
                well_formed = True

            case TypeEnum.TEXT: # (txt)
                well_formed = True

            case TypeEnum.NODE: # (nod)
                well_formed = True

            case TypeEnum.EDGE: # (edg)
                well_formed = True

            case TypeEnum.NAT | TypeEnum.INT | TypeEnum.REAL: # (tar)
                well_formed = self.parse_type_arithmetic(node_type)

            case TypeEnum.GRAPH | TypeEnum.DIGRAPH | TypeEnum.TREE: # (tgt)
                well_formed = self.parse_graph_type(node_type)

        return well_formed

    def parse_type_arithmetic(self, type_arit: TypeEnum | str) -> bool:
        # elements gotten from the ast is in string form and needs to be converted
        node_type = type_arit if isinstance(type_arit, TypeEnum) else resolve_type(type_arit)
        well_formed = False
        match node_type:
            case TypeEnum.INT: # (itt)
                well_formed = True

            case TypeEnum.NAT: # (ntt)
                well_formed = True

            case TypeEnum.REAL: # (rlt)
                well_formed = True

        return well_formed

    def parse_graph_type(self, graph_type: TypeEnum | str) -> bool:
        # elements gotten from the ast is in string form and needs to be converted
        node_type = graph_type if isinstance(graph_type, TypeEnum) else resolve_type(graph_type)
        well_formed = False
        match node_type:
            case TypeEnum.GRAPH: # (grp)
                well_formed = True

            case TypeEnum.DIGRAPH: # (dgr)
                well_formed = True

            case TypeEnum.TREE: # (tre)
                well_formed = True

        return well_formed

    def parse_algorithm(self, node: ASTNode, env_a: TypeEnv) -> TypeEnv:
        if not isinstance(node, Algorithm):
            raise Exception("parse_algorithm: Implementation error")

        if node.return_type is None: # (alg)
            env_v = TypeEnv()
            env_g = TypeEnv()
            env_i = TypeEnv()
            parameter_types = []

            # yes i assign them again, just to make them look more like rule
            env_vi = env_v; env_gi = env_g
            for param in node.parameters:
                env_vi, env_gi, decl_type = self.parse_declaration(param, env_vi, env_gi, env_i, None)
                parameter_types.append(decl_type)

            env_a1 = env_a.bind(node.identifier, {"parameters": tuple(parameter_types),
                                                  "return_type": TypeEnum.UNKNOWN})

            env_v1 = env_vi; env_a2 = env_a1; env_g1 = env_gi; env_i1 = env_i
            for statement in node.statements:
                env_v1, env_a2, env_g1, env_i1 = self.parse_statement(statement, env_v1, env_a2, env_g1, env_i1,
                                                                      node.identifier, None, False)
            env_a = env_a1
        else: # (alr)
            env_v = TypeEnv()
            env_g = TypeEnv()
            env_i = TypeEnv()
            parameter_types = []
            return_type = resolve_type(node.return_type)

            # yes i assign them again, just to make them look more like rule
            env_v1 = env_v; env_g1 = env_g
            for param in node.parameters:
                env_v1, env_g1, decl_type = self.parse_declaration(param, env_v1, env_g1, env_i, None)

            if not self.parse_type(return_type):
                raise TypeCheckError(self.parse_statement, "valid return type", "Invalid return type")

            env_a1 = env_a.bind(node.identifier, {"parameters": tuple(parameter_types),
                                                  "return_type": return_type})

            env_v2 = env_v1; env_a2 = env_a1; env_g2 = env_g1; env_i1 = env_i
            for statement in node.statements:
                env_v2, env_a2, env_g2, env_i1 = self.parse_statement(statement, env_v2, env_a2, env_g2, env_i1,
                                                                      node.identifier, None, False)
            env_a = env_a1

        return env_a

    def parse_declaration(self, node: ASTNode,
                          env_v: TypeEnv,
                          env_g: TypeEnv,
                          env_i: TypeEnv,
                          curr_graph: str | None
                          ) -> tuple[TypeEnv, TypeEnv, TypeEnum]:
        if (
            not isinstance(node, Declaration)
            and not isinstance(node, Parameter)
            and not isinstance(node, NodeDecl)
        ):
            raise Exception("parse_declaration: Implementation error")

        decl_type = TypeEnum.UNKNOWN
        # The parameter class is also treated as declaration but does not have is_list attr
        if getattr(node, "is_list", False) is False:
            if isinstance(node, Parameter): # parameter is not a list type like normal decl's, so it is converted
                setattr(node, "identifiers", [node.identifier])

            if self.parse_type_arithmetic(node.type): # (dca)
                decl_type = resolve_type(node.type)
                for identifier in node.identifiers:
                    env_v = env_v.bind(identifier, decl_type)
            else:
                if env_i.lookup(curr_graph) == TypeEnum.UNKNOWN: # (dti)
                    decl_type = resolve_type(node.type)
                    if not self.parse_type(decl_type):
                        raise TypeCheckError(self.parse_declaration, "valid type", "invalid type")
                    self.expect_type_one_of(decl_type, { TypeEnum.NODE, TypeEnum.TEXT }, self.parse_declaration)

                    for identifier in node.identifiers:
                        env_v = env_v.bind(identifier, decl_type)
                else: # (dtg)
                    graph_type, graph_weight_type, graph_env_v = env_g.lookup(env_i.lookup(curr_graph))

                    decl_type = resolve_type(node.type)
                    if not self.parse_type(decl_type):
                        raise TypeCheckError(self.parse_declaration, "valid type", "invalid type")

                    self.expect_type(decl_type, TypeEnum.NODE, self.parse_declaration)

                    for identifier in node.identifiers:
                        graph_env_v = graph_env_v.bind(identifier, decl_type)

                    env_g = env_g.bind(curr_graph, (graph_type, graph_weight_type, graph_env_v))

        else: # (dlt)
            env_v1, decl_type = self.parse_declaration_list(node, env_v)
            env_v = env_v1

        return (env_v, env_g, decl_type)

    def parse_declaration_list(self, node: ASTNode, env_v: TypeEnv) -> tuple[TypeEnv, TypeEnum]:
        if not isinstance(node, Declaration) or node.is_list is False:
            raise Exception("parse_declaration_list: Implementation error")

        # (dli)
        if not self.parse_dimensions(node.dimension):
            raise TypeCheckError(self.parse_declaration_list, "valid dimension", "invalid dimension")

        resolved_type = resolve_type(node.type)
        if not self.parse_type(resolved_type):
            raise TypeCheckError(self.parse_declaration_list, "valid type", "invalid type")

        for identifier in node.identifiers: # should only be one (what abstract syntax shows)
            env_v = env_v.bind(identifier, resolved_type)

        return (env_v, resolved_type)

    def parse_dimensions(self, dimensions: ASTNode) -> bool:
        well_formed = False
        if dimensions is not None: # (dim)
            kind = self.parse_expression(dimensions, TypeEnv(), TypeEnv(), TypeEnv(), TypeEnv())
            if kind != TypeEnum.NAT:
                return False

            well_formed = True
        else: # (din)
            well_formed = True

        return well_formed

    def parse_graph_declaration(self, node: ASTNode, env_g: TypeEnv, env_i: TypeEnv) -> tuple[TypeEnv, TypeEnv]:
        if not isinstance(node, GraphDecl):
            raise Exception("parse_graph_declaration: Implementation error")

        if len(node.nodes) == 0 and len(node.edges) == 0:
            if node.weight_type is None: # (ghd)
                graph_type = resolve_type(node.graph_type)
                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                env_g = env_g.bind(node.identifier, (graph_type, TypeEnum.UNKNOWN, TypeEnv()))
                env_i = env_i.bind(node.identifier, node.identifier)
            else: # (gdw)
                graph_type = resolve_type(node.graph_type)
                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                weight_type = resolve_type(node.weight_type)
                if not self.parse_type_arithmetic(weight_type):
                    raise TypeCheckError(self.parse_graph_declaration, self.arit_types, weight_type)

                env_g = env_g.bind(node.identifier, (graph_type, weight_type, TypeEnv()))
                env_i = env_i.bind(node.identifier, node.identifier)
        else:
            if node.weight_type is None: # (gdi)
                graph_type = resolve_type(node.graph_type)
                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                env_g1= env_g.bind(node.identifier, (graph_type, TypeEnum.UNKNOWN, TypeEnv()))
                env_i = env_i.bind(node.identifier, node.identifier)

                env_v1 = TypeEnv(); env_a1 = TypeEnv(); env_g2 = env_g1; env_i1 = env_i
                for _node in [*node.nodes, *node.edges]: # doesn't look like rule because (com doesn't have node)
                    env_v1, env_a1, env_g2, env_i1 = self.parse_statement(_node, env_v1, env_a1, env_g2, env_i1,
                                                                          None, node.identifier, False)
                env_g = env_g2
                env_i = env_i1
            else: # (gwi)
                graph_type = resolve_type(node.graph_type)
                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, "valid graph type", "invalid graph type")

                weight_type = resolve_type(node.weight_type)
                if not self.parse_type_arithmetic(weight_type):
                    raise TypeCheckError(self.parse_graph_declaration, self.arit_types, weight_type)

                env_g1 = env_g.bind(node.identifier, (graph_type, weight_type, TypeEnv()))
                env_i = env_i.bind(node.identifier, node.identifier)

                env_v1 = TypeEnv(); env_a1 = TypeEnv(); env_g2 = env_g1; env_i1 = env_i
                for _node in [*node.nodes, *node.edges]: # doesn't look like rule because (com doesn't have node)
                    env_v1, env_a1, env_g2, env_i1 = self.parse_statement(_node, env_v1, env_a1, env_g2, env_i1,
                                                                          None, node.identifier, False)
                env_g = env_g2
                env_i = env_i1

        return env_g, env_i

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

    def expect_type(self, actual: TypeEnum, expected: TypeEnum, rule) -> None:
        """Helper function that throws an error if actual is not the expected type"""

        if actual != expected:
            raise TypeCheckError(rule, expected, actual)


    def expect_type_one_of(self, actual: TypeEnum, expected_types: set, rule) -> None:
        """Helper function that throws an error if actual not one of the expected types"""

        if actual not in expected_types:
            expected = " or ".join(
                t.name for t in expected_types
            ) # makes it print the enum types without their value (which it does by default)
            raise TypeCheckError(rule, expected, actual)

    def expect_type_list_of(self, actual: list[TypeEnum], expected: TypeEnum, rule) -> None:
        """Helper function that throws an error if actual is not a list of the expected type"""

        if not isinstance(actual, list) or all(elem != expected for elem in actual):
            raise TypeCheckError(rule, f"list[{expected}]", actual)

    def expect_list_of_one_type(self, actual: list[TypeEnum], rule) -> None:
        """Helper function that throws an error if actual is a list of more than one type"""

        if len(set(actual)) > 1:
            raise TypeCheckError(rule, "list of one type", actual)

    def reject_type(self, actual: TypeEnum, expected: TypeEnum, rule) -> None:
        """Helper function that throws an error if actual and expected are the same type"""

        if actual == expected:
            raise TypeCheckError(rule, f"not {expected}", actual)
