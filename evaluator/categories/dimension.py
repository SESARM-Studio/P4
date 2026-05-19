from parser.ast_builder import *
from evaluator.functions import *
from evaluator.categories.expression import execute_expression

def execute_dimension(node: Declaration, env_graph: dict, env_var: dict, env_algo: dict, loc: Location, graph_object: Graph, store: dict):
    # dDim
    E = execute_expression(node.dimension, env_graph, env_var, env_algo, loc, graph_object, store)
    if E.v != 0:
        a = create_dimensional_array(E.v)
        return a

    else:
        raise RuntimeError("Dimension cannot be 0")

