from parser.ast_builder import *
from evaluator.functions import *
import evaluator.categories.expression

def execute_node_expression(tree_node: ExprNode, env_graph, env_var, env_algo, loc, graph_object: Graph, store):
    if graph_object.graph is not None:
        match tree_node.direction:
            case "---":
                node_identifier, store1 = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(graph_object.graph.neighbors(node_identifier))
            case "-->":
                node_identifier, store1 = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(graph_object.graph.successors(node_identifier))
            case "<--":
                node_identifier, store1 = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(graph_object.graph.predecessors(node_identifier))
            case "<->":
                points_both_ways = []
                node_identifier, store1 = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                successors = list(graph_object.graph.successors(node_identifier))
                predecessors = list(graph_object.graph.predecessors(node_identifier))
                for node in successors:
                    if node in predecessors:
                        points_both_ways.append(node)
                return points_both_ways
    else:
        match tree_node.direction:
            case "---":
                node_identifier, graph_object = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(graph_object.graph.neighbors(node_identifier))
            case "-->":
                node_identifier, graph_object = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(graph_object.graph.successors(node_identifier))
            case "<--":
                node_identifier, graph_object = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(graph_object.graph.predecessors(node_identifier))
            case "<->":
                points_both_ways = []
                node_identifier, graph_object = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                successors = list(graph_object.graph.successors(node_identifier))
                predecessors = list(graph_object.graph.predecessors(node_identifier))
                for node in successors:
                    if node in predecessors:
                        points_both_ways.append(node)
                return points_both_ways