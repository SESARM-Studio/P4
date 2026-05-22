from parser.ast_builder import *
import math
from copy import deepcopy

import evaluator.categories.statement
from evaluator.categories.statement import ReturnException
import evaluator.categories.node_expression
from evaluator.functions import Graph

class ExpressionReturn():
    def __init__(self, value, store, graph_object=Graph()):
        self.v = value
        self.modified_store = store
        self.graph_object = graph_object


def execute_expression(node: Expression | Term, env_graph, env_var, env_algo, loc, graph_object, store):
    match node:
        case Term():
            match node.type: # (LIT)
                case 'NATURAL_NUMBER':
                    return ExpressionReturn(abs(int(node.value)), store)
                case 'INTEGER_NUMBER':
                    return ExpressionReturn(int(node.value), store)
                case 'REAL_NUMBER':
                    return ExpressionReturn(float(node.value), store)
                case 'TEXT':
                    return ExpressionReturn(str(node.value).strip("\""), store)
                case 'BOOL_VALUE':
                    if node.value == "true":
                        return ExpressionReturn(True, store)
                    else: return ExpressionReturn(False, store)
                case 'IDENTIFIER':
                    if graph_object.graph is not None and node.value == "nodes": #(IDG)
                        return ExpressionReturn(graph_object.get_nodes(), store)
                    else:  # (ID)
                        location = env_var.get(node.value)
                        return ExpressionReturn(store.get(location), store)
                case _:
                    exit("Invalid term type!")

        case AlgorithmCall(): # (cll2)
            argument_values = []
            algorithm_store = deepcopy(store)

            # Retrieve algorithm information.  # (cll1)
            parameters, body_statements, env_graph_old, env_var_old, env_algo_old = env_algo.get(node.identifier)

            # Update algorithm's algorithm store to contain itself to allow recursive calls
            env_algo_old.update({node.identifier: deepcopy(env_algo.get(node.identifier))})

            # Not deep-copying next free location as location object fields are never used.
            free_location = loc

            # If the function call was given arguments # (cll1)
            if node.arguments:
                # Evaluating algorithm arguments
                for argument in node.arguments:

                    E = execute_expression(argument, env_graph, env_var, env_algo, loc, graph_object, algorithm_store)
                    argument_values.append(E.v)
                    algorithm_store = E.modified_store

                # Assign algorithm parameters a location in algorithm's variable environment
                # and then assign algorithm parameters the values passed in as arguments
                env_var_old.update({parameters[0].identifier: free_location})
                E.modified_store.update({free_location: argument_values[0]})

                for idx, parameter in enumerate(parameters[1:], 1):
                    env_var_old.update({parameter.identifier: env_var_old.get(parameters[idx-1].identifier).next_location()})
                    E.modified_store.update({env_var_old.get(parameter.identifier): argument_values[idx]})
                
                free_location = env_var_old.get(parameters[-1].identifier).next_location() # index -1 accesses last element in an array.

            try: 

                for statement in body_statements:
                    algorithm_store, env_var_old, env_var_old, env_graph_old, v, free_location = evaluator.categories.statement.execute_statement(statement, free_location, graph_object, algorithm_store, env_var_old, env_algo_old, env_graph_old)

                return ExpressionReturn(v, algorithm_store)
            except ReturnException as e:
                return ExpressionReturn(e.v, e.store)
        
        case ListExpression(): # (LIST)
            v = []
            for i in node.expressions:
                E = execute_expression(i, env_graph, env_var, env_algo, loc, graph_object, store)
                v.append(E.v)
            return ExpressionReturn(v, E.modified_store)
        
        case AbsoluteValue(): # (ABS)
            E = execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                    
            return ExpressionReturn(abs(E.v), E.modified_store)

        case Magnitude(): # (AG)
            E = execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)

            return ExpressionReturn(len(E.v), E.modified_store)
        
        case IdentifierAccess():
            if env_graph.get(node.identifiers[0]) or env_graph.get(store.get(env_var.get(node.identifiers[0]))): # (DOT)
                graph_object = env_graph.get(node.identifiers[0])
                if len(node.identifiers) == 3:
                    if isinstance(node.identifiers[2], AlgorithmCall): # G.nodes.addattribute()
                        new_term = Term("Term")
                        new_term.type = "IDENTIFIER"
                        new_term.value = node.identifiers[1]
                        E1 = execute_expression(new_term, env_graph, env_var, env_algo, loc, graph_object, store)
                        E2 = execute_expression(node.identifiers[2].arguments[1], env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                        for graph_node in E1.v:
                            graph_object.add_attribute(graph_node, E2.v)
                        v = None
                        return ExpressionReturn(v, E2.modified_store)
                    else: # G.a.SPE
                        v = graph_object.get_node_data(node.identifiers[1],node.identifiers[2])
                        return ExpressionReturn(v, store)
                else: # G.a | G.nodes
                    if node.identifiers[1] == "nodes":
                        new_term = Term("Term")
                        new_term.type = "IDENTIFIER"
                        new_term.value = node.identifiers[1]
                        E = execute_expression(new_term, env_graph, env_var, env_algo, loc, graph_object, store)
                        return ExpressionReturn(E.v, E.modified_store, graph_object)
                    else:
                        v = node.identifiers[1]
                        return ExpressionReturn(v, store, graph_object)
            else: # (DGO)
                if graph_object.graph is not None: # Accessed from foreachEdge
                    location = env_var.get(node.identifiers[0])
                    value = store.get(location)
                    if isinstance(node.identifiers[1], AlgorithmCall): # a.addatribute()
                        E = execute_expression(node.identifiers[1].arguments[1], env_graph, env_var, env_algo, loc, graph_object, store)
                        graph_object.add_attribute(value, E.v)
                        v = None
                        return ExpressionReturn(v, E.modified_store)
                    else: # a.SPE
                        v = graph_object.get_node_data(value,node.identifiers[1])
                        return ExpressionReturn(v, store)
                else:
                    raise Exception("Cant access global node")

        case ArrayAccess(): # (IDX)
            array_location = env_var.get(node.identifier)
            array = list(store.get(array_location))

            # Evaluate given array indices
            access_indices = []

            E = ExpressionReturn(None, store)

            for index in node.indexes:
                E = execute_expression(index, env_graph, env_var, env_algo, loc, graph_object, E.modified_store)
                access_indices.append(E.v)
            
            # Retrieve array element with evaluated indices and retrieved array
            v = array
            for idx in access_indices:
                v = v[idx-1] # -1 as GSL indexes from 1

            return ExpressionReturn(v, E.modified_store)

        case ExprNode(): # (NEX)
            v, store = evaluator.categories.node_expression.execute_node_expression(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return ExpressionReturn(v, store)

        case Expression():
            match node.operator:
                case '=': # (EQ)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v == E2.v, E2.modified_store)
                case '!=': # (NEQ)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v != E2.v, E2.modified_store)
                case '<': # (LT)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v < E2.v, E2.modified_store)
                case '>': # (GT)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v > E2.v, E2.modified_store)
                case '<=': # (LEQ)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v <= E2.v, E2.modified_store)
                case '>=': # (GEQ)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v >= E2.v, E2.modified_store)
                case '+': # (ADD)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v + E2.v, E2.modified_store)

                case '-': # (SUB)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v - E2.v, E2.modified_store)
        
                case '*': # (MUL)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v * E2.v, E2.modified_store)

                case '/': # (DIV)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v / E2.v, E2.modified_store)

                case '%': # (MOD)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v % E2.v, E2.modified_store)
                
                case '^': # (EXP)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(math.pow(E1.v, E2.v), E2.modified_store)
                
                case 'neg': # (NEG)
                    E = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)

                    return ExpressionReturn(not E.v, E.modified_store)

                case 'and': # (AND)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v and E2.v, E2.modified_store)
                
                case 'or': # (OR)
                    E1 = execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
                    E2 = execute_expression(node.arg2, env_graph, env_var, env_algo, loc, graph_object, E1.modified_store)
                    
                    return ExpressionReturn(E1.v or E2.v, E2.modified_store)
                
                case 'weight of':
                    graph_identifier = node.arg1.split(".")[0]
                    graph = env_graph.get(graph_identifier)

                    if "-->" in node.arg1:  # (NWD)
                        node_identifiers = node.arg1.split(".")[1].split("-->")
                    else:  # (NWUD)
                        node_identifiers = node.arg1.split(".")[1].split("---")

                    edge_data = graph.get_edge_data(node_identifiers[0], node_identifiers[1])
                    v = edge_data.get("weight")

                    return ExpressionReturn(v, store)

                case _:
                    return execute_expression(node.arg1, env_graph, env_var, env_algo, loc, graph_object, store)
        
        case _:
            exit("Error: No execute_Expression case match!")
