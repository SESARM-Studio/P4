from parser.ast_builder import *
from evaluator.functions import *
from evaluator.categories.expression import *

def execute_edge_declaration(tree_node: EdgeDecl, env_graph, env_var, env_algo, loc, graph_object: Graph, store):
    print(vars(tree_node))
    if tree_node.weight != []:
        if graph_object.graph is not None:
            match tree_node.direction:
                case "---":
                    added_edges = []

                    for index, node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(node, Expression):
                            edge.append(execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))
                    graph_object.add_weighted_edges(added_edges)
                    return added_edges
                
                case "-->":
                    added_edges = []
                    for index, dst_node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(dst_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(dst_node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))
                    graph_object.add_weighted_edges(added_edges)
                    return added_edges

                case "<--":
                    added_edges = []
                    for index, src_node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(src_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(src_node)
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))
                    graph_object.add_weighted_edges(added_edges)
                    return added_edges

                case "<->":
                    added_edges = []
                    for index, node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))

                        edge = []
                        if isinstance(node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))
                    graph_object.add_weighted_edges(added_edges)
                    return added_edges
                
        else:
            match tree_node.direction:
                case "---":
                    added_edges = []
                    for index, node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(node, Expression):
                            edge.append(execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))
                    return added_edges
                
                case "-->":
                    added_edges = []
                    for index, dst_node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(dst_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(dst_node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))
                    return added_edges

                case "<--":
                    added_edges = []
                    for index, src_node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(src_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(src_node)
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))
                    return added_edges

                case "<->":
                    added_edges = []
                    for index, node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))

                        edge = []
                        if isinstance(node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        edge.append(execute_expression(tree_node.weight[index], env_graph, env_var, env_algo, loc, graph_object, store))
                        added_edges.append(tuple(edge))
                    return added_edges
                
    else:
        if graph_object.graph is not None:
            match tree_node.direction:
                case "---":
                    added_edges = []
                    for index, node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(node, Expression):
                            edge.append(execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        added_edges.append(tuple(edge))
                    graph_object.add_edges(added_edges)
                    return added_edges
                
                case "-->":
                    added_edges = []
                    for index, dst_node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(dst_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(dst_node)
                        added_edges.append(tuple(edge))
                    graph_object.add_edges(added_edges)
                    return added_edges

                case "<--":
                    added_edges = []
                    for index, src_node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(src_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(src_node)
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        added_edges.append(tuple(edge))
                    graph_object.add_edges(added_edges)
                    return added_edges

                case "<->":
                    added_edges = []
                    for index, node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        added_edges.append(tuple(edge))

                        edge = []
                        if isinstance(node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        added_edges.append(tuple(edge))
                    graph_object.add_edges(added_edges)
                    return added_edges
                
        else:
            match tree_node.direction:
                case "---":
                    added_edges = []
                    for index, node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(node, Expression):
                            edge.append(execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        added_edges.append(tuple(edge))
                    return added_edges
                
                case "-->":
                    added_edges = []
                    for index, dst_node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(dst_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(dst_node)
                        added_edges.append(tuple(edge))
                    return added_edges

                case "<--":
                    added_edges = []
                    for index, src_node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(src_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(src_node)
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        added_edges.append(tuple(edge))
                    return added_edges

                case "<->":
                    added_edges = []
                    for index, node in enumerate(tree_node.nodes):
                        edge = []
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        if isinstance(node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        added_edges.append(tuple(edge))

                        edge = []
                        if isinstance(node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(node)
                        if isinstance(tree_node.initial_node, Expression):
                            edge.append(execute_expression(tree_node.initial_node, env_graph, env_var, env_algo, loc, graph_object, store))
                        else:
                            edge.append(tree_node.initial_node)
                        added_edges.append(tuple(edge))
                    return added_edges



