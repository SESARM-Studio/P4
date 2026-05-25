from parser.ast_builder import *
from evaluator.helpers import *
import evaluator.categories.expression

def execute_edge_declaration(ast_node: EdgeDecl, env_graph, env_var, env_algo, loc, graph_object: Graph, store):
    if ast_node.weight == []:
        if graph_object.graph is None:
            match ast_node.direction:
                case "---": # (EDGE---)1
                    # We add edges as an array of edge tuples e.g. [("a","b")] or [("a", "b", 3)]
                    direction = "undirected"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    return edges_to_add, modified_store
                    
                case "-->": # (EDGE-->)1
                    direction = "left_to_right"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    return edges_to_add, modified_store

                case "<--": # (EDGE<--)1
                    direction = "right_to_left"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    return edges_to_add, modified_store

                case "<->": # (EDGE<->)1
                    edges_to_add = [] # Creating the array here and append the result of get_edges_to_add() because edge could be a <-> b weight 10 so edges_to_add should be [(a,b,10), (b,a,10)]
                    modified_store = store
                    for direction in ["left_to_right", "right_to_left"]: # get_edges_t_add returns an array of tuples in one direction so .extend is needed to only get the tuples.
                        directional_edges, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, modified_store, direction)        
                        edges_to_add.extend(directional_edges)
                    return edges_to_add, modified_store
        else:
            match ast_node.direction:
                case "---": # (EDGE---)2
                    direction = "undirected"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    graph_object.add_edges(edges_to_add)
                    return edges_to_add, modified_store
                
                case "-->": # (EDGE-->)2
                    direction = "left_to_right"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    graph_object.add_edges(edges_to_add)
                    return edges_to_add, modified_store

                case "<--": # (EDGE<--)2
                    direction = "right_to_left"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    graph_object.add_edges(edges_to_add)
                    return edges_to_add, modified_store

                case "<->": # (EDGE<->)2
                    edges_to_add = [] # Creating the array here and append the result of get_edges_to_add() because edge could be a <-> b weight 10 so edges_to_add should be [(a,b,10), (b,a,10)]
                    modified_store = store
                    for direction in ["left_to_right", "right_to_left"]: # get_edges_t_add returns an array of tuples in one direction so .extend is needed to only get the tuples.
                        directional_edges, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, modified_store, direction)    
                        edges_to_add.extend(directional_edges)
                    graph_object.add_edges(edges_to_add)
                    return edges_to_add, modified_store

    else:
        if graph_object.graph is None:
            match ast_node.direction:
                case "---": # (EDGE---)_weight1
                    direction = "undirected"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    return edges_to_add, modified_store
                
                case "-->": # (EDGE-->)_weight1
                    direction = "left_to_right"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    return edges_to_add, modified_store

                case "<--": # (EDGE<--)_weight1
                    direction = "right_to_left"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    return edges_to_add, modified_store

                case "<->": # (EDGE<->)_weight1
                    edges_to_add = [] # Creating the array here and append the result of get_edges_to_add() because edge could be a <-> b weight 10 so edges_to_add should be [(a,b,10), (b,a,10)]
                    modified_store = store
                    for direction in ["left_to_right", "right_to_left"]: # get_edges_t_add returns an array of tuples in one direction so .extend is needed to only get the tuples.
                        directional_edges, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, modified_store, direction)                
                        edges_to_add.extend(directional_edges)
                    return edges_to_add, modified_store
        else:
            match ast_node.direction:
                case "---": # (EDGE---)_weight2
                    # We add edges as an array of edge tuples e.g. [("a","b")] or [("a", "b", 3)]
                    direction = "undirected"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    graph_object.add_weighted_edges(edges_to_add)
                    return edges_to_add, modified_store
                    
                case "-->": # (EDGE-->)_weight2
                    direction = "left_to_right"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    graph_object.add_weighted_edges(edges_to_add)
                    return edges_to_add, modified_store

                case "<--": # (EDGE<--)_weight2
                    direction = "right_to_left"
                    edges_to_add, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, store, direction)
                    graph_object.add_weighted_edges(edges_to_add)
                    return edges_to_add, modified_store

                case "<->": # (EDGE<->)_weight2
                    edges_to_add = [] # Creating the array here and append the result of get_edges_to_add() because edge could be a <-> b weight 10 so edges_to_add should be [(a,b,10), (b,a,10)]
                    modified_store = store
                    for direction in ["left_to_right", "right_to_left"]: # get_edges_t_add returns an array of tuples in one direction so .extend is needed to only get the tuples.
                        directional_edges, modified_store = get_edges_to_add(ast_node, env_graph, env_var, env_algo, loc, graph_object, modified_store, direction)          
                        edges_to_add.extend(directional_edges)
                    graph_object.add_weighted_edges(edges_to_add)
                    return edges_to_add, modified_store
            
def get_edges_to_add(tree_node: EdgeDecl, env_graph, env_var, env_algo, loc, graph_object: Graph, store, direction):
    added_edges = []
    E = evaluator.categories.expression.ExpressionReturn(None, store, graph_object)
    for index, node in enumerate(tree_node.nodes):
        edge = []
        match direction:
            case "left_to_right" | "undirected":
                edge.append(tree_node.initial_node)
                edge.append(node)
            case "right_to_left":
                edge.append(node)
                edge.append(tree_node.initial_node)
        if tree_node.weight != []:
            E = evaluator.categories.expression.execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, E.modified_store)
            edge.append(E.v)
        added_edges.append(tuple(edge))
    return added_edges, E.modified_store
