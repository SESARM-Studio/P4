from parser.ast_builder import *
from evaluator.helpers import *
import evaluator.categories.edge_declaration
from exceptions.evaluator_exception import EvaluatorException

def execute_graph_statement(tree_node: GraphStatement, env_graph, env_var, env_algo, loc, graph_object: Graph, store):
    match tree_node.operator:
        case "add":
            match tree_node.argument:
                case Declaration():
                    # Dont need to parse this to execute_declaration because we are not declaring new nodes.
                    if not env_var.get(tree_node.argument.identifiers[0]): # (ADD-NODE1)
                        if isinstance(env_graph.get(tree_node.graph_identifier), Graph):
                            g = env_graph.get(tree_node.graph_identifier)
                            g.add_node(tree_node.argument.identifiers[0])
                        else:
                            raise EvaluatorException("Cant add node to not graph object", tree_node)
                    else:
                        location = env_var.get(tree_node.argument.identifiers[0])
                        value = store.get(location)
                        if isinstance(env_graph.get(tree_node.graph_identifier), Graph):
                            g = env_graph.get(tree_node.graph_identifier)
                            g.add_node(value)
                        else:
                            raise EvaluatorException("Cant add node to not graph object", tree_node)

                case EdgeDecl(): # (ADD-EDGE)
                    if isinstance(env_graph.get(tree_node.graph_identifier), Graph):
                        g = env_graph.get(tree_node.graph_identifier)
                        if tree_node.argument.weight != []:
                            edges, store = evaluator.categories.edge_declaration.execute_edge_declaration(tree_node.argument, env_graph, env_var, env_algo, loc, graph_object=Graph(), store = store)
                            g.add_weighted_edges(edges)
                        else:
                            edges, store = evaluator.categories.edge_declaration.execute_edge_declaration(tree_node.argument, env_graph, env_var, env_algo, loc, graph_object=Graph(), store = store)
                            g.add_edges(edges)
                    else:
                        raise EvaluatorException("Cant add edge to not graph object", tree_node)

        case "remove":
            match tree_node.argument:
                case Declaration(): # (REMOVE-NODE)
                    # Dont need to parse this to executre_declaration because we are only interested in the identifier.
                    if isinstance(env_graph.get(tree_node.graph_identifier), Graph):
                        g = env_graph.get(tree_node.graph_identifier)
                        g.remove_node(tree_node.argument.identifiers[0])
                    else:
                        raise EvaluatorException("Can't remove node from not graph object", tree_node)

                case EdgeDecl(): # (REMOVE-EDGE)
                    if isinstance(env_graph.get(tree_node.graph_identifier), Graph):
                        g = env_graph.get(tree_node.graph_identifier)
                        edges_to_remove, store = evaluator.categories.edge_declaration.execute_edge_declaration(tree_node.argument, env_graph, env_var, env_algo, loc, graph_object=Graph(), store = store)
                        for removed_edge in edges_to_remove:
                            g.remove_edge(removed_edge[0], removed_edge[1]) #removed_edge is a tuple e.g. ("a", "b") so [0] = "a" [1] = "b"
                    else:
                        raise EvaluatorException("Cant remove edge from not graph object", tree_node)

                