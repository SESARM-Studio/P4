from parser.ast_builder import *
from evaluator.functions import *
from evaluator.categories.declaration import *
from evaluator.categories.edge_declaration import *

def execute_graph_decl(tree_node: GraphDecl, env_graph, env_var, env_algo, loc, graph_object: Graph, store):
    if tree_node.weight_type is not None:
        if tree_node.nodes != [] or tree_node.edges != []:
            graph_object = Graph()
            graph_object.create_graph(tree_node.graph_type)
            
            for node in tree_node.nodes:
                execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            
            for edge in tree_node.edges:
                execute_edge_declaration(edge, env_graph, env_var, env_algo, loc, graph_object, store)
            
            env_graph.update({tree_node.identifier: graph_object})

            graph_object = Graph()

            return env_graph, store
        else:
            graph_object = Graph()
            graph_object.create_graph(tree_node.graph_type)

            env_graph.update({tree_node.identifier: graph_object})

            graph_object = Graph()

            return env_graph, store
    else:
        if tree_node.nodes != [] or tree_node.edges != []:
            graph_object = Graph()
            graph_object.create_graph(tree_node.graph_type)
            
            for node in tree_node.nodes:
                execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            
            for edge in tree_node.edges:
                execute_edge_declaration(edge, env_graph, env_var, env_algo, loc, graph_object, store)
            
            env_graph.update({tree_node.identifier: graph_object})

            graph_object = Graph()

            return env_graph, store
        else:
            graph_object = Graph()
            graph_object.create_graph(tree_node.graph_type)

            env_graph.update({tree_node.identifier: graph_object})

            graph_object = Graph()

            return env_graph, store
                
