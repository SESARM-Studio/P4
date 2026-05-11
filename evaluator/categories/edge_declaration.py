from parser.ast_builder import *
from evaluator.functions import *
import evaluator.categories.expression

def execute_edge_declaration(tree_node: EdgeDecl, env_graph, env_var, env_algo, loc, graph_object: Graph, store):
    if tree_node.weight != []:
        match tree_node.direction:
            case "---":
                # We add edges as an array of edge tuples e.g. [("a","b")] or [("a", "b", 3)]
                added_edges = []
                left_to_right = True
                get_edges_to_add(tree_node, env_graph, env_var, env_algo, loc, graph_object, store, added_edges, left_to_right)
                if graph_object.graph is not None:
                    graph_object.add_weighted_edges(added_edges)
                return added_edges
                
            case "-->":
                added_edges = []
                left_to_right = True
                get_edges_to_add(tree_node, env_graph, env_var, env_algo, loc, graph_object, store, added_edges, left_to_right)
                if graph_object.graph is not None:
                    graph_object.add_weighted_edges(added_edges)
                return added_edges

            case "<--":
                added_edges = []
                left_to_right = False
                get_edges_to_add(tree_node, env_graph, env_var, env_algo, loc, graph_object, store, added_edges, left_to_right)
                if graph_object.graph is not None:
                    graph_object.add_weighted_edges(added_edges)
                return added_edges

            case "<->":
                added_edges = []
                for left_to_right in [True, False]:
                    get_edges_to_add(tree_node, env_graph, env_var, env_algo, loc, graph_object, store, added_edges, left_to_right)                
                if graph_object.graph is not None:
                    graph_object.add_weighted_edges(added_edges)
                return added_edges
                
    else:
        match tree_node.direction:
            case "---":
                added_edges = []
                left_to_right = True
                get_edges_to_add(tree_node, env_graph, env_var, env_algo, loc, graph_object, store, added_edges, left_to_right)
                if graph_object.graph is not None:
                    graph_object.add_edges(added_edges)
                return added_edges
            
            case "-->":
                added_edges = []
                left_to_right = True
                get_edges_to_add(tree_node, env_graph, env_var, env_algo, loc, graph_object, store, added_edges, left_to_right)
                if graph_object.graph is not None:
                    graph_object.add_edges(added_edges)
                return added_edges

            case "<--":
                added_edges = []
                left_to_right = False
                get_edges_to_add(tree_node, env_graph, env_var, env_algo, loc, graph_object, store, added_edges, left_to_right)
                if graph_object.graph is not None:
                    graph_object.add_weighted_edges(added_edges)
                return added_edges

            case "<->":
                added_edges = []
                for left_to_right in [True, False]:    
                    get_edges_to_add(tree_node, env_graph, env_var, env_algo, loc, graph_object, store, added_edges, left_to_right)
                if graph_object.graph is not None:
                    graph_object.add_edges(added_edges)
                return added_edges
            
def get_edges_to_add(tree_node: EdgeDecl, env_graph, env_var, env_algo, loc, graph_object: Graph, store, added_edges, left_to_right):
    for index, node in enumerate(tree_node.nodes):
        edge = []
        if left_to_right is True:
            if isinstance(tree_node.initial_node, Expression):
                edge.append(evaluator.categories.expression.execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
            else:
                edge.append(tree_node.initial_node)
            if isinstance(node, Expression):
                edge.append(evaluator.categories.expression.execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store))
            else:
                edge.append(node)
        else:
            if isinstance(node, Expression):
                edge.append(evaluator.categories.expression.execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store))
            else:
                edge.append(node)
            if isinstance(tree_node.initial_node, Expression):
                edge.append(evaluator.categories.expression.execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
            else:
                edge.append(tree_node.initial_node)
        if tree_node.weight != []:
            value, store = evaluator.categories.expression.execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store)
            edge.append(value)
        added_edges.append(tuple(edge))
    return added_edges
