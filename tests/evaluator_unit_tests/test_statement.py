import unittest

from parser.ast_builder import (
    Declaration,
    DeclarationInit,
    Assignment,
    ArrayAccess,
    Term
)

from evaluator.categories.statement import execute_statement
from evaluator.categories.expression import execute_expression
from unittest.mock import patch
from types import SimpleNamespace

class TestStatements(unittest.TestCase):
    def test_declaration(self):
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

        self.assertEqual(env_var["a"], 2)
        self.assertIsNone(value)
        self.assertEqual(loc, 3)

    def test_declaration_init_non_list(self):
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

        self.assertEqual(store[2], 99)
        self.assertEqual(value, None)
        self.assertEqual(loc, 3)

    def test_declaration_init_list(self):
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

        self.assertEqual(store[2], 7)
        self.assertEqual(value, 7)
        self.assertEqual(loc, 3)

    def test_normal_assignment(self):
        node = Assignment("Assignment")
        node.identifiers = ["x"]

        expr = Term("Term")
        expr.type = "INTEGER_NUMBER"
        expr.value = "42"
        node.expression = expr

        with patch("evaluator.categories.expression.execute_expression", return_value=(42, self.store.copy())):
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

        self.assertEqual(store[0], 42)
        self.assertIsNone(value)
        self.assertEqual(loc, self.loc)