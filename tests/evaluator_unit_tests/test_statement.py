import unittest

from parser.ast_builder import *
from evaluator.functions import *

from evaluator.categories.statement import execute_statement
from evaluator.categories.expression import execute_expression

from unittest.mock import patch
from types import SimpleNamespace



class TestStatements(unittest.TestCase):

    def setUp(self):
        #arrange
        self.env_graph = {}
        self.env_var = {"x": 0, "arr": 1}
        self.env_algo = {}

        self.store = {
            0: 10,
            1: [[1, 2], [3, 4]],
        }

        self.loc = 2
        self.graph_object = None




    def test_declaration(self):

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
                self.env_graph,
                self.env_var,
                self.env_algo,
                self.loc,
                self.graph_object,
                self.store
            )
            
        store, env_var, env_algo, env_graph, value, loc = result

        #assert
        self.assertEqual(env_var["a"], 2)
        self.assertIsNone(value)
        self.assertEqual(loc, 3)

    def test_declaration_init_non_list(self):

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

        with patch("evaluator.categories.expression.execute_expression", return_value=(99, self.store.copy())), patch("evaluator.categories.declaration.execute_declaration",return_value=fake_result):
            #act
            result = execute_statement(
                node,
                self.env_graph,
                self.env_var,
                self.env_algo,
                self.loc,
                self.graph_object,
                self.store,
            )

        store, env_var, env_algo, env_graph, value, loc = result

        #assert
        self.assertEqual(store[2], 99)
        self.assertEqual(value, None)
        self.assertEqual(loc, 3)

    def test_declaration_init_list(self):

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

        with patch("evaluator.categories.expression.execute_expression", return_value=(7, self.store.copy())), patch("evaluator.categories.declaration.execute_declaration", return_value=fake_decl_result):
            #act
            result = execute_statement(
                node,
                self.env_graph,
                self.env_var,
                self.env_algo,
                self.loc,
                self.graph_object,
                self.store,
            )

        store, env_var, env_algo, env_graph, value, loc = result

        #assert
        self.assertEqual(store[2], 7)
        self.assertEqual(value, 7)
        self.assertEqual(loc, 3)

    def test_normal_assignment(self):

        #arrange
        node = Assignment("Assignment")
        node.identifiers = ["x"]

        expr = Term("Term")
        expr.type = "INTEGER_NUMBER"
        expr.value = "42"
        node.expression = expr

        with patch("evaluator.categories.expression.execute_expression", return_value=(42, self.store.copy())):
            #act
            result = execute_statement(
                node,
                self.env_graph,
                self.env_var,
                self.env_algo,
                self.loc,
                self.graph_object,
                self.store,
            )

        store, env_var, env_algo, env_graph, value, loc = result

        #assert
        self.assertEqual(store[0], 42)
        self.assertIsNone(value)
        self.assertEqual(loc, self.loc)


    def test_graph_node_attribute_assignment_outside_graph(self):
        #arrange
        self.env_graph = {"G": {"x": {"value": 1}}}

        node = Assignment("Assignment")
        node.identifiers = ["G", "x", "value"]

        expr = Term("Term")
        expr.type = "INTEGER_NUMBER"
        expr.value = "99"
        node.expression = expr

        with patch("evaluator.categories.expression.execute_expression", return_value=(99, self.store.copy())):

            #act
            result = execute_statement(
                node,
                self.env_graph,
                self.env_var,
                self.env_algo,
                self.loc,
                None,
                self.store
                )

        store, env_var, env_algo, env_graph, value, loc = result

        #assert
        self.assertEqual(env_graph["G"]["x"]["value"], 99)
        self.assertIsNone(value)


def test_graph_node_nested_attribute_assignment_outside_graph(self):
    #arrange
        self.env_graph = {"G": {"x": {"child": {"value": 1}}}}

        node = Assignment("Assignment")
        node.identifiers = ["G", "x", "value"]

        expr = Term("Term")
        expr.type = "INTEGER_NUMBER"
        expr.value = "99"
        node.expression = expr

        with patch("evaluator.categories.expression.execute_expression", return_value=(123, self.store.copy())):
            #act
            result = execute_statement(
                node,
                self.env_graph,
                self.env_var,
                self.env_algo,
                self.loc,
                None,
                self.store,
            )

        store, env_var, env_algo, env_graph, value, loc = result

        #assert
        self.assertEqual(env_graph["G"]["x"]["child"]["value"], 123)
        self.assertIsNone(value)


def test_graph_node_attribute_assignment_inside_graph(self):
    #arrange
    graph_object = {"x": {"value": 1}}

    node = Assignment("Assignment")
    node.identifiers = ["x", "value"]

    expr = Term("Term")
    expr.type = "INTEGER_NUMBER"
    expr.value = "55"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=(55, self.store.copy())):
        #act
        result = execute_statement(
            node,
            self.env_graph,
            self.env_var,
            self.env_algo,
            self.loc,
            graph_object,
            self.store,
        )

    store, env_var, env_algo, env_graph, value, loc = result

    #assert
    self.assertEqual(graph_object["x"]["value"], 55)
    self.assertIsNone(value)


def test_graph_node_nested_attribute_assignment_inside_graph(self):
    #arrange
    graph_object = {"x": {"child": {"child": {"value": 1}}}}

    node = Assignment("Assignment")
    node.identifiers = ["x", "child", "child", "value"]

    expr = Term("Term")
    expr.type = "INTEGER_NUMBER"
    expr.value = "88"
    node.expression = expr

    with patch("evaluator.categories.expression.execute_expression", return_value=(88, self.store.copy())):
        #act
        result = execute_statement(
            node,
            self.env_graph,
            self.env_var,
            self.env_algo,
            self.loc,
            graph_object,
            self.store,
        )

    store, env_var, env_algo, env_graph, value, loc = result

    #assert
    self.assertEqual(graph_object["x"]["child"]["child"]["value"], 88)
    self.assertIsNone(value)
