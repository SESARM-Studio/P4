from parser.ast_builder import *
from evaluator.functions import *
from evaluator.categories.list_declaration import execute_list_declaration, DeclarationReturn

def execute_declaration(node: Declaration | NodeDecl, env_graph: dict, env_var: dict, env_algo: dict, loc: Location, graph_object: Graph, store: dict) -> DeclarationReturn:
    env_graph_copy = env_graph.copy()
    env_var_copy = env_var.copy()
    env_algo_copy = env_algo.copy()
    store_copy = store.copy()

    if isinstance(node, NodeDecl):
        if graph_object.graph is not None:
            # D2NODE
            graph_object.add_nodes(node.identifiers)

            return DeclarationReturn(env_var, store, loc)

    if node.is_list:
        if node.dimension is None:
            # D4
            d_list2 = execute_list_declaration(node, env_graph_copy, env_var_copy, env_algo_copy, loc, graph_object, store_copy)
            return d_list2
        else:
            #D3
            d_list1 = execute_list_declaration(node, env_graph_copy, env_var_copy, env_algo_copy, loc, graph_object, store_copy)
            return d_list1


    else:
        if node.type in ("int", "nat", "real"): #D1

            for iden in node.identifiers:
                env_var_copy.update({iden: loc})
                store_copy.update({env_var_copy.get(iden): 0})
                loc = env_var_copy.get(iden).next_location()

            return DeclarationReturn(env_var_copy, store_copy, loc)

        else: # D2
            if graph_object.graph is None:
                for iden in node.identifiers:
                    env_var_copy.update({iden: loc})
                    loc = env_var_copy.get(iden).next_location()
                return DeclarationReturn(env_var_copy, store, loc)
            else:
                raise RuntimeError("Invalid declaration")