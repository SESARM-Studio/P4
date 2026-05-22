from parser.ast_builder import *
from evaluator.functions import *
from evaluator.categories.dimension import execute_dimension
from typing import NamedTuple
from copy import deepcopy

class DeclarationReturn(NamedTuple):
    env_var: dict
    store: dict
    location: Location


def execute_list_declaration(node: Declaration, env_graph: dict, env_var: dict, env_algo: dict, loc: Location, graph_object: Graph, store: dict) -> DeclarationReturn:
    env_graph_copy = env_graph.copy()
    env_var_copy = deepcopy(env_var)
    env_algo_copy = deepcopy(env_algo)

    # DLIST
    array = execute_dimension(node, env_graph_copy, env_var_copy, env_algo_copy, loc, graph_object, store)
    env_var_copy.update({node.identifiers[0]: loc})
    store.update({loc: array})
    loc = loc.next_location()

    return DeclarationReturn(env_var_copy, store, loc)
