import pytest

from parser.ast_builder import *
from evaluator.helpers import *

from evaluator.categories.statement import execute_statement, LoopStop, Return

from unittest.mock import patch
from types import SimpleNamespace

from copy import deepcopy

from evaluator.categories.statement import *
from evaluator.categories.expression import *
from evaluator.categories.graph_declaration import *
from evaluator.categories.declaration import *
from typesystem.data_types import *

class EmptyGraphContext:
    graph = None

class FakeGraph:
    def __init__(self, nodes=None):
        self.graph = {}
        self.nodes = nodes or {}

    def get_nodes(self):
        return self.nodes    

@pytest.fixture
def setup_env():
    return {
        "env_graph": {},
        "env_var": {"x": 0, "arr": 1},
        "env_algo": {},
        "store": {
            0: 10,
            1: [[1, 2], [3, 4]],
        },
        "loc": 2,
        "graph_object": EmptyGraphContext
    }

def expr_result(value, store=None, graph_object=None):
    if store is None:
        store = {}
    return SimpleNamespace(
        v=value,
        modified_store=store,
        store=store,
        graph_object=graph_object,
    )


def test_declaration(setup_env):

    # Arrange
    node = Declaration("Declaration")
    node.identifiers = ["a"]
    node.type = TypeEnum.INT
    node.is_list = False

    fake_result = SimpleNamespace(
        store={0: 10, 1: [[1, 2], [3, 4]], 2: None},
        env_var={"x": 0, "arr": 1, "a": 2},
        location=3,
    )

    with patch("evaluator.categories.declaration.execute_declaration", return_value=fake_result):

        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
        )
        
    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert env_var["a"] == 2
    assert value is None
    assert loc == 3


def test_declaration_init_non_list(setup_env):

    # Arrange
    node = DeclarationInit("DeclarationInit")
    node.identifiers = ["a"]
    node.type = TypeEnum.INT
    node.is_list = False

    expr = Term("Term")
    expr.type = TypeEnum.INT
    expr.value = "99"
    node.expression = [expr]

    fake_result = SimpleNamespace(
        store={0: 10, 1: [[1, 2], [3, 4]], 2: None},
        env_var={"x": 0, "arr": 1, "a": 2},
        location=3,
    )

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(99, setup_env["store"].copy())), patch("evaluator.categories.declaration.execute_declaration",return_value=fake_result):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert store[2] == 99
    assert value is None
    assert loc == 3

def test_declaration_init_list(setup_env):

    # Arrange
    node = DeclarationInit("DeclarationInit")
    node.identifiers = ["xs"]
    node.type = TypeEnum.INT
    node.is_list = True

    expr = Term("Term")
    expr.type = TypeEnum.NAT
    expr.value = "7"
    node.expression = [expr]

    fake_decl_result = SimpleNamespace(
        store={0: 10, 1: [[1, 2], [3, 4]], 2: []},
        env_var={"x": 0, "arr": 1, "xs": 2},
        location=3,
    )

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(7, setup_env["store"].copy())), patch("evaluator.categories.declaration.execute_declaration", return_value=fake_decl_result):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert store[2] == 7
    assert value == None
    assert loc == 3

def test_normal_assignment(setup_env):

    # Arrange
    node = Assignment("Assignment")
    node.identifiers = ["x"]

    expr = Term("Term")
    expr.type = TypeEnum.INT
    expr.value = "42"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(42, setup_env["store"].copy())):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert store[0] == 42
    assert value is None
    assert loc == setup_env["loc"]


def test_graph_node_attribute_assignment_outside_graph(setup_env):
    # Arrange
    setup_env["env_graph"] = {"G": FakeGraph({"x": {"value": 1}})}

    node = Assignment("Assignment")
    node.identifiers = ["G", "x", "value"]

    expr = Term("Term")
    expr.type = TypeEnum.INT
    expr.value = "99"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(99, setup_env["store"].copy())):

        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
            )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert env_graph["G"].get_nodes()["x"]["value"] == 99
    assert value is None


def test_graph_node_nested_attribute_assignment_outside_graph(setup_env):
    # Arrange
    setup_env["env_graph"] = {"G": FakeGraph({"x": {"child": {"value": 1}}})}

    node = Assignment("Assignment")
    node.identifiers = ["G", "x", "child", "value"]

    expr = Term("Term")
    expr.type = TypeEnum.INT
    expr.value = "99"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(123, setup_env["store"].copy())):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert env_graph["G"].get_nodes()["x"]["child"]["value"] == 123
    assert value is None


def test_graph_node_attribute_assignment_inside_graph(setup_env):
    # Arrange
    graph_object = FakeGraph({"node_x": {"value": 1}})
    setup_env["env_var"]["x"] = 2
    setup_env["store"][2] = "node_x"

    node = Assignment("Assignment")
    node.identifiers = ["x", "value"]

    expr = Term("Term")
    expr.type = TypeEnum.INT
    expr.value = "55"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(55, setup_env["store"].copy())):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            graph_object,
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert graph_object.get_nodes()["node_x"]["value"] == 55
    assert value is None


def test_graph_node_nested_attribute_assignment_inside_graph(setup_env):
    # Arrange
    graph_object = FakeGraph({"node_x": {"child": {"child": {"value": 1}}}})
    setup_env["env_var"]["x"] = 2
    setup_env["store"][2] = "node_x"


    node = Assignment("Assignment")
    node.identifiers = ["x", "child", "child", "value"]

    expr = Term("Term")
    expr.type = TypeEnum.INT
    expr.value = "88"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(88, setup_env["store"].copy())):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            graph_object,
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert graph_object.get_nodes()["node_x"]["child"]["child"]["value"] == 88
    assert value is None


def test_if_statement_true_branch(setup_env):
    # Arrange
    node = IfStatement("IfStatement")
    node.condition = Term("Term")
    node.then_statements = [Declaration("Declaration")]
    node.else_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=expr_result(True, setup_env["store"].copy()),
    ), patch(
        "evaluator.categories.statement.execute_statement",
        return_value=(
            {0: 99},
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
            None,
            setup_env["loc"],
        )
    ) as mocked_statement:
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert store == {0: 99}
    assert value is None
    assert mocked_statement.call_count == 1

def test_if_statement_false_branch(setup_env):
    # Arrange
    node = IfStatement("IfStatement")
    node.condition = Term("Term")
    node.then_statements = [Declaration("Declaration")]
    node.else_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=expr_result(False, setup_env["store"].copy()),
    ), patch(
        "evaluator.categories.statement.execute_statement",
        return_value=(
            {0: 77},
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
            None,
            setup_env["loc"],
        ),
    ) as mocked_statement:
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert store == {0: 77}
    assert value is None
    assert mocked_statement.call_count == 1

def test_if_statement_false_no_else(setup_env):
    # Arrange
    node = IfStatement("IfStatement")
    node.condition = Term("Term")
    node.then_statements = [Declaration("Declaration")]
    node.else_statements = []

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(False, setup_env["store"].copy())):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert store == setup_env["store"]
    assert value is None
    assert loc == setup_env["loc"]


def test_algorithm_statement(setup_env):
    # Arrange
    node = Algorithm("Algorithm")

    with patch("evaluator.categories.algorithm.execute_algorithm", return_value={"algo": "env"}):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert env_algo == {"algo": "env"}
    assert value is None
    assert loc == setup_env["loc"]


def test_graph_decl_statement(setup_env):
    # Arrange
    node = GraphDecl("GraphDecl")

    with patch("evaluator.categories.graph_declaration.execute_graph_decl", return_value=({"G": {}}, {0: 10})):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert env_graph == {"G": {}}
    assert store == {0: 10}
    assert value is None
    assert loc == setup_env["loc"]

def test_expression_statement(setup_env):
    # Arrange
    node = Expression("Expression")

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(42, {0: 10})):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert store == {0: 10}
    assert value is None
    assert loc == setup_env["loc"]

def test_edge_decl_statement(setup_env):
    # Arrange
    node = EdgeDecl("EdgeDecl")

    with patch("evaluator.categories.edge_declaration.execute_edge_declaration", return_value=("edge-value", setup_env["store"])):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert value == None
    assert store == setup_env["store"]
    assert loc == setup_env["loc"]

def test_node_decl_statement(setup_env):
    # Arrange
    node = NodeDecl("NodeDecl")
    node.identifiers = ["n"]

    fake_graph_object = SimpleNamespace(graph={})

    fake_decl_result = SimpleNamespace(
        store={0: 10, 2: None},
        env_var={"x": 0, "n": 2},
        location=3,
    )

    with patch("evaluator.categories.declaration.execute_declaration", return_value=fake_decl_result):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            fake_graph_object,
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert store == fake_decl_result.store
    assert env_var == fake_decl_result.env_var
    assert value is None
    assert loc == 3

def test_graph_statement(setup_env):
    # Arrange
    node = GraphStatement("GraphStatement")

    with patch("evaluator.categories.graph_statement.execute_graph_statement") as mocked:
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    mocked.assert_called_once()
    assert value is None
    assert store == setup_env["store"]

def test_loop_modifier_raises_loop_exception(setup_env):
    # Arrange
    node = LoopModifier("LoopModifier")

    # Act & Assert
    with pytest.raises(LoopStop):
        execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )


def test_display_statement(setup_env, capsys):
    # Arrange
    node = DisplayStatement("DisplayStatement")
    node.expression = Term("Term")

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result("hello world", {0: 10})):
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    captured = capsys.readouterr()
    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert "hello world" in captured.out
    assert store == {0: 10}
    assert value is None

def test_return_statement_raises_return_exception(setup_env):
    # Arrange
    node = ReturnStatement("ReturnStatement")
    node.expression = Term("Term")

    with patch("evaluator.categories.expression.execute_expression", return_value=expr_result(99, {0: 10})):
        #act & assert
        with pytest.raises(Return):
            execute_statement(
                node,
                setup_env["loc"],
                setup_env["graph_object"],
                setup_env["store"],
                setup_env["env_var"],
                setup_env["env_algo"],
                setup_env["env_graph"],
            )

def test_repeat_statement_runs_body_three_times(setup_env):
    # Arrange
    node = RepeatStatement("RepeatStatement")
    node.repeat_expression = Term("Term")
    node.repeat_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=expr_result(3, setup_env["store"].copy()),
    ), patch(
        "evaluator.categories.statement.execute_statement",
        return_value=(
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
            None,
            setup_env["loc"],
        ),
    ) as mocked_statement:
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert mocked_statement.call_count == 3
    assert store == setup_env["store"]
    assert value is None
    assert loc == setup_env["loc"]

def test_repeat_statement_zero_times_does_not_run_body(setup_env):
    # Arrange
    node = RepeatStatement("RepeatStatement")
    node.repeat_expression = Term("Term")
    node.repeat_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=expr_result(0, setup_env["store"].copy()),
    ), patch(
        "evaluator.categories.statement.execute_statement",
    ) as mocked_statement:
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert mocked_statement.call_count == 0
    assert store == setup_env["store"]
    assert value is None
    assert loc == setup_env["loc"]


def test_repeat_statement_breaks_on_loop_exception(setup_env):
    # Arrange
    node = RepeatStatement("RepeatStatement")
    node.repeat_expression = Term("Term")
    node.repeat_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=expr_result(5, setup_env["store"].copy()),
    ), patch(
        "evaluator.categories.statement.execute_statement",
        side_effect=LoopStop(),
    ) as mocked_statement:
        # Act
        result = execute_statement(
            node,
            setup_env["loc"],
            setup_env["graph_object"],
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"],
        )

    store, env_var, env_algo, env_graph, value, loc = result

    # Assert
    assert mocked_statement.call_count == 1
    assert store == setup_env["store"]
    assert value is None
    assert loc == setup_env["loc"]

def make_term(_type=None, value=None, children=None, token="Term"):
    term = Term(token)
    term.type = _type
    term.value = value
    term.children = children
    return term

def make_expression(operator=None, arg1=None, arg2=None, token="Expression"):
    expr = Expression(token)
    expr.operator = operator
    expr.arg1 = arg1
    expr.arg2 = arg2
    return expr

def make_list_expression(expressions: list, token="ListExpression"):
    list_expression = ListExpression(token)
    list_expression.expressions = expressions
    return list_expression

def make_assignment(identifiers: list, expression: Expression, token="Assignment"):
    assigment = Assignment(token)
    assigment.identifiers = identifiers
    assigment.expression = expression
    return assigment

def make_declaration(identifiers: list[str], _type: str, is_list=False, dimension=None, token="Declaration"):
    declaration = Declaration(token)
    declaration.type = _type
    declaration.identifiers = identifiers
    declaration.is_list = is_list
    if dimension:
        declaration.dimension = Term("Term")
        declaration.dimension.type = TypeEnum.NAT
        declaration.dimension.value = dimension
    return declaration

def make_node_declaration(identifiers: list[str], is_list=False, dimension=None, token="NodeDecl"):
    declaration = NodeDecl(token)
    declaration.identifiers = identifiers
    declaration.is_list = is_list
    if dimension:
        declaration.dimension = Term("Term")
        declaration.dimension.type = TypeEnum.NAT
        declaration.dimension.value = dimension
    return declaration

def make_edge_declaration(initial_node, nodes: list, direction, weight: list, token="EdgeDecl"):
    edge_decl = EdgeDecl(token)
    edge_decl.initial_node = initial_node
    edge_decl.nodes = nodes
    edge_decl.direction = direction
    edge_decl.weight = weight
    return edge_decl

def give_edge_declaration_int_weight(edge_decl):
    for i in range(0,len(edge_decl.nodes)):
        term = make_term(TypeEnum.INT,f"{i+1}")
        edge_decl.weight.append(make_expression(arg1=term))

def make_graph_decl(graph_type, identifier, weight_type, nodes: list, edges: list, token="GraphDecl"):
    graph_decl = GraphDecl(token)
    graph_decl.graph_type = graph_type
    graph_decl.identifier = identifier
    graph_decl.weight_type = weight_type
    graph_decl.nodes = nodes
    graph_decl.edges = edges
    return graph_decl

def make_graph_statement(graph_identifier, operator, argument, token="GraphStatement"):
    graph_statement = GraphStatement(token)
    graph_statement.graph_identifier = graph_identifier
    graph_statement.operator = operator
    graph_statement.argument = argument
    return graph_statement

def make_edge_loop(initial_node, last_node, direction, token="EdgeLoop"):
    edge_loop = EdgeLoop(token)
    edge_loop.initial_node = initial_node
    edge_loop.last_node = last_node
    edge_loop.direction = direction
    return edge_loop

def make_while_statement(condition: Expression, statements: list, token="WhileStatement"):
    while_statement = WhileStatement(token)
    while_statement.condition = condition
    while_statement.statements = statements
    return while_statement

def make_for_each_normal(loop_identifier, iterable, statements: list, token="ForEachNormal"):
    for_each_normal = ForEachNormal(token)
    for_each_normal.loop_identifier = loop_identifier
    for_each_normal.iterable = iterable
    for_each_normal.statements = statements
    return for_each_normal

def make_for_each_edge(edge, weight_identifier, graph_identifier, statements: list, token="ForEachEdge"):
    for_each_edge = ForEachEdge(token)
    for_each_edge.edge = edge
    for_each_edge.weight_identifier = weight_identifier
    for_each_edge.graph_identifier = graph_identifier
    for_each_edge.statements = statements
    return for_each_edge

def make_reapeat_statement(repeat_expression=None, repeat_statements=[], token="RepeatStatement"):
    repeat_statement = RepeatStatement(token)
    repeat_statement.repeat_expression = repeat_expression
    repeat_statement.repeat_statements = repeat_statements
    return repeat_statement

def test_while_statement():
    # Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()
    statements = []

    condition_expression_arg1 = make_term("IDENTIFIER","i")
    condition_expression_arg2 = make_term(TypeEnum.NAT,"6")
    condition_expression = make_expression("<", condition_expression_arg1, condition_expression_arg2)
    condition_expression = make_expression(arg1=condition_expression)
    env_var.update({"i": loc})
    store.update({loc: 1})
    loc = loc.next_location()
    
    assigment_expression_arg1 = make_term(TypeEnum.NAT,"1")
    assigment_expression_arg2 = make_term("IDENTIFIER","i")
    assigment_expression = make_expression("+", assigment_expression_arg1, assigment_expression_arg2)
    assigment_expression = make_expression(arg1=assigment_expression)
    assigment = make_assignment(["i"],assigment_expression)

    statements.append(assigment)

    while_statment = make_while_statement(condition_expression,statements)

    # Act
    store, env_var, env_algo, env_graph, value, loc = execute_statement(while_statment, loc, graph_object, store, env_var, env_algo, env_graph)

    # Assert
    assert store.get(env_var.get("i")) == 6
    

def test_for_each_normal():
    # Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()
    statements = []

  
    loop_identifier = "i"
    
    assigment_expression_arg1 = make_term(TypeEnum.NAT,"1")
    assigment_expression = make_expression(None, assigment_expression_arg1, None)
    assigment_expression = make_expression(arg1=assigment_expression)
    assigment = make_assignment(["i"],assigment_expression)

    statements.append(assigment)

    env_var.update({"array": loc})
    store.update({loc: [2,4,6,8,10]})
    loc = loc.next_location()
    iterable_arg1 = make_term("IDENTIFIER","array")
    iterable = make_expression(None, iterable_arg1, None)

    for_each_normal = make_for_each_normal(loop_identifier,iterable,statements)

    # Act
    store, env_var, env_algo, env_graph, value, loc = execute_statement(for_each_normal, loc, graph_object, store, env_var, env_algo, env_graph)

    # Assert
    assert store.get(env_var.get("i")) == None
    assert store.get(env_var.get("array")) == [2,4,6,8,10]
    
def test_for_each_edge():
    # Arrange
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()
    
    global_node_decl = make_node_declaration(['f'])
    store, env_var, env_algo, env_graph, v, loc = execute_statement(global_node_decl, loc, graph_object, store, env_var, env_algo, env_graph)

    node_decl = []
    node_decl_nodes = ['a', 'b,', 'c', 'd', 'e']
    node_decl.append(make_node_declaration(node_decl_nodes))
    
    edge_initial_node = 'a'
    edge_decl_nodes = ['b', 'c', 'd', 'e']
    edge_direction = '-->'
    temp_edge_decl = make_edge_declaration(edge_initial_node, edge_decl_nodes, edge_direction, [])
    give_edge_declaration_int_weight(temp_edge_decl)
    edge_decl = []
    edge_decl.append(temp_edge_decl)

    graph_decl_type = TypeEnum.DIGRAPH
    graph_decl_identifier = 'G'
    graph_decl_weight_type = TypeEnum.INT
    graph_decl_nodes = node_decl
    graph_decl_edges = edge_decl
    graph_decl = make_graph_decl(graph_decl_type, graph_decl_identifier, graph_decl_weight_type, graph_decl_nodes, graph_decl_edges)
    store, env_var, env_algo, env_graph, value, loc = execute_statement(graph_decl, loc, graph_object, store, env_var, env_algo, env_graph)
    
    graph_statement1_edge_decl = make_edge_declaration('x', ['y'], '-->', [])
    graph_statement1 = make_graph_statement(graph_decl_identifier, 'remove', graph_statement1_edge_decl)

    graph_statement2_edge_decl = make_edge_declaration('y', ['f'], '-->', [make_expression(arg1=make_term('IDENTIFIER','w'))])
    graph_statement2 = make_graph_statement(graph_decl_identifier, 'add', graph_statement2_edge_decl)

    edge_loop = make_edge_loop('x', 'y', '-->')
    weight_identifier = 'w'
    graph_identifier = 'G'
    statements = []
    statements.append(graph_statement1)
    statements.append(graph_statement2)
    for_each_edge = make_for_each_edge(edge_loop, weight_identifier, graph_identifier, statements)

    # Act
    store, env_var, env_algo, env_graph, value, loc = execute_statement(for_each_edge, loc, graph_object, store, env_var, env_algo, env_graph)

    # Assert
    assert store.get(env_var.get("w")) == None
    assert store.get(env_var.get("x")) == None
    assert store.get(env_var.get("y")) == None
    assert env_graph.get(graph_identifier).get_edge_data('b', 'f')['weight'] == 1
    assert env_graph.get(graph_identifier).get_edge_data('c', 'f')['weight'] == 2
    assert env_graph.get(graph_identifier).get_edge_data('d', 'f')['weight'] == 3
    assert env_graph.get(graph_identifier).get_edge_data('e', 'f')['weight'] == 4
    assert ('b','f') in env_graph.get(graph_identifier).get_edges()
    assert ('c','f') in env_graph.get(graph_identifier).get_edges()
    assert ('d','f') in env_graph.get(graph_identifier).get_edges()
    assert ('e','f') in env_graph.get(graph_identifier).get_edges()