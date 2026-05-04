from abstract_syntax_tree.ast_builder import *
from .categories import *

class Location:
    def __init__(self):
        self.number = 0
        self.name = f"l{self.number}"

    def next_location(self):
        l = Location()
        l.number = self.number + 1
        l.name = f"l{l.number}"
        return l

class Graph:
    pass

def traverse_program(program: ASTNode):
    env_graph = dict()
    env_var = dict()
    env_algo = dict()
    loc = Location()
    graph_object = Graph()
    store = dict()

    if len(program.children) != 1:
        for child in program.children:
            execute_statement(child, None, None, None, None, None, None)





