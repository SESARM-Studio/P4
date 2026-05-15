from typesystem.type_checker import TypeChecker
from parser.ast_builder import *
# this will maybe be split up into each category

### AST tree helpers ###
def make_term(_type=None, value=None, token="Term"):
    term = Term(token)
    term.type = _type
    term.value = value
    return term

def make_expression(operator=None, arg1=None, arg2=None, token="Expression"):
    expr = Expression(token)
    expr.operator = operator
    expr.arg1 = arg1
    expr.arg2 = arg2
    return expr

########################

def test_type_system_pgn():
    # Arrange
    expected = True
    ast = ASTNode("PROGRAM", [
        ASTNode("EOF", value="'$'")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_pgm():
    # Arrange
    expected = True

    ast = ASTNode("PROGRAM", [
        make_expression(
            arg1=make_term("NATURAL_NUMBER", "5")
        ),
        ASTNode("EOF", value="'$'")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_abs():
    # Arrange
    expected = True

    absolute_value_node = AbsoluteValue("AbsoluteValue")
    absolute_value_node.expression = make_expression(
        arg1=make_term("NATURAL_NUMBER", "3")
    )

    ast = ASTNode("PROGRAM", [
        make_expression(
            arg1=absolute_value_node
        ),
        ASTNode("EOF", value="'$'")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_mag():
    # Arrange
    expected = True

    magnitude_node = Magnitude("Magnitude")
    magnitude_node.expression = make_expression(
        arg1=make_term("TEXT", "\"hello\"")
    )

    ast = ASTNode("PROGRAM", [
        make_expression(
            arg1=magnitude_node
        ),
        ASTNode("EOF", value="'$'")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_aca():
    # Arrange
    expected = True

    param = Parameter("Parameter")
    param.type = "nat"
    param.identifier = "yes"

    algo = Algorithm("Algorithm")
    algo.identifier = "exp"
    algo.parameters = [
        param
    ]
    algo.statements = [
        make_expression(
            arg1=make_term("BOOL_VALUE", "false")
        )
    ]

    algo_call = AlgorithmCall("AlgorithmCall")
    algo_call.identifier = "exp"
    algo_call.arguments = [
        make_expression(
            arg1=make_term("NATURAL_NUMBER", "2")
        )
    ]

    ast = ASTNode("PROGRAM", [
        algo,
        make_expression(
            arg1=algo_call
        ),
        ASTNode("EOF", value="'$'")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_arr():
    # Arrange
    expected = True

    list_expr = ListExpression("ListExpression")
    list_expr.expressions = [
        make_expression(
            arg1=make_term("INTEGER_NUMBER", "-1")
        ),
        make_expression(
            arg1=make_term("INTEGER_NUMBER", "1")
        )
    ]

    decl_init_node = DeclarationInit("DeclarationInit")
    decl_init_node.is_list = True
    decl_init_node.dimension = make_term("NATURAL_NUMBER", "1")
    decl_init_node.identifiers = ["mrts"]
    decl_init_node.type = "int"
    decl_init_node.expression = [list_expr]

    array_access = ArrayAccess("ArrayAccess")
    array_access.identifier = "mrts"
    array_access.indexes = [
        make_expression(
            arg1=make_term("NATURAL_NUMBER", "1")
        )
    ]

    ast = ASTNode("PROGRAM", [
        decl_init_node,
        make_expression(
            arg1=array_access
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_nac():
    # Arrange
    expected = True

    node0 = NodeDecl("NodeDecl")
    node0.identifiers = ["ez"]

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "tree"
    graph_decl_node.identifier = "ze"
    graph_decl_node.weight_type = "int"
    graph_decl_node.nodes = [
        node0
    ]

    id_access = IdentifierAccess("IdentifierAccess")
    id_access.identifiers = ["ze", "ez"]

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        make_expression(
            arg1=id_access
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_arl():
    # Arrange
    expected = True


    list_expr_row1_node = ListExpression("ListExpression")
    list_expr_row1_node.expressions = [
        make_expression(
            arg1=make_term("REAL_NUMBER", "3.14")
        ),
        make_expression(
            arg1=make_term("REAL_NUMBER", "17.9")
        )
    ]

    list_expr_row2_node = ListExpression("ListExpression")
    list_expr_row2_node.expressions = [
        make_expression(
            arg1=make_term("REAL_NUMBER", "3.14")
        ),
        make_expression(
            arg1=make_term("REAL_NUMBER", "17.9")
        )
    ]

    list_expr_column_node = ListExpression("ListExpression")
    list_expr_column_node.expressions = [
        make_expression(
            arg1=list_expr_row1_node
        ),
        make_expression(
            arg1=list_expr_row2_node
        )
    ]

    ast = ASTNode("PROGRAM", [
        make_expression(
            arg1=list_expr_column_node
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_ope():
    # Arrange
    expected = True

    ast = ASTNode("PROGRAM", [
        make_expression(
            arg1=make_expression("+", token="ExprPlus",
                arg1=make_expression("/", token="ExprMult",
                    arg1=make_term("REAL_NUMBER", "-1.3"),
                    arg2=make_term("INTEGER_NUMBER", "-2")
                ),
                arg2=make_expression("-", token="ExprPlus",
                    arg1=make_expression("*", token="ExprMult",
                        arg1=make_term("NATURAL_NUMBER", "14"),
                        arg2=make_term("NATURAL_NUMBER", "3")
                    ),
                    arg2=make_expression("^", token="ExprMult",
                        arg1=make_term("REAL_NUMBER", "64.0"),
                        arg2=make_term("NATURAL_NUMBER", "2")
                    )
                )
            )
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_mod():
    # Arrange
    expected = True

    ast = ASTNode("PROGRAM", [
        make_expression(
            arg1=make_expression("%", token="ExprMult",
                arg1=make_term("INTEGER_NUMBER", "-1"),
                arg2=make_term("NATURAL_NUMBER", "13")
            )
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_wot():
# Arrange
    expected = True

    node1 = NodeDecl("NodeDecl")
    node1.identifiers = ["alt", "alt2"]

    ident = IdentifierAccess("IdentifierAccess")
    ident.identifiers = ["alt"]

    ident2 = IdentifierAccess("IdentifierAccess")
    ident2.identifiers = ["alt2"]

    edge1 = EdgeDecl("EdgeDecl")
    edge1.initial_node = ident
    edge1.nodes = [ident2]
    edge1.direction = "-->"
    edge1.weight = [
        make_expression(
            arg1=make_term("NATURAL_NUMBER", "2")
        )
    ]

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "digraph"
    graph_decl_node.identifier = "test"
    graph_decl_node.weight_type = "nat"
    graph_decl_node.nodes = [
        node1
    ]
    graph_decl_node.edges = [
        edge1
    ]

    weight_of = make_expression("weight of",
        arg1="test.alt2-->alt",
    )

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        weight_of,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)


def test_type_system_woe():
    # Arrange
    expected = True

    node1 = NodeDecl("NodeDecl")
    node1.identifiers = ["a", "b"]

    ident = IdentifierAccess("IdentifierAccess")
    ident.identifiers = ["a"]

    ident2 = IdentifierAccess("IdentifierAccess")
    ident2.identifiers = ["b"]

    edge1 = EdgeDecl("EdgeDecl")
    edge1.initial_node = ident
    edge1.nodes = [ident2]
    edge1.direction = "---"
    edge1.weight = [
        make_expression(
            arg1=make_term("INTEGER_NUMBER", "-1")
        )
    ]

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "graph"
    graph_decl_node.identifier = "test"
    graph_decl_node.weight_type = "int"
    graph_decl_node.nodes = [
        node1
    ]
    graph_decl_node.edges = [
        edge1
    ]

    weight_of = make_expression("weight of",
        arg1="test.a---b",
    )

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        weight_of,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)


def test_type_system_cmp():
    # Arrange
    expected = True

    ast = ASTNode("PROGRAM", [
        make_expression(
            arg1=make_expression("<", token="ExprRel",
                arg1=make_term("REAL_NUMBER", "2.3"),
                arg2=make_term("NATURAL_NUMBER", "2"),
            )
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_neg():
    # Arrange
    expected = True

    ast = ASTNode("PROGRAM", [
        make_expression(
            arg1=make_expression("neg", token="ExprNot",
                arg1=make_term("BOOL_VALUE", "false")
            )
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_and():
    # Arrange
    expected = True

    ast = ASTNode("PROGRAM", [
        make_expression(
            arg1=make_expression("and", token="ExprAnd",
                arg1=make_term("BOOL_VALUE", "true"),
                arg2=make_term("BOOL_VALUE", "true")
            )
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_orc():
    # Arrange
    expected = True

    ast = ASTNode("PROGRAM", [
        make_expression("or", token="Expr",
            arg1=make_term("BOOL_VALUE", "false"),
            arg2=make_term("BOOL_VALUE", "true")
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_gan_dtg():
    # Arrange
    expected = True

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "tree"
    graph_decl_node.identifier = "yes_graph"
    graph_decl_node.weight_type = None

    node_decl = Declaration("Declaration")
    node_decl.identifiers = ["top"]
    node_decl.type = "node"

    graph_stmt = GraphStatement("GraphStatement")
    graph_stmt.graph_identifier = "yes_graph"
    graph_stmt.operator = "add"
    graph_stmt.argument = node_decl

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        graph_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_grn():
    # Arrange
    expected = True

    node1 = NodeDecl("NodeDecl")
    node1.identifiers = ["a", "b", "c"]

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "tree"
    graph_decl_node.identifier = "yes_graph"
    graph_decl_node.weight_type = None
    graph_decl_node.nodes = [
        node1
    ]

    graph_stmt = GraphStatement("GraphStatement")
    graph_stmt.graph_identifier = "yes_graph"
    graph_stmt.operator = "remove"
    graph_stmt.argument = "c"

    ast = ASTNode("PROGRAM", [
        graph_decl_node,

        graph_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_are():
    # Arrange
    expected = True

    node1 = NodeDecl("NodeDecl")
    node1.identifiers = ["a", "b"]

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "tree"
    graph_decl_node.identifier = "yes_graph"
    graph_decl_node.weight_type = None
    graph_decl_node.nodes = [
        node1
    ]

    ident = IdentifierAccess("IdentifierAccess")
    ident.identifiers = ["a"]

    ident2 = IdentifierAccess("IdentifierAccess")
    ident2.identifiers = ["b"]

    edge1 = EdgeDecl("EdgeDecl")
    edge1.initial_node = ident
    edge1.nodes = [ident2]
    edge1.direction = "<--"

    graph_stmt = GraphStatement("GraphStatement")
    graph_stmt.graph_identifier = "yes_graph"
    graph_stmt.operator = "add"
    graph_stmt.argument = edge1

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        node1,
        graph_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_ind():
    # Arrange
    expected = True

    node_decl_node = NodeDecl("NodeDecl")
    node_decl_node.identifiers = ["a"]

    expr_node_node = ExprNode("ExprNode")
    expr_node_node.expression = make_expression(
        arg1=make_term("IDENTIFIER", "a")
    )
    expr_node_node.direction = "-->"

    ast = ASTNode("PROGRAM", [
        node_decl_node,
        make_expression(
            arg1=expr_node_node
        ),
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)


def test_type_system_com_dis():
    # Arrange
    expected = True

    display1 = DisplayStatement("DisplayStatement")
    display1.expression = make_expression(
        arg1=make_term("NATURAL_NUMBER", "1")
    )

    display2 = DisplayStatement("DisplayStatement")
    display2.expression = make_expression(
        arg1=make_term("NATURAL_NUMBER", "2")
    )

    ast = ASTNode("PROGRAM", [
        display1,
        display2,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_dcl():
    # Arrange
    expected = True

    decl_init_node = DeclarationInit("DeclarationInit")
    decl_init_node.is_list = False
    decl_init_node.identifiers = ["y"]
    decl_init_node.type = "text"
    decl_init_node.expression = [make_expression(
        arg1=make_term("TEXT", "\"he did it\"")
    )]


    ast = ASTNode("PROGRAM", [
        decl_init_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_ass():
    # Arrange
    expected = True

    decl_node = Declaration("Declaration")
    decl_node.is_list = False
    decl_node.identifiers = ["y"]
    decl_node.type = "real"

    assignment = Assignment("Assignment")
    assignment.identifiers = ["y"]
    assignment.expression = make_expression(
        arg1=make_term("NATURAL_NUMBER", "3")
    )

    ast = ASTNode("PROGRAM", [
        decl_node,
        assignment,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_las():
    # Arrange
    expected = True

    list_expr = ListExpression("ListExpression")
    list_expr.expressions = [
        make_expression(
            arg1=make_term("INTEGER_NUMBER", "-1")
        ),
        make_expression(
            arg1=make_term("INTEGER_NUMBER", "1")
        )
    ]

    list_expr2 = ListExpression("ListExpression")
    list_expr2.expressions = [
        make_expression(
            arg1=make_term("INTEGER_NUMBER", "-2")
        ),
        make_expression(
            arg1=make_term("INTEGER_NUMBER", "2")
        )
    ]

    list_expr3 = ListExpression("ListExpression")
    list_expr3.expressions = [
        make_expression(
            arg1=list_expr
        ),
        make_expression(
            arg1=list_expr2
        )
    ]

    decl_init_node = DeclarationInit("DeclarationInit")
    decl_init_node.is_list = True
    decl_init_node.dimension = make_term("NATURAL_NUMBER", "2")
    decl_init_node.identifiers = ["mrts"]
    decl_init_node.type = "int"
    decl_init_node.expression = [list_expr3]

    ast = ASTNode("PROGRAM", [
        decl_init_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_ift():
    # Arrange
    expected = True

    if_stmt = IfStatement("ListExpression")
    if_stmt.condition = make_expression(
        arg1=make_expression("=", token="ExprEq",
            arg1=make_term("INTEGER_NUMBER", "-1"),
            arg2=make_term("INTEGER_NUMBER", "1")
        )
    )
    if_stmt.then_statements = [
        make_expression(
            arg1=make_expression("+", token="ExprPlus",
                arg1=make_term("NATURAL_NUMBER", "1"),
                arg2=make_term("NATURAL_NUMBER", "2"),
            )
        )
    ]

    ast = ASTNode("PROGRAM", [
        if_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_ife():
    # Arrange
    expected = True

    if_stmt = IfStatement("ListExpression")
    if_stmt.condition = make_expression(
        arg1=make_expression("=", token="ExprEq",
            arg1=make_term("INTEGER_NUMBER", "-1"),
            arg2=make_term("INTEGER_NUMBER", "1")
        )
    )
    if_stmt.then_statements = [
        make_expression(
            arg1=make_expression("+", token="ExprPlus",
                arg1=make_term("NATURAL_NUMBER", "1"),
                arg2=make_term("NATURAL_NUMBER", "2"),
            )
        )
    ]

    if_stmt.else_statements = [
        make_expression(
            arg1=make_expression("-", token="ExprPlus",
                arg1=make_term("REAL_NUMBER", "1"),
                arg2=make_term("REAL_NUMBER", "2"),
            )
        )
    ]

    ast = ASTNode("PROGRAM", [
        if_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_whl():
    # Arrange
    expected = True

    while_stmt = WhileStatement("WhileExpression")
    while_stmt.condition = make_expression(
        arg1=make_expression("=", token="ExprEq",
            arg1=make_term("INTEGER_NUMBER", "-1"),
            arg2=make_term("INTEGER_NUMBER", "1")
        )
    )
    while_stmt.statements = [
        make_expression(
            arg1=make_expression("+", token="ExprPlus",
                arg1=make_term("NATURAL_NUMBER", "1"),
                arg2=make_term("NATURAL_NUMBER", "2"),
            )
        )
    ]

    ast = ASTNode("PROGRAM", [
        while_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_rpt():
    # Arrange
    expected = True

    repeat_stmt = RepeatStatement("RepeatStatement")
    repeat_stmt.repeat_expression = make_expression(
        arg1=make_term("NATURAL_NUMBER", "1")
    )
    repeat_stmt.statements = [
        make_expression(
            arg1=make_expression("+", token="ExprPlus",
                arg1=make_term("NATURAL_NUMBER", "1"),
                arg2=make_term("NATURAL_NUMBER", "2"),
            )
        )
    ]

    ast = ASTNode("PROGRAM", [
        repeat_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_for():
    # Arrange
    expected = True

    for_normal_stmt = ForEachNormal("ForEachNormal")
    for_normal_stmt.loop_identifier = "x"
    for_normal_stmt.iterable = make_expression(
        arg1=make_term("TEXT", "\"martin\"")
    )
    for_normal_stmt.statements = [
        make_expression(
            arg1=make_expression("+", token="ExprPlus",
                arg1=make_term("NATURAL_NUMBER", "1"),
                arg2=make_term("NATURAL_NUMBER", "2"),
            )
        )
    ]

    ast = ASTNode("PROGRAM", [
        for_normal_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_fre():
    # Arrange
    expected = True

    node1 = NodeDecl("NodeDecl")
    node1.identifiers = ["a", "b"]

    ident = IdentifierAccess("IdentifierAccess")
    ident.identifiers = ["a"]

    ident2 = IdentifierAccess("IdentifierAccess")
    ident2.identifiers = ["b"]

    edge1 = EdgeDecl("EdgeDecl")
    edge1.initial_node = ident
    edge1.nodes = [ident2]
    edge1.direction = "---"

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "graph"
    graph_decl_node.identifier = "test"
    graph_decl_node.weight_type = None
    graph_decl_node.nodes = [
        node1
    ]
    graph_decl_node.edges = [
        edge1
    ]

    ident3 = IdentifierAccess("IdentifierAccess")
    ident3.identifiers = ["x"]

    ident4 = IdentifierAccess("IdentifierAccess")
    ident4.identifiers = ["y"]

    edge2 = EdgeLoop("EdgeDecl")
    edge2.initial_node = ident
    edge2.last_node = ident4
    edge2.direction = "---"

    for_edge_stmt = ForEachEdge("ForEachEdge")
    for_edge_stmt.edge = edge2
    for_edge_stmt.graph_identifier = "test"
    for_edge_stmt.statements = [
        make_expression(
            arg1=make_term("NATURAL_NUMBER", "1")
        )
    ]

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        for_edge_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_frw():
    # Arrange
    expected = True

    node1 = NodeDecl("NodeDecl")
    node1.identifiers = ["a", "b"]

    ident = IdentifierAccess("IdentifierAccess")
    ident.identifiers = ["a"]

    ident2 = IdentifierAccess("IdentifierAccess")
    ident2.identifiers = ["b"]

    edge1 = EdgeDecl("EdgeDecl")
    edge1.initial_node = ident
    edge1.nodes = [ident2]
    edge1.direction = "-->"
    edge1.weight = [
        make_expression(
            arg1=make_term("INTEGER_NUMBER", "-3")
        )
    ]

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "digraph"
    graph_decl_node.identifier = "test"
    graph_decl_node.weight_type = "int"
    graph_decl_node.nodes = [
        node1
    ]
    graph_decl_node.edges = [
        edge1
    ]

    ident3 = IdentifierAccess("IdentifierAccess")
    ident3.identifiers = ["x"]

    ident4 = IdentifierAccess("IdentifierAccess")
    ident4.identifiers = ["y"]

    edge2 = EdgeLoop("EdgeDecl")
    edge2.initial_node = ident
    edge2.last_node = ident4
    edge2.direction = "-->"

    for_edge_stmt = ForEachEdge("ForEachEdge")
    for_edge_stmt.edge = edge2
    for_edge_stmt.weight_identifier = "a"
    for_edge_stmt.graph_identifier = "test"
    for_edge_stmt.statements = [
        make_expression(
            arg1=make_term("NATURAL_NUMBER", "1")
        )
    ]

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        for_edge_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_stp():
    # Arrange
    expected = True

    stop_node = LoopModifier("LoopModifier")
    stop_node.modifier = "stop"

    for_normal_stmt = ForEachNormal("ForEachNormal")
    for_normal_stmt.loop_identifier = "x"
    for_normal_stmt.iterable = make_expression(
        arg1=make_term("TEXT", "\"martin\"")
    )
    for_normal_stmt.statements = [
        stop_node
    ]

    ast = ASTNode("PROGRAM", [
        for_normal_stmt,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_alg():
    # Arrange
    expected = True

    algo = Algorithm("Algorithm")
    algo.identifier = "nat"
    algo.statements = [
        make_expression(
            arg1=make_term("BOOL_VALUE", "false")
        )
    ]

    ast = ASTNode("PROGRAM", [
        algo,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_alr_ret():
    # Arrange
    expected = True

    param1 = Parameter("Parameter")
    param1.type = "int"
    param1.identifier = "y"

    param2 = Parameter("Parameter")
    param2.type = "nat"
    param2.identifier = "k"

    return_statement = ReturnStatement("ReturnStatement")
    return_statement.expression = make_term("REAL_NUMBER", "21.14")

    algo = Algorithm("Algorithm")
    algo.identifier = "mat"
    algo.parameters = [
        param1,
        param2
    ]
    algo.return_type = "real"
    algo.statements = [return_statement]

    ast = ASTNode("PROGRAM", [
        algo,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_dca():
    # Arrange
    expected = True

    decl_node = Declaration("Declaration")
    decl_node.is_list = False
    decl_node.identifiers = ["y"]
    decl_node.type = "real"

    ast = ASTNode("PROGRAM", [
        decl_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_dlt_dti():
    # Arrange
    expected = True

    decl_node = Declaration("Declaration")
    decl_node.is_list = False
    decl_node.identifiers = ["n"]
    decl_node.type = "node"

    ast = ASTNode("PROGRAM", [
        decl_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_dli_dim():
    # Arrange
    expected = True

    list_decl_node = Declaration("Declaration")
    list_decl_node.is_list = True
    list_decl_node.identifiers = ["x"]
    list_decl_node.type = "int"
    list_decl_node.dimension = make_term("NATURAL_NUMBER", "2")

    ast = ASTNode("PROGRAM", [
        list_decl_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_dli_din():
    # Arrange
    expected = True

    list_decl_node = Declaration("Declaration")
    list_decl_node.is_list = False
    list_decl_node.identifiers = ["x"]
    list_decl_node.type = "int"


    ast = ASTNode("PROGRAM", [
        list_decl_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_ghd():
    # Arrange
    expected = True

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "graph"
    graph_decl_node.identifier = "i"
    graph_decl_node.weight_type = None

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_gdw():
    # Arrange
    expected = True

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "tree"
    graph_decl_node.identifier = "tw"
    graph_decl_node.weight_type = "int"

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_gdi_edu():
    # Arrange
    expected = True

    node1 = NodeDecl("NodeDecl")
    node1.identifiers = ["a", "b", "c"]

    ident = IdentifierAccess("IdentifierAccess")
    ident.identifiers = ["a"]

    ident2 = IdentifierAccess("IdentifierAccess")
    ident2.identifiers = ["b"]

    ident3 = IdentifierAccess("IdentifierAccess")
    ident3.identifiers = ["c"]

    edge1 = EdgeDecl("EdgeDecl")
    edge1.initial_node = ident
    edge1.nodes = [ident2, ident3]
    edge1.direction = "---"

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "graph"
    graph_decl_node.identifier = "gdi"
    graph_decl_node.weight_type = None
    graph_decl_node.nodes = [
        node1
    ]
    graph_decl_node.edges = [
        edge1
    ]

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)

def test_type_system_gwi_ewd():
    # Arrange
    expected = True

    node1 = NodeDecl("NodeDecl")
    node1.identifiers = ["a", "b", "c"]

    ident = IdentifierAccess("IdentifierAccess")
    ident.identifiers = ["a"]

    ident2 = IdentifierAccess("IdentifierAccess")
    ident2.identifiers = ["b"]

    ident3 = IdentifierAccess("IdentifierAccess")
    ident3.identifiers = ["c"]

    edge1 = EdgeDecl("EdgeDecl")
    edge1.initial_node = ident
    edge1.nodes = [ident2, ident3]
    edge1.direction = "-->"
    edge1.weight = [
        make_expression(
            arg1=make_term("REAL_NUMBER", "2.3")
        ),
        make_expression(
            arg1=make_term("REAL_NUMBER", "4.5")
        )
    ]

    graph_decl_node = GraphDecl("GraphDecl")
    graph_decl_node.graph_type = "digraph"
    graph_decl_node.identifier = "gwi"
    graph_decl_node.weight_type = "real"
    graph_decl_node.nodes = [
        node1
    ]
    graph_decl_node.edges = [
        edge1
    ]

    ast = ASTNode("PROGRAM", [
        graph_decl_node,
        ASTNode("EOF", value="$")
    ])
    checker = TypeChecker(ast)

    # Act
    well_formed = checker.check()

    # Assert
    assert well_formed == expected, print_ast(ast)
