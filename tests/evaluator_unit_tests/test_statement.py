import pytest

from parser.ast_builder import *
from evaluator.functions import *

from evaluator.categories.statement import execute_statement, LoopException, ReturnException

from unittest.mock import patch
from types import SimpleNamespace


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
        "graph_object": None,
    }




def test_declaration(setup_env):

    #arrange
    node = Declaration("Declaration")
    node.identifiers = ["a"]
    node.type = "int"
    node.is_list = False

    fake_result = SimpleNamespace(
        store={0: 10, 1: [[1, 2], [3, 4]], 2: None},
        env_var={"x": 0, "arr": 1, "a": 2},
        location=3,
    )

    with patch("evaluator.categories.declaration.execute_declaration", return_value=fake_result):

        #act
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

    #assert
    assert env_var["a"] == 2
    assert value is None
    assert loc == 3


def test_declaration_init_non_list(setup_env):

    #arrange
    node = DeclarationInit("DeclarationInit")
    node.identifiers = ["a"]
    node.type = "int"
    node.is_list = False

    expr = Term("Term")
    expr.type = "INTEGER_NUMBER"
    expr.value = "99"
    node.expression = [expr]

    fake_result = SimpleNamespace(
        store={0: 10, 1: [[1, 2], [3, 4]], 2: None},
        env_var={"x": 0, "arr": 1, "a": 2},
        location=3,
    )

    with patch("evaluator.categories.expression.execute_expression", return_value=(99, setup_env["store"].copy())), patch("evaluator.categories.declaration.execute_declaration",return_value=fake_result):
        #act
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

    #assert
    assert store[2] == 99
    assert value is None
    assert loc == 3

def test_declaration_init_list(setup_env):

    #arrange
    node = DeclarationInit("DeclarationInit")
    node.identifiers = ["xs"]
    node.type = "int"
    node.is_list = True

    expr = Term("Term")
    expr.type = "NATURAL_NUMBER"
    expr.value = "7"
    node.expression = [expr]

    fake_decl_result = SimpleNamespace(
        store={0: 10, 1: [[1, 2], [3, 4]], 2: []},
        env_var={"x": 0, "arr": 1, "xs": 2},
        location=3,
    )

    with patch("evaluator.categories.expression.execute_expression", return_value=(7, setup_env["store"].copy())), patch("evaluator.categories.declaration.execute_declaration", return_value=fake_decl_result):
        #act
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

    #assert
    assert store[2] == 7
    assert value == 7
    assert loc == 3

def test_normal_assignment(setup_env):

    #arrange
    node = Assignment("Assignment")
    node.identifiers = ["x"]

    expr = Term("Term")
    expr.type = "INTEGER_NUMBER"
    expr.value = "42"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=(42, setup_env["store"].copy())):
        #act
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

    #assert
    assert store[0] == 42
    assert value is None
    assert loc == setup_env["loc"]


def test_graph_node_attribute_assignment_outside_graph(setup_env):
    #arrange
    setup_env["env_graph"] = {"G": {"x": {"value": 1}}}

    node = Assignment("Assignment")
    node.identifiers = ["G", "x", "value"]

    expr = Term("Term")
    expr.type = "INTEGER_NUMBER"
    expr.value = "99"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=(99, setup_env["store"].copy())):

        #act
        result = execute_statement(
            node,
            setup_env["loc"],
            None,
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
            )

    store, env_var, env_algo, env_graph, value, loc = result

    #assert
    assert env_graph["G"]["x"]["value"] == 99
    assert value is None


def test_graph_node_nested_attribute_assignment_outside_graph(setup_env):
    #arrange
    setup_env["env_graph"] = {"G": {"x": {"child": {"value": 1}}}}

    node = Assignment("Assignment")
    node.identifiers = ["G", "x", "child", "value"]

    expr = Term("Term")
    expr.type = "INTEGER_NUMBER"
    expr.value = "99"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=(123, setup_env["store"].copy())):
        #act
        result = execute_statement(
            node,
            setup_env["loc"],
            None,
            setup_env["store"],
            setup_env["env_var"],
            setup_env["env_algo"],
            setup_env["env_graph"]
        )

    store, env_var, env_algo, env_graph, value, loc = result

    #assert
    assert env_graph["G"]["x"]["child"]["value"] == 123
    assert value is None


def test_graph_node_attribute_assignment_inside_graph(setup_env):
    #arrange
    graph_object = {"x": {"value": 1}}

    node = Assignment("Assignment")
    node.identifiers = ["x", "value"]

    expr = Term("Term")
    expr.type = "INTEGER_NUMBER"
    expr.value = "55"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=(55, setup_env["store"].copy())):
        #act
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

    #assert
    assert graph_object["x"]["value"] == 55
    assert value is None


def test_graph_node_nested_attribute_assignment_inside_graph(setup_env):
    #arrange
    graph_object = {"x": {"child": {"child": {"value": 1}}}}

    node = Assignment("Assignment")
    node.identifiers = ["x", "child", "child", "value"]

    expr = Term("Term")
    expr.type = "INTEGER_NUMBER"
    expr.value = "88"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=(88, setup_env["store"].copy())):
        #act
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

    #assert
    assert(graph_object["x"]["child"]["child"]["value"]) == 88
    assert value is None


def test_if_statement_true_branch(setup_env):
    #arrange
    node = IfStatement("IfStatement")
    node.condition = Term("Term")
    node.then_statements = [Declaration("Declaration")]
    node.else_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=(True, setup_env["store"].copy()),
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
        #act
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

    #assert
    assert store == {0: 99}
    assert value is None
    assert mocked_statement.call_count == 1

def test_if_statement_false_branch(setup_env):
    #arange
    node = IfStatement("IfStatement")
    node.condition = Term("Term")
    node.then_statements = [Declaration("Declaration")]
    node.else_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=(False, setup_env["store"].copy()),
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
        #act
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

    #asset
    assert store == {0: 77}
    assert value is None
    assert mocked_statement.call_count == 1

def test_if_statement_false_no_else(setup_env):
    #arrange
    node = IfStatement("IfStatement")
    node.condition = Term("Term")
    node.then_statements = [Declaration("Declaration")]
    node.else_statements = []

    with patch("evaluator.categories.expression.execute_expression", return_value=(False, setup_env["store"].copy())):
        #act
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

    #assert
    assert store == setup_env["store"]
    assert value is None
    assert loc == setup_env["loc"]


def test_algorithm_statement(setup_env):
    #arrange
    node = Algorithm("Algorithm")

    with patch("evaluator.categories.algorithm.execute_algorithm", return_value={"algo": "env"}):
        #act
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

    #assert
    assert env_algo == {"algo": "env"}
    assert value is None
    assert loc == setup_env["loc"]


def test_graph_decl_statement(setup_env):
    #arrange
    node = GraphDecl("GraphDecl")

    with patch("evaluator.categories.graph_declaration.execute_graph_decl", return_value=({"G": {}}, {0: 10})):
        #act
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

    #assert
    assert env_graph == {"G": {}}
    assert store == {0: 10}
    assert value is None
    assert loc == setup_env["loc"]

def test_expression_statement(setup_env):
    #arrange
    node = Expression("Expression")

    with patch("evaluator.categories.expression.execute_expression", return_value=(42, {0: 10})):
        #act
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

    #assert
    assert store == {0: 10}
    assert value is None
    assert loc == setup_env["loc"]

def test_edge_decl_statement(setup_env):
    #arange
    node = EdgeDecl("EdgeDecl")

    with patch("evaluator.categories.edge_declaration.execute_edge_declaration", return_value=("edge-value")):
        #act
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

    #assert
    assert value == "edge-value"
    assert store == setup_env["store"]
    assert loc == setup_env["loc"]

def test_node_decl_statement(setup_env):
    #arrange
    node = NodeDecl("NodeDecl")
    node.identifiers = ["n"]

    fake_graph_object = SimpleNamespace(graph={})

    fake_decl_result = SimpleNamespace(
        store={0: 10, 2: None},
        env_var={"x": 0, "n": 2},
        location=3,
    )

    with patch("evaluator.categories.declaration.execute_declaration", return_value=fake_decl_result):
        #act
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

    #assert
    assert store == fake_decl_result.store
    assert env_var == fake_decl_result.env_var
    assert value is None
    assert loc == 3

def test_graph_statement(setup_env):
    #arrange
    node = GraphStatement("GraphStatement")

    with patch("evaluator.categories.graph_statement.execute_graph_statement") as mocked:
        #act
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

    #assert
    mocked.assert_called_once()
    assert value is None
    assert store == setup_env["store"]

def test_loop_modifier_raises_loop_exception(setup_env):
    #arrange
    node = LoopModifier("LoopModifier")

    #act & assert
    with pytest.raises(LoopException):
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
    #arrange
    node = DisplayStatement("DisplayStatement")
    node.expression = Term("Term")

    with patch("evaluator.categories.expression.execute_expression", return_value=("hello world", {0: 10})):
        #act
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

    #assert
    assert "hello world" in captured.out
    assert store == {0: 10}
    assert value is None

def test_return_statement_raises_return_exception(setup_env):
    #arrange
    node = ReturnStatement("ReturnStatement")
    node.expression = Term("Term")

    with patch("evaluator.categories.expression.execute_expression", return_value=(99, {0: 10})):
        #act & assert
        with pytest.raises(ReturnException):
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
    #arrange
    node = RepeatStatement("RepeatStatement")
    node.repeat_expression = Term("Term")
    node.repeat_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=(3, setup_env["store"].copy()),
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
        #act
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

    #assert
    assert mocked_statement.call_count == 3
    assert store == setup_env["store"]
    assert value is None
    assert loc == setup_env["loc"]

def test_repeat_statement_zero_times_does_not_run_body(setup_env):
    #arrange
    node = RepeatStatement("RepeatStatement")
    node.repeat_expression = Term("Term")
    node.repeat_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=(0, setup_env["store"].copy()),
    ), patch(
        "evaluator.categories.statement.execute_statement",
    ) as mocked_statement:
        #act
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

    #assert
    assert mocked_statement.call_count == 0
    assert store == setup_env["store"]
    assert value is None
    assert loc == setup_env["loc"]


def test_repeat_statement_breaks_on_loop_exception(setup_env):
    #arrange
    node = RepeatStatement("RepeatStatement")
    node.repeat_expression = Term("Term")
    node.repeat_statements = [Declaration("Declaration")]

    with patch(
        "evaluator.categories.expression.execute_expression",
        return_value=(5, setup_env["store"].copy()),
    ), patch(
        "evaluator.categories.statement.execute_statement",
        side_effect=LoopException(),
    ) as mocked_statement:
        #act
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

    #assert
    assert mocked_statement.call_count == 1
    assert store == setup_env["store"]
    assert value is None
    assert loc == setup_env["loc"]