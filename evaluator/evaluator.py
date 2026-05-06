from parser.ast_builder import *
from .categories import *
from .functions import *

def traverse_program(program: ASTNode):
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    if len(program.children) != 1:
        for child in program.children:
            execute_statement(child, env_graph, env_var, env_algo, loc, graph_object, store)

    print("")