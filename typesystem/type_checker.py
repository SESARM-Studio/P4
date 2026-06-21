from typesystem.type_env import VariableEnv, AlgorithmEnv, GraphEnv, TypeEnv
from typesystem.data_types import TypeEnum, resolve_type
from parser.ast_builder import *
from exceptions.typesystem_exception import TypeCheckError
from preprocessor.source_map import SourceMap
import sys

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
    arit_order = {
        TypeEnum.NAT:  1,
        TypeEnum.INT:  2,
        TypeEnum.REAL: 3
    }

    def __init__(self, ast: ASTNode, source_map: SourceMap) -> None:
        self.ast = ast
        self.source_map = source_map
        self.attributes: dict = {} # simplification of attributes added by addAttributes

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
                env_v = VariableEnv()
                env_a = AlgorithmEnv()
                env_g = GraphEnv()
                for statement in node.children[:-1]: # does not follow rule, but (com) doesn't exist
                    env_v, env_a, env_g = self.parse_statement(statement, env_v, env_a, env_g, None, None, False)
                well_formed = True
            except TypeCheckError as e:
                self.source_map.print_error(e, e.span[0], e.span[1])
                sys.exit(1)
        else: # (pgn)
            # last element is always expected to be EOF
            end_of_file = node.children[-1]
            if end_of_file.token == "EOF":
                well_formed = True

        return well_formed

    def parse_expression(self,
                         node: ASTNode,
                         env_v: VariableEnv,
                         env_a: AlgorithmEnv,
                         env_g: GraphEnv
                         ) -> TypeEnum:
        kind: TypeEnum | list[TypeEnum] = TypeEnum.UNKNOWN
        match node:
            case Term(type="INTEGER_NUMBER"): # (int)
                kind = TypeEnum.INT

            case Term(type="NATURAL_NUMBER"): # (nat)
                kind = TypeEnum.NAT

            case Term(type="REAL_NUMBER"): # (rea)
                kind = TypeEnum.REAL

            case Term(type="TEXT"): # (str)
                kind = TypeEnum.TEXT

            case Term(type="BOOL_VALUE"): # (boo)
                kind = TypeEnum.BOOL

            case Term(type="IDENTIFIER"):
                if (ident_type := env_v.lookup(node.value)) != TypeEnum.UNKNOWN: # (var1)
                    # check purely to match rule
                    self.reject_type(ident_type, TypeEnum.UNKNOWN, self.parse_expression, node)

                    kind = ident_type
                else: # (var2)
                    graph = env_g.lookup(node.value)
                    self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_expression, node)

                    graph_type, weight_type, node_set = graph
                    self.expect_type_one_of(graph_type, self.graph_types, self.parse_expression, node)
                    self.expect_type_one_of(
                        weight_type, { self.arit_types, TypeEnum.UNKNOWN }, self.parse_expression, node
                    )

            case ExprNode(): # (nex)
                node_expr_type = self.parse_node_expression(node, env_v, env_a, env_g)
                self.expect_type_list_of(node_expr_type, TypeEnum.NODE, self.parse_expression, node)
                kind = node_expr_type # special type (list[TypeEnum])

            case AbsoluteValue(): # (abs)
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)
                self.expect_type_one_of(expr_type, self.arit_types, self.parse_expression, node)
                kind = TypeEnum.NAT

            case Magnitude(): # (mag)
                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)
                if (
                    expr_type is not TypeEnum.TEXT
                    and not self.list_of_one_type(expr_type)
                ):
                    raise TypeCheckError(self.parse_expression, node.span, f"{TypeEnum.TEXT} or list", expr_type)
                kind = TypeEnum.NAT

            case AlgorithmCall(): # (aca)
                algo_type = env_a.lookup(node.identifier)
                self.reject_type(algo_type, TypeEnum.UNKNOWN, self.parse_expression, node)

                arguments = node.arguments if node.arguments is not None else []
                if len(algo_type["parameters"]) != len(arguments):
                    raise TypeCheckError(self.parse_expression, node.span,"same number of parameters and arguments", "not that")

                for param_type, arg in zip(algo_type["parameters"], arguments):
                    arg_type = self.parse_expression(arg, env_v, env_a, env_g)
                    self.expect_type_compatable(arg_type, param_type, self.parse_expression, node)

                kind = algo_type["return_type"]

            case ArrayAccess(): # (arr)
                for index in node.indexes:
                    expr_type = self.parse_expression(index, env_v, env_a, env_g)
                    self.expect_type(expr_type, TypeEnum.NAT, self.parse_expression, node)

                array_type = env_v.lookup(node.identifier)
                self.reject_type(array_type, TypeEnum.UNKNOWN, self.parse_expression, node)

                elem_type = array_type
                list_access_size = 0
                for _ in range(len(node.indexes)):
                    if isinstance(elem_type, list):
                        elem_type = elem_type[0]
                        list_access_size += 1

                if len(node.indexes) > list_access_size:
                    raise TypeCheckError(
                        self.parse_expression, node.span,f"list access in {list_access_size}d list", f"{len(node.indexes)}d list"
                    )

                kind = elem_type

            case IdentifierAccess(identifiers=[i1, i2]) if i2 == "nodes": # (gns)
                graph = env_g.lookup(i1)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_expression, node)

                kind = [TypeEnum.NODE]

            case IdentifierAccess(identifiers=[i1, i2]) if env_v.lookup(i1) == TypeEnum.UNKNOWN and not isinstance(i2, AlgorithmCall): # (gnd)

                graph = env_g.lookup(i1)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_expression, node)

                graph_type, weight_type, node_set = graph
                self.expect_type_one_of(graph_type, self.graph_types, self.parse_expression, node)
                self.expect_type_one_of(weight_type, { TypeEnum.UNKNOWN, *self.arit_types }, self.parse_expression, node)

                self.expect_in_domain(i2, node_set, self.parse_expression, node)

                kind = TypeEnum.NODE

            case IdentifierAccess(identifiers=[i1, i2]) if env_v.lookup(i1) == TypeEnum.UNKNOWN and isinstance(i2, AlgorithmCall):
                graph = env_g.lookup(i1)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_expression, node)

                graph_type, weight_type, node_set = graph
                self.expect_type_one_of(graph_type, self.graph_types, self.parse_expression, node)
                self.expect_type_one_of(weight_type, { TypeEnum.UNKNOWN, *self.arit_types }, self.parse_expression, node)
                if i2.identifier == "toMatrix":
                    if i2.arguments:
                        raise TypeCheckError(self.parse_expression, node.span, "0 arguments", f"{len(i2.arguments)} argument{"s" if len(i2.arguments) > 1 else ""}" )
                    else:
                        if weight_type == TypeEnum.UNKNOWN:
                            kind = [[TypeEnum.NAT]]
                        else:
                            kind = [[weight_type]]
                elif i2.identifier == "fromMatrix":
                    if not i2.arguments or len(i2.arguments) > 1:
                        raise TypeCheckError(self.parse_expression, node.span, "1 argument", f"{0 if not i2.arguments else len(i2.arguments) } arguments" )
                    else:
                        if env_v.lookup(i2.arguments[0].arg1.value) != TypeEnum.UNKNOWN:
                            adjacencyListType = env_v.lookup(i2.arguments[0].arg1.value)[0][0]

                            self.expect_type_one_of(adjacencyListType, self.arit_types, self.parse_expression, node)
                            if weight_type != TypeEnum.UNKNOWN:
                                    self.expect_type_compatable(adjacencyListType, weight_type, self.parse_expression, node)

                        else:
                            if isinstance(i2.arguments[0].arg1, ListExpression):
                                adjacencyListType = self.parse_expression(i2.arguments[0].arg1, env_v, env_a, env_g)[0][0]

                                self.expect_type_one_of(adjacencyListType, self.arit_types, self.parse_expression, node)
                                if weight_type != TypeEnum.UNKNOWN:
                                    self.expect_type_compatable(adjacencyListType, weight_type, self.parse_expression, node)

                                nodeAmount = len(i2.arguments[0].arg1.expressions[0].arg1.expressions)
                                nodes = {chr(ord('a') + i) for i in range(nodeAmount)}
                                
                                env_g = env_g.bind(i1, (graph_type, weight_type, nodes))

                            else:
                                raise TypeCheckError(self.parse_expression, node.span, "ListExpression", i2.arguments[0].arg1.token)

            case IdentifierAccess(identifiers=ids):
                if (graph := env_g.lookup(ids[0])) != TypeEnum.UNKNOWN: # (gxr) with addAttribute
                    graph_type, weight_type, node_set = graph
                    self.expect_type_one_of(graph_type, self.graph_types, self.parse_expression, node)
                    self.expect_type_one_of(
                        weight_type, { *self.arit_types, TypeEnum.UNKNOWN }, self.parse_expression, node
                    )

                    if (
                        len(ids) == 3 and isinstance(ids[2], AlgorithmCall) # G.nodes.addAttribute()
                    ):
                        algorithm_identifier = ids[2].identifier
                        if algorithm_identifier != "addAttribute":
                            raise TypeCheckError(self.parse_expression, node.span, "addAttribute", algorithm_identifier)

                        arguments = ids[2].arguments
                        attribute_type = resolve_type(arguments[0].arg1.value.strip('"'))
                        attribute_identifier = arguments[1].arg1.value

                        # internal algorithm implementation of addAttribute that is built in:
                        self.attributes[attribute_identifier] = attribute_type
                    
                    elif (len(ids) == 3): # G.nodeA.attribute
                        self.expect_in_domain(ids[1], node_set, self.parse_expression, node)
                        if ids[2] not in self.attributes:
                            raise TypeCheckError
                        kind = self.attributes.get(ids[2], TypeEnum.UNKNOWN)

                    else: # type system version of (gxr):
                        expr_type = self.parse_expression(ids[1], env_v, env_a, env_g)
                        self.reject_type(expr_type, TypeEnum.UNKNOWN, self.parse_expression, node)

                        kind = expr_type

                else: # (nxr)
                    node_type = env_v.lookup(ids[0])
                    self.expect_type(node_type, TypeEnum.NODE, self.parse_expression, node)

                    if isinstance(ids[1], str):
                        kind = self.attributes.get(ids[1], TypeEnum.UNKNOWN)
                    else: # type system version of (nxr)
                        expr_type = self.parse_expression(node.identifiers[1], env_v, env_a, env_g)
                        self.reject_type(expr_type, TypeEnum.UNKNOWN, self.parse_expression, node)
                        kind = expr_type

            case ListExpression(): # (arl)
                list_types = []
                for child in node.expressions:
                    list_types.append(self.parse_expression(child, env_v, env_a, env_g))
                self.expect_list_of_one_type(list_types, self.parse_expression, node)
                self.annotate_list_expr(list_types)

                kind = [list_types[0]] if len(list_types) > 0 else TypeEnum.UNKNOWN

            case Expression(operator="+" | "-" | "*" | "/" | "^"): # (ope)
                expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)
                self.expect_type_one_of(expr1_type, self.arit_types, self.parse_expression, node)

                expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)
                self.expect_type_one_of(expr2_type, self.arit_types, self.parse_expression, node)

                kind = self.lub_arit(expr1_type, expr2_type)

            case Expression(operator="%"): # (mod)
                expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)
                self.expect_type_one_of(expr1_type, { TypeEnum.NAT, TypeEnum.INT }, self.parse_expression, node)

                expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)
                self.expect_type_one_of(expr2_type, { TypeEnum.NAT, TypeEnum.INT }, self.parse_expression, node)

                kind = self.lub_arit(expr1_type, expr2_type)

            case Expression(operator="weight of") if "-->" in node.arg1: # (wot)
                ident1n2, ident3 = node.arg1.split("-->")
                ident1, ident2 = ident1n2.split(".")

                graph = env_g.lookup(ident1)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_expression, node)

                graph_type, weight_type, node_set = graph
                self.expect_type(graph_type, TypeEnum.DIGRAPH, self.parse_expression, node)

                self.expect_type_one_of(weight_type, self.arit_types, self.parse_expression, node)

                self.expect_in_domain(ident2, node_set, self.parse_expression, node)
                self.expect_in_domain(ident3, node_set, self.parse_expression, node)

                kind = weight_type

            case Expression(operator="weight of") if "---" in node.arg1: # (woe)
                ident1n2, ident3 = node.arg1.split("---")
                ident1, ident2 = ident1n2.split(".")

                graph = env_g.lookup(ident1)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_expression, node)

                graph_type, weight_type, node_set = graph
                self.expect_type_one_of(
                    graph_type, { TypeEnum.GRAPH, TypeEnum.TREE }, self.parse_expression, node
                )

                self.expect_type_one_of(weight_type, self.arit_types, self.parse_expression, node)

                self.expect_in_domain(ident2, node_set, self.parse_expression, node)
                self.expect_in_domain(ident3, node_set, self.parse_expression, node)

                kind = weight_type

            case Expression(operator="=" | "!=" | "<" | "<=" | ">" | ">="): # (cmp)
                expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)
                self.expect_type_one_of(expr1_type, self.arit_types, self.parse_expression, node)

                expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)
                self.expect_type_one_of(expr2_type, self.arit_types, self.parse_expression, node)

                kind = TypeEnum.BOOL

            case Expression(operator="neg"): # (neg)
                expr_type = self.parse_expression(node.arg1, env_v, env_a, env_g)
                self.expect_type(expr_type, TypeEnum.BOOL, self.parse_expression, node)

                kind = expr_type

            case Expression(operator="and"): # (and)
                expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)
                self.expect_type(expr1_type, TypeEnum.BOOL, self.parse_expression, node)

                expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)
                self.expect_type(expr2_type, TypeEnum.BOOL, self.parse_expression, node)

                kind = expr1_type

            case Expression(operator="or"): # (ore)
                expr1_type = self.parse_expression(node.arg1, env_v, env_a, env_g)
                self.expect_type(expr1_type, TypeEnum.BOOL, self.parse_expression, node)

                expr2_type = self.parse_expression(node.arg2, env_v, env_a, env_g)
                self.expect_type(expr2_type, TypeEnum.BOOL, self.parse_expression, node)

                kind = expr1_type

            case Expression(operator=None | ""): # sometimes the expr just contains another expr
                kind = self.parse_expression(node.arg1, env_v, env_a, env_g)

            case _:
                raise Exception("Unknown expression type")

        setattr(node, "type", kind)
        return kind

    def parse_graph_statement(self,
                              node: ASTNode,
                              env_v: VariableEnv,
                              env_a: AlgorithmEnv,
                              env_g: GraphEnv
                              ) -> GraphEnv:
        if not isinstance(node, GraphStatement):
            raise Exception("parse_graph_expression: Implementation error")

        if not isinstance(node.argument, EdgeDecl):
            if node.operator == "add": # (gan)
                graph = env_g.lookup(node.graph_identifier)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_graph_statement, node)

                env_v1, env_g1, decl_type = self.parse_declaration(
                    node.argument, env_v, env_a, env_g, node.graph_identifier
                )
                env_g = env_g1

                self.expect_type(decl_type, TypeEnum.NODE, self.parse_graph_statement, node)
            else: # (grn)
                graph = env_g.lookup(node.graph_identifier)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_graph_statement, node)

                graph_type, weight_type, node_set = graph
                self.expect_type_one_of(graph_type, self.graph_types, self.parse_graph_statement, node)

                self.expect_type_one_of(weight_type, { *self.arit_types, TypeEnum.UNKNOWN }, self.parse_graph_statement, node)

                ident2 = node.argument
                self.expect_in_domain(ident2, node_set, self.parse_graph_statement, node)
        else: # (are)
            graph = env_g.lookup(node.graph_identifier)
            self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_graph_statement, node)

            expr_type = self.parse_edge_declaration(node.argument, env_v, env_a, env_g, node.graph_identifier)
            self.expect_type(expr_type, TypeEnum.EDGE, self.parse_graph_statement, node)

        return env_g

    def parse_node_expression(self,
                              node: ASTNode,
                              env_v: VariableEnv,
                              env_a: AlgorithmEnv,
                              env_g: GraphEnv
                              ) -> list[TypeEnum]:
        if not isinstance(node, ExprNode):
            raise Exception("parse_node_expression: Implementation error")

        # (ind)
        expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)
        self.expect_type(expr_type, TypeEnum.NODE, self.parse_node_expression, node)

        list_expr_type = [TypeEnum.NODE]
        setattr(node, "type", list_expr_type)
        return list_expr_type

    def parse_edge_declaration(self,
                               node: ASTNode,
                               env_v: VariableEnv,
                               env_a: AlgorithmEnv,
                               env_g: GraphEnv,
                               curr_graph: str | None
                               ) -> TypeEnum:
        if not isinstance(node, EdgeDecl):
            raise Exception("parse_expression: Implementation error")

        kind: TypeEnum = TypeEnum.UNKNOWN

        match node:
            case EdgeDecl(weight=[], direction="---"): # (edu)
                graph = env_g.lookup(curr_graph)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_edge_declaration, node)

                graph_type, weight_type, node_set = graph
                self.expect_type_one_of(graph_type, { TypeEnum.GRAPH, TypeEnum.TREE }, self.parse_edge_declaration, node)
                self.expect_type(weight_type, TypeEnum.UNKNOWN, self.parse_edge_declaration, node)

                identifier1 = (
                    node.initial_node.identifiers[0]
                    if isinstance(node.initial_node, IdentifierAccess)
                    else node.initial_node
                )
                self.expect_in_domain(identifier1, node_set, self.parse_edge_declaration, node)

                for node_obj in node.nodes:
                    node_id = (
                        node_obj.identifiers[0]
                        if isinstance(node_obj, IdentifierAccess)
                        else node_obj
                    )
                    self.expect_in_domain(node_id, node_set, self.parse_edge_declaration, node)

                kind = TypeEnum.EDGE

            case EdgeDecl(weight=[], direction="<--" | "-->" | "<->"): # (edd)
                graph = env_g.lookup(curr_graph)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_edge_declaration, node)

                graph_type, weight_type, node_set = graph
                self.expect_type(graph_type, TypeEnum.DIGRAPH, self.parse_edge_declaration, node)
                self.expect_type(weight_type, TypeEnum.UNKNOWN, self.parse_edge_declaration, node)

                identifier1 = (
                    node.initial_node.identifiers[0]
                    if isinstance(node.initial_node, IdentifierAccess)
                    else node.initial_node
                )
                self.expect_in_domain(identifier1, node_set, self.parse_edge_declaration, node)

                for node_obj in node.nodes:
                    node_id = (
                        node_obj.identifiers[0]
                        if isinstance(node_obj, IdentifierAccess)
                        else node_obj
                    )
                    self.expect_in_domain(node_id, node_set, self.parse_edge_declaration, node)

                kind = TypeEnum.EDGE

            case EdgeDecl(weight=weights, direction="---") if len(weights) > 0: # (ewu)
                curr_graph_type = env_g.lookup(curr_graph)
                self.reject_type(curr_graph_type, TypeEnum.UNKNOWN, self.parse_edge_declaration, node)

                graph_type, weight_type, node_set = curr_graph_type
                self.expect_type_one_of(graph_type, { TypeEnum.GRAPH, TypeEnum.TREE }, self.parse_edge_declaration, node)
                self.expect_type_one_of(weight_type, self.arit_types, self.parse_edge_declaration, node)

                identifier1 = (
                    node.initial_node.identifiers[0]
                    if isinstance(node.initial_node, IdentifierAccess)
                    else node.initial_node
                )
                self.expect_in_domain(identifier1, node_set, self.parse_edge_declaration, node)

                if len(node.nodes) != len(node.weight):
                    raise TypeCheckError(self.parse_edge_declaration, node.span,
                                         "matching number of nodes and weights",
                                         "uneven amount of nodes and weigths")

                for node_obj, weight in zip(node.nodes, node.weight):
                    node_id = (
                        node_obj.identifiers[0]
                        if isinstance(node_obj, IdentifierAccess)
                        else node_obj
                    )
                    self.expect_in_domain(node_id, node_set, self.parse_edge_declaration, node)

                    expr_type = self.parse_expression(weight, env_v, env_a, env_g)
                    self.expect_type_compatable(expr_type, weight_type, self.parse_edge_declaration, node)

                kind = TypeEnum.EDGE

            case EdgeDecl(weight=weights, direction="<--" | "-->" | "<->") if len(weights) > 0: # (ewd)
                curr_graph_type = env_g.lookup(curr_graph)
                self.reject_type(curr_graph_type, TypeEnum.UNKNOWN, self.parse_edge_declaration, node)

                graph_type, weight_type, node_set = curr_graph_type
                self.expect_type(graph_type, TypeEnum.DIGRAPH, self.parse_edge_declaration, node)
                self.expect_type_one_of(weight_type, self.arit_types, self.parse_edge_declaration, node)

                identifier1 = (
                    node.initial_node.identifiers[0]
                    if isinstance(node.initial_node, IdentifierAccess)
                    else node.initial_node
                )
                self.expect_in_domain(identifier1, node_set, self.parse_edge_declaration, node)

                if len(node.nodes) != len(node.weight):
                    raise TypeCheckError(self.parse_edge_declaration, node.span,
                                         "matching number of nodes and weights",
                                         "uneven amount of nodes and weigths")

                for node_obj, weight in zip(node.nodes, node.weight):
                    node_id = (
                        node_obj.identifiers[0]
                        if isinstance(node_obj, IdentifierAccess)
                        else node_obj
                    )
                    self.expect_in_domain(node_id, node_set, self.parse_edge_declaration, node)

                    expr_type = self.parse_expression(weight, env_v, env_a, env_g)
                    self.expect_type_compatable(expr_type, weight_type, self.parse_edge_declaration, node)

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
                        env_v: VariableEnv,
                        env_a: AlgorithmEnv,
                        env_g: GraphEnv,
                        curr_algo: str | None,
                        curr_graph: str | None,
                        inside_loop: bool
                        ) -> tuple[VariableEnv, AlgorithmEnv, GraphEnv]:
        match node:
            # case S NL S # (com) # doesnt exist and is just a list on the node noew

            case DeclarationInit(is_list=False): # (dcl)
                env_v1, env_g1, decl_type = self.parse_declaration(node, env_v, env_a, env_g, curr_graph)

                expr_type = self.parse_expression(node.expression[0], env_v, env_a, env_g)
                self.expect_type_compatable(expr_type, decl_type, self.parse_statement, node)

                env_v = env_v1
                env_g = env_g1

            case Assignment(identifiers=[I]) if not isinstance(I, ArrayAccess): # (ass)
                ident_type = TypeEnum.UNKNOWN
                ident_type = env_v.lookup(node.identifiers[0])

                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)
                self.expect_type_compatable(expr_type, ident_type, self.parse_statement, node)

            case Assignment(identifiers=ids) if len(ids) == 3: # 3 = I.I.X # (aas)
                identifier_access_type = TypeEnum.UNKNOWN
                graph = env_g.lookup(ids[0])
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_statement, node)
                graph_type, weight_type, node_set = graph

                self.expect_in_domain(ids[1], node_set, self.parse_statement, node)

                if ids[2] not in self.attributes:
                    raise TypeCheckError
                attribute_type = self.attributes.get(ids[2], TypeEnum.UNKNOWN)

                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)
                self.expect_type_compatable(expr_type, attribute_type, self.parse_statement, node)

            case Assignment(identifiers=ids) if len(ids) == 2: # 2 = I.X # (aas)
                identifier_access_type = TypeEnum.UNKNOWN
                # if string : I.X cannot be parsed to expression as seen in type system
                if isinstance(ids[0], str) and isinstance(ids[1], str):
                    identifier_access_type = self.attributes.get(ids[1], TypeEnum.UNKNOWN) # attribute access
                else:
                    identifier_access_type = self.parse_expression(node.identifiers[0], env_v, env_a, env_g)
                    self.reject_type(identifier_access_type, TypeEnum.UNKNOWN, self.parse_statement, node)

                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)
                self.expect_type_compatable(expr_type, identifier_access_type, self.parse_statement, node)

            case Assignment(identifiers=ids) if len(ids) == 1: # (ara)
                array_access_type = self.parse_expression(node.identifiers[0], env_v, env_a, env_g)
                self.reject_type(array_access_type, TypeEnum.UNKNOWN, self.parse_statement, node)

                expr_type = self.parse_expression(node.expression, env_v, env_a, env_g)
                self.expect_type_compatable(expr_type, array_access_type, self.parse_statement, node)

            case DeclarationInit(is_list=True): # (las)
                env_v1, decl_type = self.parse_declaration_list(node, env_v, env_a, env_g)
                for expr in node.expression:
                    expr_type = self.parse_expression(expr, env_v, env_a, env_g)
                    self.expect_type_compatable(expr_type, decl_type, self.parse_statement, node)

                env_v = env_v1

            case Declaration() | NodeDecl(): # (std)
                env_v1, env_g1, decl_type = self.parse_declaration(node, env_v, env_a, env_g, curr_graph)
                env_v = env_v1
                env_g = env_g1

            case IfStatement() if len(node.else_statements) == 0: # (ift)
                if_kind = self.parse_expression(node.condition, env_v, env_a, env_g)
                self.expect_type(if_kind, TypeEnum.BOOL, self.parse_statement, node)

                env_v1 = env_v.enter_scope()
                env_a1 = env_a.enter_scope()
                env_g1 = env_g.enter_scope()
                for statement in node.then_statements:
                    env_v1, env_a1, env_g1 = self.parse_statement(statement, env_v1, env_a1, env_g1,
                                                                  curr_algo, curr_graph, inside_loop)
                env_v1 = env_v1.exit_scope()
                env_a1 = env_a1.exit_scope()
                env_g1 = env_g1.exit_scope()

                env_g = env_g1

            case IfStatement() if len(node.else_statements) != 0: # (ife)
                if_kind = self.parse_expression(node.condition, env_v, env_a, env_g)
                self.expect_type(if_kind, TypeEnum.BOOL, self.parse_statement, node)

                env_v1 = env_v.enter_scope()
                env_a1 = env_a.enter_scope()
                env_g1 = env_g.enter_scope()
                for statement in node.then_statements:
                    env_v1, env_a1, env_g1 = self.parse_statement(statement, env_v1, env_a1, env_g1,
                                                                  curr_algo, curr_graph, inside_loop)
                env_v1 = env_v1.exit_scope()
                env_a1 = env_a1.exit_scope()
                env_g1 = env_g1.exit_scope()

                env_v2 = env_v.enter_scope()
                env_a2 = env_a.enter_scope()
                env_g2 = env_g.enter_scope()
                for statement in node.else_statements:
                    env_v2, env_a2, env_g2 = self.parse_statement(statement, env_v2, env_a2, env_g2,
                                                                  curr_algo, curr_graph, inside_loop)
                env_v2 = env_v2.exit_scope()
                env_a2 = env_a2.exit_scope()
                env_g2 = env_g2.exit_scope()

                env_g.current_scope = GraphEnv.merge(env_g1.current_scope, env_g2.current_scope)

            case WhileStatement(): # (whl)
                cond_kind = self.parse_expression(node.condition, env_v, env_a, env_g)
                self.expect_type(cond_kind, TypeEnum.BOOL, self.parse_statement, node)

                env_v1 = env_v.enter_scope()
                env_a1 = env_a.enter_scope()
                env_g1 = env_g.enter_scope()
                for statement in node.statements:
                    env_v1, env_a1, env_g1 = self.parse_statement(statement, env_v1, env_a1, env_g1,
                                                                  curr_algo, curr_graph, inside_loop=True)
                env_v1 = env_v1.exit_scope()
                env_a1 = env_a1.exit_scope()
                env_g1 = env_g1.exit_scope()

                env_g = env_g1 # only update env_g as rule states

            case RepeatStatement(): # (rpt)
                repeat_expression = self.parse_expression(node.repeat_expression, env_v, env_a, env_g)
                self.expect_type(repeat_expression, TypeEnum.NAT, self.parse_statement, node)

                env_v1 = env_v.enter_scope()
                env_a1 = env_a.enter_scope()
                env_g1 = env_g.enter_scope()
                for statement in node.repeat_statements:
                    env_v1, env_a1, env_g1 = self.parse_statement(statement, env_v1, env_a1, env_g1,
                                                                  curr_algo, curr_graph, inside_loop=True)
                env_v1 = env_v1.exit_scope()
                env_a1 = env_a1.exit_scope()
                env_g1 = env_g1.exit_scope()

                env_g = env_g1 # only update env_g as rule states

            case ForEachNormal(): # (for)
                iterable_type = self.parse_expression(node.iterable, env_v, env_a, env_g)
                self.expect_list_of_one_type(iterable_type, self.parse_statement, node)

                elem_type = iterable_type[0]
                env_v1 = env_v.enter_scope().bind(node.loop_identifier, elem_type)
                env_a1 = env_a.enter_scope()
                env_g1 = env_g.enter_scope()
                for statement in node.statements:
                    env_v1, env_a1, env_g1 = self.parse_statement(statement, env_v1, env_a1, env_g1,
                                                                  curr_algo, curr_graph, inside_loop=True)
                env_v1 = env_v1.exit_scope()
                env_a1 = env_a1.exit_scope()
                env_g1 = env_g1.exit_scope()

                env_g = env_g1 # only update env_g as rule states

            case ForEachEdge(weight_identifier=None): # (fre)
                graph = env_g.lookup(node.graph_identifier)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_statement, node)

                env_v1 = VariableEnv(current_scope=self.parse_edge_loop(node.edge, TypeEnv()))

                env_v2 = env_v1.enter_scope()
                env_a1 = env_a.enter_scope()
                env_g1 = env_g.enter_scope()
                for statement in node.statements:
                    env_v2, env_a1, env_g1 = self.parse_statement(statement, env_v2, env_a1, env_g1,
                                                                  curr_algo, curr_graph, inside_loop=True)
                env_v2 = env_v2.exit_scope()
                env_a1 = env_a1.exit_scope()
                env_g1 = env_g1.exit_scope()

                env_g = env_g1 # only update env_g as rule states

            case ForEachEdge() if node.weight_identifier is not None: # (frw)
                graph = env_g.lookup(node.graph_identifier)
                self.reject_type(graph, TypeEnum.UNKNOWN, self.parse_expression, node)

                graph_type, weight_type, node_set = graph
                self.expect_type_one_of(graph_type, self.graph_types, self.parse_statement, node)
                self.expect_type_one_of(weight_type, self.arit_types, self.parse_statement, node)

                env_v1 = VariableEnv(current_scope=self.parse_edge_loop(node.edge, TypeEnv()))

                env_v2 = env_v1.enter_scope().bind(node.weight_identifier, weight_type)
                env_a1 = env_a.enter_scope()
                env_g1 = env_g.enter_scope()
                for statement in node.statements:
                    env_v2, env_a1, env_g1 = self.parse_statement(statement, env_v2, env_a1, env_g1,
                                                                  curr_algo, curr_graph, inside_loop=True)
                env_v2 = env_v2.exit_scope()
                env_a1 = env_a1.exit_scope()
                env_g1 = env_g1.exit_scope()

                env_g = env_g1 # only update env_g as rule states

            case ReturnStatement(): # (ret)
                if curr_algo is None:
                    raise TypeCheckError(self.parse_statement, node.span, "inside function", "outside function")

                algorithm = env_a.lookup(curr_algo)
                return_type = self.parse_expression(node.expression, env_v, env_a, env_g)
                self.expect_type_compatable(return_type, algorithm["return_type"], self.parse_statement, node)

            case Algorithm(): # (alg)
                env_a1 = self.parse_algorithm(node, env_v, env_a, env_g)
                env_a = env_a1

            case Expression(): # (exp)
                self.parse_expression(node, env_v, env_a, env_g)

            case LoopModifier(): # (lop)
                self.parse_loop_modifier(node, inside_loop)

            case GraphDecl(): # (grt)
                env_g1 = self.parse_graph_declaration(node, env_v, env_a, env_g)
                env_g = env_g1

            case EdgeDecl(): # (edc)
                edge_decl_type = self.parse_edge_declaration(node, env_v, env_a, env_g, curr_graph)
                self.expect_type(edge_decl_type, TypeEnum.EDGE, self.parse_expression, node)

            case GraphStatement(): # (gst)
                env_g1 = self.parse_graph_statement(node, env_v, env_a, env_g)
                env_g = env_g1

            case DisplayStatement(): # (dis)
                display_expr = self.parse_expression(node.expression, env_v, env_a, env_g)
                self.reject_type(display_expr, TypeEnum.UNKNOWN, self.parse_statement, node)

            case _:
                raise Exception(f"Unknown statement type")

        return env_v, env_a, env_g

    def parse_loop_modifier(self, node: ASTNode, inside_loop: bool) -> bool:
        if not isinstance(node, LoopModifier):
            raise Exception("parse_loop_modifier: Implementation error")

        # (stp)
        if inside_loop is False:
            raise TypeCheckError(self.parse_loop_modifier, node.span, True, inside_loop)

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

    def parse_algorithm(self,
                        node: ASTNode,
                        env_v: VariableEnv,
                        env_a: AlgorithmEnv,
                        env_g: GraphEnv
                        ) -> AlgorithmEnv:
        if not isinstance(node, Algorithm):
            raise Exception("parse_algorithm: Implementation error")

        if node.return_type is None: # (alg)
            if env_v.current_scope.in_domain(node.identifier):
                raise TypeCheckError(self.parse_algorithm, node.span, "not in domain", "double declaration")
            if env_a.current_scope.in_domain(node.identifier):
                raise TypeCheckError(self.parse_algorithm, node.span, "not in domain", "double declaration")
            if env_g.current_scope.in_domain(node.identifier):
                raise TypeCheckError(self.parse_algorithm, node.span, "not in domain", "double declaration")

            parameter_types = []

            env_vi = env_v.enter_scope()
            scope_a = env_a.enter_scope()
            env_gi = env_g.enter_scope()
            for param in node.parameters:
                env_vi, env_gi, decl_type = self.parse_declaration(param, env_vi, scope_a, env_gi, None)
                parameter_types.append(decl_type)

            env_a1 = env_a.bind(node.identifier, {"parameters": tuple(parameter_types),
                                                  "return_type": TypeEnum.UNKNOWN})

            env_v1 = env_vi
            env_a2 = env_a1
            env_g1 = env_gi
            for statement in node.statements:
                env_v1, env_a2, env_g1 = self.parse_statement(statement, env_v1, env_a2, env_g1,
                                                              node.identifier, None, False)
            env_v1 = env_v1.exit_scope()
            env_a2 = env_a2.exit_scope()
            env_g1 = env_g1.exit_scope()

            env_a = env_a1
        else: # (alr)
            if env_v.current_scope.in_domain(node.identifier):
                raise TypeCheckError(self.parse_algorithm, node.span, "not in domain", "double declaration")
            if env_a.current_scope.in_domain(node.identifier):
                raise TypeCheckError(self.parse_algorithm, node.span, "not in domain", "double declaration")
            if env_g.current_scope.in_domain(node.identifier):
                raise TypeCheckError(self.parse_algorithm, node.span, "not in domain", "double declaration")

            parameter_types = []
            return_type = resolve_type(node.return_type)

            env_vi = env_v.enter_scope()
            scope_a = env_a.enter_scope()
            env_gi = env_g.enter_scope()
            for param in node.parameters:
                env_vi, env_gi, decl_type = self.parse_declaration(param, env_vi, scope_a, env_gi, None)
                parameter_types.append(decl_type)

            if not self.parse_type(return_type):
                raise TypeCheckError(self.parse_statement, node.span, "valid return type", "Invalid return type")

            env_a1 = env_a.bind(node.identifier, {"parameters": tuple(parameter_types),
                                                  "return_type": return_type})

            env_v1 = env_vi
            env_a2 = env_a1
            env_g1 = env_gi
            for statement in node.statements:
                env_v1, env_a2, env_g1 = self.parse_statement(statement, env_v1, env_a2, env_g1,
                                                              node.identifier, None, False)
            env_v1 = env_v1.exit_scope()
            env_a2 = env_a2.exit_scope()
            env_g1 = env_g1.exit_scope()

            env_a = env_a1

        return env_a

    def parse_declaration(self,
                          node: ASTNode,
                          env_v: VariableEnv,
                          env_a: AlgorithmEnv,
                          env_g: GraphEnv,
                          curr_graph: str | None
                          ) -> tuple[VariableEnv, GraphEnv, TypeEnum]:
        if not isinstance(node, (Declaration, Parameter, NodeDecl)):
            raise Exception("parse_declaration: Implementation error")

        decl_type = TypeEnum.UNKNOWN
        # The parameter class is also treated as declaration but does not have is_list attr
        if getattr(node, "is_list", False) is False:
            if isinstance(node, Parameter): # parameter is not a list type like normal decl's, so it is converted
                setattr(node, "identifiers", [node.identifier])

            if self.parse_type_arithmetic(node.type): # (dca)
                decl_type = resolve_type(node.type)

                for identifier in node.identifiers:
                    if env_v.current_scope.in_domain(identifier):
                        raise TypeCheckError(self.parse_declaration, node.span, "not in domain", "double declaration")
                    if env_a.current_scope.in_domain(identifier):
                        raise TypeCheckError(self.parse_declaration, node.span, "not in domain", "double declaration")
                    if env_g.current_scope.in_domain(identifier):
                        raise TypeCheckError(self.parse_declaration, node.span, "not in domain", "double declaration")

                    env_v = env_v.bind(identifier, decl_type)

            else:
                if env_g.lookup(curr_graph) == TypeEnum.UNKNOWN: # (dti)
                    decl_type = resolve_type(node.type)

                    for identifier in node.identifiers:
                        if env_v.current_scope.in_domain(identifier):
                            raise TypeCheckError(self.parse_declaration, node.span, "not in domain", "double declaration")
                        if env_a.current_scope.in_domain(identifier):
                            raise TypeCheckError(self.parse_declaration, node.span, "not in domain", "double declaration")
                        if env_g.current_scope.in_domain(identifier):
                            raise TypeCheckError(self.parse_declaration, node.span, "not in domain", "double declaration")

                        env_v = env_v.bind(identifier, decl_type)

                    if not self.parse_type(decl_type):
                        raise TypeCheckError(self.parse_declaration, node.span, "valid type", "invalid type")

                    self.expect_type_one_of(
                        decl_type, { TypeEnum.NODE, TypeEnum.TEXT, TypeEnum.BOOL }, self.parse_declaration, node
                    )
                else: # (dtg)
                    graph_type, weight_type, node_set = env_g.lookup(curr_graph)
                    self.expect_type_one_of(graph_type, self.graph_types, self.parse_statement, node)
                    self.expect_type_one_of(weight_type, { *self.arit_types, TypeEnum.UNKNOWN }, self.parse_statement, node)

                    decl_type = resolve_type(node.type)

                    if not self.parse_type(decl_type):
                        raise TypeCheckError(self.parse_declaration, node.span, "valid type", "invalid type")

                    self.expect_type(decl_type, TypeEnum.NODE, self.parse_declaration, node)

                    for identifier in node.identifiers:
                        if self.reject_in_domain(identifier, node_set, self.parse_declaration, node):
                            raise TypeCheckError(self.parse_declaration, node.span, "not in domain", "double declaration")

                    env_g = env_g.update_node_set(curr_graph, set(node.identifiers))

        else: # (dlt)
            env_v1, decl_type = self.parse_declaration_list(node, env_v, env_a, env_g)
            env_v = env_v1

        return (env_v, env_g, decl_type)

    def parse_declaration_list(self,
                               node: ASTNode,
                               env_v: VariableEnv,
                               env_a: AlgorithmEnv,
                               env_g: GraphEnv
                               ) -> tuple[VariableEnv, TypeEnum]:
        if not isinstance(node, (Declaration, DeclarationInit)) or node.is_list is False:
            raise Exception("parse_declaration_list: Implementation error")

        # (dli)
        if not self.parse_dimensions(node.dimension):
            raise TypeCheckError(self.parse_declaration_list, node.span, "valid dimension", "invalid dimension")

        resolved_type = resolve_type(node.type)
        if not self.parse_type(resolved_type):
            raise TypeCheckError(self.parse_declaration_list, node.span, "valid type", "invalid type")

        dimension_type = resolved_type
        if node.dimension is not None:
            for _ in range(int(node.dimension.value)):
                dimension_type = [dimension_type]
        else:
            dimension_type = [dimension_type] # if 1d list notation is not used

        # abstract syntax only allows one identifier for list declarations
        if env_v.current_scope.in_domain(node.identifiers[0]):
            raise TypeCheckError(self.parse_declaration_list, node.span, "not in domain", "double declaration")
        if env_a.current_scope.in_domain(node.identifiers[0]):
            raise TypeCheckError(self.parse_declaration_list, node.span, "not in domain", "double declaration")
        if env_g.current_scope.in_domain(node.identifiers[0]):
            raise TypeCheckError(self.parse_declaration_list, node.span, "not in domain", "double declaration")

        env_v = env_v.bind(node.identifiers[0], dimension_type)

        return (env_v, dimension_type)

    def parse_dimensions(self, node: ASTNode) -> bool:
        if not isinstance(node, Term) and node is not None: # the dimension node is impl as Term
            raise Exception("parse_dimensions: Implementation error")

        well_formed = False
        if node is not None: # (dim)
            kind = self.parse_expression(node, VariableEnv(), AlgorithmEnv(), GraphEnv())
            self.expect_type(kind, TypeEnum.NAT, self.parse_dimensions, node)
            well_formed = True
        else: # (din)
            well_formed = True

        return well_formed

    def parse_graph_declaration(self,
                                node: ASTNode,
                                env_v: VariableEnv,
                                env_a: AlgorithmEnv,
                                env_g: GraphEnv
                                ) -> GraphEnv:
        if not isinstance(node, GraphDecl):
            raise Exception("parse_graph_declaration: Implementation error")

        match node:
            case GraphDecl(nodes=[], edges=[], weight_type=None): # (ghd)
                graph_type = resolve_type(node.graph_type)
                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "valid graph type", "invalid graph type")

                if env_v.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "not in domain", "double declaration")
                if env_a.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "not in domain", "double declaration")
                if env_g.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "not in domain", "double declaration")

                env_g = env_g.bind(node.identifier, (graph_type, TypeEnum.UNKNOWN, set()))

            case GraphDecl(nodes=[], edges=[]): # (gdw)
                graph_type = resolve_type(node.graph_type)
                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "valid graph type", "invalid graph type")

                weight_type = resolve_type(node.weight_type)
                if not self.parse_type_arithmetic(weight_type):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, self.arit_types, weight_type)

                if env_v.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration, node.span,"not in domain", "double declaration")
                if env_a.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "not in domain", "double declaration")
                if env_g.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "not in domain", "double declaration")

                env_g = env_g.bind(node.identifier, (graph_type, weight_type, set()))

            case GraphDecl(nodes=nodes, edges=edges, weight_type=None) if len(nodes) > 0 or len(edges) > 0: # (gdi)
                graph_type = resolve_type(node.graph_type)
                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "valid graph type", "invalid graph type")

                if env_v.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "not in domain", "double declaration")
                if env_a.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "not in domain", "double declaration")
                if env_g.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration, node.span, "not in domain", "double declaration")

                env_g1 = env_g.bind(node.identifier, (graph_type, TypeEnum.UNKNOWN, set()))

                env_v1 = env_v.enter_scope()
                env_a1 = env_a.enter_scope()
                env_g2 = env_g1.enter_scope()
                for _node in [*node.nodes, *node.edges]:
                    env_v1, env_a1, env_g2 = self.parse_statement(_node, env_v1, env_a1, env_g2,
                                                                None, node.identifier, False)
                env_v1 = env_v1.exit_scope()
                env_a1 = env_a1.exit_scope()
                env_g2 = env_g2.exit_scope()

                env_g = env_g2

            case GraphDecl(nodes=nodes, edges=edges) if len(nodes) > 0 or len(edges) > 0: # (gwi)
                graph_type = resolve_type(node.graph_type)
                if not self.parse_graph_type(graph_type):
                    raise TypeCheckError(self.parse_graph_declaration,node.span, "valid graph type", "invalid graph type")

                weight_type = resolve_type(node.weight_type)
                if not self.parse_type_arithmetic(weight_type):
                    raise TypeCheckError(self.parse_graph_declaration,node.span, self.arit_types, weight_type)

                if env_v.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration,node.span, "not in domain", "double declaration")
                if env_a.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration,node.span, "not in domain", "double declaration")
                if env_g.current_scope.in_domain(node.identifier):
                    raise TypeCheckError(self.parse_graph_declaration,node.span, "not in domain", "double declaration")

                env_g1 = env_g.bind(node.identifier, (graph_type, weight_type, set()))

                env_v1 = env_v.enter_scope()
                env_a1 = env_a.enter_scope()
                env_g2 = env_g1.enter_scope()
                for _node in [*node.nodes, *node.edges]:
                    env_v1, env_a1, env_g2 = self.parse_statement(_node, env_v1, env_a1, env_g2,
                                                                None, node.identifier, False)
                env_v1 = env_v1.exit_scope()
                env_a1 = env_a1.exit_scope()
                env_g2 = env_g2.exit_scope()

                env_g = env_g2

        return env_g

    def lub_arit(self, type_1: TypeEnum, type_2: TypeEnum) -> TypeEnum:
        """Least upper bound helper function""" # explicit on purpose

        _type_1 = self.arit_order.get(type_1, None)
        _type_2 = self.arit_order.get(type_2, None)

        if _type_1 is None or _type_2 is None:
            raise Exception("Types must be arithmetic types")

        if _type_1 == _type_2:
            return type_1
        elif _type_1 < _type_2:
            return type_2
        else: # _type_2 < _type_1
            return type_1

    def expect_type(self, actual: TypeEnum, expected: TypeEnum, rule, node) -> None:
        """Helper function that throws an error if actual is not the expected type"""

        if actual != expected:
            raise TypeCheckError(rule, node.span, expected, actual)

    def expect_type_compatable(self, actual: TypeEnum, expected: TypeEnum, rule, node) -> None:
        """Helper function throws an error if actual and expected are not compatable types"""

        if isinstance(expected, list) and isinstance(actual, list):
            self.expect_type_compatable(actual[0], expected[0], rule, node) # list types only have one element
            return

        if isinstance(expected, list) or isinstance(actual, list): # one is a list the other is not
            raise TypeCheckError(rule, node.span, f"compatable with {expected}", actual)

        _expected = self.arit_order.get(expected, None)
        _actual = self.arit_order.get(actual, None)

        if _expected is not None and _actual is not None:
            # arithmetic types: allow widening/equal types
            if _actual > _expected: # can cast to wider type but not vice versa
                raise TypeCheckError(rule, node.span, f"compatable with {expected}", actual)

        elif expected != actual: # compare normally
            raise TypeCheckError(rule, node.span, f"compatable with {expected}", actual)

    def expect_type_one_of(self, actual: TypeEnum, expected_types: set, rule, node) -> None:
        """Helper function that throws an error if actual not one of the expected types"""
        if not isinstance(actual, TypeEnum):
            raise TypeCheckError(rule, node.span,TypeEnum, actual)

        if actual not in expected_types:
            expected = " or ".join(
                t.name for t in expected_types
            ) # makes it print the enum types without their value (which it does by default)
            raise TypeCheckError(rule, node.span, expected, actual)

    def expect_type_list_of(self, actual: list[TypeEnum], expected: TypeEnum, rule, node) -> None:
        """Helper function that throws an error if actual is not a list of the expected type"""

        if not isinstance(actual, list) or all(elem != expected for elem in actual):
            raise TypeCheckError(rule, node.span, f"list[{expected}]", actual)

    def expect_list_of_one_type(self, actual: list[TypeEnum], rule, node) -> None:
        """Helper function that throws an error if actual is a list of more than one type"""

        if not self.list_of_one_type(actual):
            raise TypeCheckError(rule, node.span, "list of one type", actual)

    def list_of_one_type(self, actual: TypeEnum | list[TypeEnum]) -> bool:
        """Returns true if actual is a list and every element has the same type (or is compatable)"""

        if not isinstance(actual, list):
            return False

        if len(actual) == 0:
            return True # if there is no elements it is of the same type

        first_type = actual[0] # expect all other types to match this

        is_nested_list = isinstance(first_type, list)
        if is_nested_list:
            return all(
                isinstance(elem, list) and self.list_of_one_type(elem)
                for elem in actual
            )

        if first_type in self.arit_types:
            return all( # arithmetic types: allow widening/equal types
                not isinstance(elem, list) and elem in self.arit_types
                for elem in actual[1:]
            )

        # non arithmetic types: require exact match
        return all(x == first_type for x in actual[1:])

    def annotate_list_expr(self, list_expr: list[TypeEnum]) -> None:
        """Annotates list of types and if arithmetic convert to least upper bound"""

        if not isinstance(list_expr, list):
            return

        if len(list_expr) == 0:
            return

        first_type = list_expr[0]

        is_nested_list = isinstance(first_type, list)
        if is_nested_list:
            for elem in list_expr:
                if isinstance(elem, list):
                    self.annotate_list_expr(elem)

            for elem in list_expr:
                if not isinstance(elem, list):
                    setattr(elem, "type", list_expr[0])
        elif first_type in self.arit_types:
            least_upper_bound = first_type
            for elem in list_expr[1:]:
                least_upper_bound = self.lub_arit(least_upper_bound, elem)

            for elem in list_expr:
                setattr(elem, "type", least_upper_bound)
            setattr(list_expr[0], "type", least_upper_bound)

    def expect_in_domain(self, identifier: str, domain: set, rule, node):
        """Helper function that throws an error if an identifier is not in the domain"""

        if identifier not in domain:
            raise TypeCheckError(rule, node.span, f"in {domain}", identifier)

    def reject_type(self, actual: TypeEnum, expected: TypeEnum, rule, node) -> None:
        """Helper function that throws an error if actual and expected are the same type"""

        if actual == expected:
            raise TypeCheckError(rule, node.span, f"not {expected}", actual)

    def reject_in_domain(self, identifier: str, domain: set, rule, node):
        """Helper function that throws an error if an identifier is in the domain"""

        if identifier in domain:
            raise TypeCheckError(rule, node.span, f"not in {domain}", identifier)
