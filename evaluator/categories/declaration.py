from parser.ast_builder import *
from evaluator.functions import *
from .expression import execute_expression
from typing import NamedTuple

class DeclarationReturn(NamedTuple):
    env_var: dict
    store: dict
    location: Location

def execute_declaration(node: Declaration | NodeDecl, env_graph: dict, env_var: dict, env_algo: dict, loc: Location, graph_object: Graph, store: dict) -> DeclarationReturn:
    env_graph_copy = env_graph.copy()
    env_var_copy = env_var.copy()
    env_algo_copy = env_algo.copy()
    store_copy = store.copy()

    if isinstance(node, NodeDecl):
        if graph_object.graph is not None:
            # d2 node node I (med mulighed for flere I'er) - Dette er for notes inde i grafer
            graph_object.add_nodes(node.identifiers)

            return DeclarationReturn(env_var, store, loc)

    if node.is_list:
        if node.dimension is None:
            # d4 (I list in T)
            d_list2 = execute_list_declaration(node, env_graph_copy, env_var_copy, env_algo_copy, loc, graph_object, store_copy)
            return d_list2
        else:
            #d3 (I DIM list in T)
            d_list1 = execute_list_declaration(node, env_graph_copy, env_var_copy, env_algo_copy, loc, graph_object, store_copy)
            return d_list1


    else:
        if node.type in ("int", "nat", "real"):
            #d1 I in T (med mulighed for flere I'er)
            for iden in node.identifiers:
                env_var_copy.update({iden: loc})
                store_copy.update({env_var_copy.get(iden): 0})
                loc = env_var_copy.get(iden).next_location()

            return DeclarationReturn(env_var_copy, store_copy, loc)

        else:
            if graph_object.graph is None:

                for iden in node.identifiers:
                    env_var_copy.update({iden: loc})
                    loc = env_var_copy.get(iden).next_location()
                return DeclarationReturn(env_var_copy, store, loc)
            else:
                raise RuntimeError("Invalid declaration")


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



def execute_dimension(node: Declaration, env_graph: dict, env_var: dict, env_algo: dict, loc: Location, graph_object: Graph, store: dict):
    # dDim
    v, _ = execute_expression(node.dimension, env_graph, env_var, env_algo, loc, graph_object, store)
    if v != 0:
        a = create_dimensional_array(v)
        return a

    else:
        raise RuntimeError("Dimension cannot be 0")

