from parser.ast_builder import *
from evaluator.helpers import *
from evaluator.categories.expression import execute_expression

def execute_dimension(node: Declaration, env_graph: dict, env_var: dict, env_algo: dict, loc: Location, graph_object: Graph, store: dict):
    if node.dimension is not None: #DIM1
        E = execute_expression(node.dimension, env_graph, env_var, env_algo, loc, graph_object, store)
        if E.v != 0:
            array = create_dimensional_array(E.v)
            return array

        else:
            raise RuntimeError("Dimension cannot be 0")
    else: #DIM2
        array = create_dimensional_array(1)
        return array
