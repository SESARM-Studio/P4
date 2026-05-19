from parser.ast_builder import *
from evaluator.functions import *
import evaluator.categories.expression

def execute_node_expression(tree_node: ExprNode, env_graph, env_var, env_algo, loc, graph_object: Graph, store):
    if graph_object.graph is not None:
        match tree_node.direction:
            case "---":
                E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(graph_object.graph.neighbors(E.v)), E.modified_store
            case "-->":
                E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(graph_object.graph.successors(E.v)), E.modified_store
            case "<--":
                E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(graph_object.graph.predecessors(E.v)), E.modified_store
            case "<->":
                points_both_ways = []
                E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                successors = list(graph_object.graph.successors(E.v))
                predecessors = list(graph_object.graph.predecessors(E.v))
                for node in successors:
                    if node in predecessors:
                        points_both_ways.append(node)
                return points_both_ways, E.modified_store
    else:
        match tree_node.direction:
            case "---":
                E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(E.graph_object.graph.neighbors(E.v)), E.modified_store
            case "-->":
                E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(E.graph_object.graph.successors(E.v)), E.modified_store
            case "<--":
                E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                return list(E.graph_object.graph.predecessors(E.v)), E.modified_store
            case "<->":
                points_both_ways = []
                E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                successors = list(E.graph_object.graph.successors(E.v))
                predecessors = list(E.graph_object.graph.predecessors(E.v))
                for node in successors:
                    if node in predecessors:
                        points_both_ways.append(node)
                return points_both_ways, E.modified_store