from parser.ast_builder import *
from .categories import *
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
        for child in program.children:
            if not child.token == "EOF":
                store, env_var, env_algo, env_graph, v, loc = execute_statement(child, loc, graph_object, store, env_var, env_algo, env_graph)

    print("")