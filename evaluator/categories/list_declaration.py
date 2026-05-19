from parser.ast_builder import *
from evaluator.functions import *
from evaluator.categories.dimension import execute_dimension
from typing import NamedTuple

class DeclarationReturn(NamedTuple):
    env_var: dict
    store: dict
    location: Location


def execute_list_declaration(node: Declaration, env_graph: dict, env_var: dict, env_algo: dict, loc: Location, graph_object: Graph, store: dict) -> DeclarationReturn:
    if len(node.identifiers) > 1: # Redundant? Possibly
        raise RuntimeError("Can only declare one array at a time")

    env_graph_copy = env_graph.copy()
    loc = loc.copy()
    env_var_copy = env_var.copy()
    env_algo_copy = env_algo.copy()
    store_copy = store.copy()

    if node.dimension is None:
        # dList2 I list in T
        a = create_dimensional_array(1)
        env_var_copy.update({node.identifiers[0]: loc})
        store_copy.update({loc: a})
        loc = loc.next_location()

        return DeclarationReturn(env_var_copy, store_copy, loc)

    else:
        # dList1 I DIM list in T
        a = execute_dimension(node, env_graph_copy, env_var_copy, env_algo_copy, loc, graph_object, store_copy)
        env_var_copy.update({node.identifiers[0]: loc})
        store_copy.update({loc: a})
        loc = loc.next_location()

        return DeclarationReturn(env_var_copy, store_copy, loc)
