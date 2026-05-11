from parser.ast_builder import *
from evaluator.functions import *
import evaluator.categories.edge_declaration

def execute_graph_statement(tree_node: GraphStatement, env_graph, env_var, env_algo, loc, graph_object: Graph, store):
    match tree_node.operator:
        case "add":
            match tree_node.argument:
                case EdgeDecl():
                    if isinstance(env_graph.get(tree_node.graph_identifier), Graph):
                        graph = env_graph.get(tree_node.graph_identifier)
                        if tree_node.argument.weight != []:
                            graph.add_weighted_edges(evaluator.categories.edge_declaration.execute_edge_declaration(tree_node.argument, env_graph, env_var, env_algo, loc, graph_object=Graph(), store = store))
                        else:
                            graph.add_edges(evaluator.categories.edge_declaration.execute_edge_declaration(tree_node.argument, env_graph, env_var, env_algo, loc, graph_object=Graph(), store = store))
                    else:
                        print("Cant add edge to not graph object")

                case Declaration():
                    # Dont need to parse this to executre_declaration because we are only interested in the identifier.
                    if isinstance(env_graph.get(tree_node.graph_identifier), Graph):
                        graph = env_graph.get(tree_node.graph_identifier)
                        graph.add_node(tree_node.argument.identifiers[0])
                    else:
                        print("Cant add node to not graph object")

        case "remove":
            match tree_node.argument:
                case EdgeDecl():
                    if isinstance(env_graph.get(tree_node.graph_identifier), Graph):
                        graph = env_graph.get(tree_node.graph_identifier)
                        edges_to_remove = evaluator.categories.edge_declaration.execute_edge_declaration(tree_node.argument, env_graph, env_var, env_algo, loc, graph_object=Graph(), store = store)
                        for edge in edges_to_remove:
                            graph.remove_edge(edge[0], edge[1])
                    else:
                        print("Cant remove edge from not graph object")

                case Declaration():
                    # Dont need to parse this to executre_declaration because we are only interested in the identifier.
                    if isinstance(env_graph.get(tree_node.graph_identifier), Graph):
                        graph = env_graph.get(tree_node.graph_identifier)
                        graph.remove_node(tree_node.argument.identifiers[0])
                    else:
                        print("Can't remove node from not graph object")