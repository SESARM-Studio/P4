from copy import deepcopy
from parser.ast_builder import *

def execute_algorithm(node: Algorithm, env_graph, env_var, env_algo, loc, graph_object, store):
    match node.token:
        case "Algorithm":
            env_graph_cpy = env_graph.copy()
            env_var_cpy = deepcopy(env_var)
            env_algo_cpy = deepcopy(env_algo)
            env_algo.update({node.identifier: (
                node.parameters,
                node.statements,
                env_graph_cpy,
                env_var_cpy,
                env_algo_cpy)
            })
            return env_algo
        case _:
            print("Error: you are trying to execute something that is not an algorithm")