from parser.ast_builder import *
from evaluator.functions import *
import evaluator.categories.expression

def execute_node_expression(tree_node: ExprNode, env_graph, env_var, env_algo, loc, graph_object: Graph, store):
    E = evaluator.categories.expression.ExpressionReturn(None, store, graph_object)
    match tree_node.direction:
        case "---": # (NODE1---) and (NODE2---)
            E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, E.graph_object, store)
            return list(E.graph_object.graph.neighbors(E.v)), E.modified_store
        case "-->": # (NODE-->)
            E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, E.graph_object, store)
            return list(E.graph_object.graph.successors(E.v)), E.modified_store
        case "<--": # (NODE<--)
            E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, E.graph_object, store)
            return list(E.graph_object.graph.predecessors(E.v)), E.modified_store
        case "<->": # (NODE<->)
            points_both_ways = []
            E = evaluator.categories.expression.execute_expression(tree_node.expression, env_graph, env_var, env_algo, loc, E.graph_object, store)
            successors = list(E.graph_object.graph.successors(E.v))
            predecessors = list(E.graph_object.graph.predecessors(E.v))
            for node in successors:
                if node in predecessors:
                    points_both_ways.append(node)
            return points_both_ways, E.modified_store