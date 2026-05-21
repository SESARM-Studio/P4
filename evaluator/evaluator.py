from parser.ast_builder import *
from .categories import *
from .categories.statement import execute_statement
from .categories.expression import execute_expression
from .functions import *
from copy import deepcopy

def traverse_program(program: ASTNode):
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    if len(program.children) != 1:
        for statement in program.children:
            if not statement.token == "EOF":
                store, env_var, env_algo, env_graph, v, loc = execute_statement(statement, loc, graph_object, store, env_var, env_algo, env_graph)