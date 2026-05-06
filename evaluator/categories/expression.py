from parser.ast_builder import *

def execute_expression(node: Expression | Term, env_graph, env_var, env_algo, loc, graph_object, store):
    match node:
        case Expression():

            match node.operator:
                case '=':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)
                    return v1 == v2, store2
                case '!=':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)
                    return v1 != v2, store2
                case '<':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)
                    return v1 < v2, store2
                case '>':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)
                    return v1 > v2, store2
                case '<=':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)
                    return v1 <= v2, store2
                case '>=':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)
                    return v1 >= v2, store2
                case '+':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)
                    return v1 + v2, store2
                case '-':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)
                    return v1 - v2, store2

                case _:
                    return execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
        case Term():
            return int(node.value), store

