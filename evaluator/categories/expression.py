from parser.ast_builder import *
import math
from copy import deepcopy

import evaluator.categories.statement

def execute_expression(node: Expression | Term, env_graph, env_var, env_algo, loc, graph_object, store):
    match node:
        case Term():
            match node.type:
                case 'NATURAL_NUMBER':
                    return abs(int(node.value)), store
                case 'INTEGER_NUMBER':
                    return int(node.value), store
                case 'REAL_NUMBER':
                    return float(node.value), store
                case 'TEXT':
                    return str(node.value).strip("\""), store
                case 'BOOL_VALUE':
                    if node.value == "true":
                        return True, store
                    else: return False, store
                case 'IDENTIFIER':
                    if graph_object.graph is not None:
                        if node.value == "nodes":
                            return graph_object.get_nodes(), store
                        else:
                            return node.value, store
                    else:      
                        location = env_var.get(node.value)
                        return store.get(location), store
                case _:
                    exit("Invalid term type!")
        case AlgorithmCall():
            argument_values = []
            algorithm_store = deepcopy(store)

            # Retrieve algorithm information
            parameters, body_statement, env_graph_old, env_var_old, env_algo_old = env_algo.get(node.identifier)

            # Update algorithm's algorithm store to contain itself to allow recursive calls
            env_algo_old.update({node.identifier: deepcopy(env_algo.get(node.identifier))})

            # Not deep-copying next free location as location object fields are never used.
            free_location = loc

            # If the function call was given arguments
            if node.arguments:
                # Evaluating algorithm arguments
                for argument in node.arguments:
                    v, algorithm_store = execute_expression(argument, env_graph, env_var, env_algo, loc, graph_object, algorithm_store)
                    argument_values.append(v)

                # Assign algorithm parameters a location in algorithm's variable environment
                # Assign algorithm parameters the values passed in as arguments
                for idx, parameter in enumerate(parameters):
                    if idx == 0:
                        env_var_old.update({parameter.identifier: loc})
                        algorithm_store.update({loc: argument_values[0]})
                    else:
                        env_var_old.update({parameter.identifier: env_var_old.get(parameters[idx-1].identifier).next_location()})
                        algorithm_store.update({env_var_old.get(parameter.identifier): argument_values[idx]})
                
                free_location = env_var_old.get(parameters[-1].identifier).next_location() # index -1 accesses last element in an array.

            store_body, env_var_body, env_algo_body, env_graph_body, v, loc_body = evaluator.categories.statement.execute_statement(body_statement[0],free_location, graph_object, algorithm_store, env_var_old, env_algo_old, env_graph_old)

            for statement in body_statement[1:]:
                store_body, env_var_body, env_algo_body, env_graph_body, v, loc_body = evaluator.categories.statement.execute_statement(statement,loc_body, graph_object, store_body, env_var_body, env_algo_body, env_graph_body)

            return v,store_body
        
        case ListExpression():
            v2 = []
            for i in node.expressions:
                v1, store1 = execute_expression(i, env_graph, env_var, env_algo, loc, graph_object, store)
                v2.append(v1)
            return v2, store1
        
        case AbsoluteValue():
            v, store1 = execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                    
            return abs(v), store1

        case Magnitude():
            v, store1 = execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)

            return len(v), store1
        
        case IdentifierAccess():
            object_identifier = node.identifiers[0]   # I
            field_identifier = node.identifiers[1]    # X
            # outside any graph object (go_inside = empty)
            if graph_object is None:
                go = env_graph.get(object_identifier)

                if go is None:
                    raise RuntimeError(f"Unknown graph object: {object_identifier}")
            
                field_loc = env_var.get(f"{go}.{field_identifier}")
            else:
                field_loc = env_var.get(f"{graph_object}.{field_identifier}")

                if field_loc is None:
                    raise RuntimeError(f"Unknown Node: {field_identifier}")

            return store.get(field_loc), store

        case ArrayAccess():
            array_location = env_var.get(node.identifier)
            array = store.get(array_location)

            # Evaluate given array indices
            access_indices = []
            idx_value, idx_store = execute_expression(node.indexes[0], env_graph, env_var, env_algo, loc, graph_object, store)
            access_indices.append(idx_value)

            for index in node.indexes[1:]:
                idx_value, idx_store = execute_expression(index, env_graph, env_var, env_algo, loc, graph_object, idx_store)
                access_indices.append(idx_value)

            # Retrieve array element with evaluated indices and retrieved array
            v = array
            for idx in access_indices:
                v = v[idx-1] # -1 as GSL indexes from 1

            return v, idx_store

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

                case 'and':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)

                    return v1 and v2
                
                case 'and':
                    v1, store1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    v2, store2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, store1)

                    return v1 or v2
                
                case 'weight of':
                    graph_identifier = node.arg1.split(".")[0]
                    graph = env_graph.get(graph_identifier)

                    if node.arg1.count("-->") > 0:
                        node_identifiers = node.arg1.split(".")[1].split("-->")
                    else:
                        node_identifiers = node.arg1.split(".")[1].split("---")

                    edge_data = graph.get_edge_data(node_identifiers[0], node_identifiers[1])
                    v = edge_data.get("weight")

                    return v, store

                case _:
                    return execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
        
        case _:
            exit("Error: No execute_Expression case match!")
