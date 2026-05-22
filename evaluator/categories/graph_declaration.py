from parser.ast_builder import *
from evaluator.functions import *
import evaluator.categories.declaration
import evaluator.categories.edge_declaration

def execute_graph_decl(tree_node: GraphDecl, env_var, env_algo, loc, env_graph, graph_object: Graph, store):
    if tree_node.nodes == [] and tree_node.edges == []:
        if tree_node.weight_type is None: # (DGRAPH1)
            graph_object = Graph()
            graph_object.create_graph(tree_node.graph_type)

            env_graph.update({tree_node.identifier: graph_object})

            graph_object = Graph()

            return env_graph, store
        else: # (DGRAPH2)
            graph_object = Graph()
            graph_object.create_graph(tree_node.graph_type)

            env_graph.update({tree_node.identifier: graph_object})

            graph_object = Graph()

            return env_graph, store
    else:
        if tree_node.weight_type is None: # (DGRAPH3)
            graph_object = Graph()
            graph_object.create_graph(tree_node.graph_type)
            
            for node in tree_node.nodes:
                evaluator.categories.declaration.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            
            for edge in tree_node.edges:
                evaluator.categories.edge_declaration.execute_edge_declaration(edge, env_graph, env_var, env_algo, loc, graph_object, store)
            
            env_graph.update({tree_node.identifier: graph_object})

            graph_object = Graph()

            return env_graph, store
        else: # (DGRAPH4)
            graph_object = Graph()
            graph_object.create_graph(tree_node.graph_type)
            
            for node in tree_node.nodes:
                evaluator.categories.declaration.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            
            for edge in tree_node.edges:
                evaluator.categories.edge_declaration.execute_edge_declaration(edge, env_graph, env_var, env_algo, loc, graph_object, store)
            
            env_graph.update({tree_node.identifier: graph_object})

            graph_object = Graph()

            return env_graph, store