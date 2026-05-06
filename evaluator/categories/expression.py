from parser.ast_builder import *
import math

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
        
                case '*':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)

                    return v1 * v2, store2

                case '/':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)

                    return v1 / v2, store2

                case '%':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)

                    return v1 % v2, store2
                
                case '^':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)

                    return math.pow(v1,v2), store2
                
                case 'neg':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)

                    return not v1, store1

                case _:
                    print("øv:")
                    return execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                
        case Term():
            match node.type:
                case 'NATURAL_NUMBER':
                    return abs(int(node.value)), store
                case 'INTEGER_NUMBER':
                    return int(node.value), store
                case 'REAL_NUMBER':
                    return float(node.value), store
                case 'TEXT':
                    return str(node.value), store
                case 'BOOL_VALUE':
                    if node.value == "true":
                        return True, store
                    else: return False, store
                case _:
                    exit("Invalid term type!")