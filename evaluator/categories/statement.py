from parser.ast_builder import *
from copy import deepcopy

import evaluator.categories.algorithm
import evaluator.categories.expression
import evaluator.categories.declaration
import evaluator.categories.graph_declaration

def execute_statement(node: ASTNode, loc, graph_object, store, env_var, env_algo, env_graph):
    match node:
        case DeclarationInit():
            # dec-ass
            if len(node.expression) > 1:
                raise RuntimeError("Can only assign to 1 expression")

            store_copy = store.copy()
            env_var_copy = env_var.copy()

            v, store_copy = evaluator.categories.execute_expression(node.expression[0], env_graph, env_var_copy, env_algo, loc, graph_object, store_copy)
            D = evaluator.categories.declaration.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            env_var_copy = D.env_var
            store_copy = D.store
            loc_prime = D.location

            store_copy.update({loc: v})

            return store_copy, env_var_copy, env_algo, env_graph, None, loc_prime

        case Declaration():
            D = evaluator.categories.declaration.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return D.store, D.env_var, env_algo, env_graph, None, D.location

        case Assignment():
            if len(node.identifiers) > 1:
                raise RuntimeError("Can only assign one identifier at a time")
            # ass

            print("Hejsa")
            #list-ass


            print(node)
            #if node.children[0].token == 'ArrayAccess':
            #    print(node.children[0].children[0].token, "Array")

        case IfStatement():
            copy_store = deepcopy(store)
            expression, copy_store = evaluator.categories.expression.execute_expression(node.condition, loc, graph_object, store, env_var, env_algo, env_graph) 
            match expression:
                case True:
                    for i in node.then_statements:
                        store, env_var, env_algo, env_graph, v, loc = execute_statement(i, loc, graph_object, copy_store, env_var, env_algo, env_graph)
                    return store, env_var, env_algo, env_graph, v, loc
                case False:
                    match node.else_statements:
                        case []:
                            return store, env_var, env_algo, env_graph, None, loc
                        case node.else_statements:
                            for i in node.else_statements:
                                store, env_var, env_algo, env_graph, v, loc = execute_statement(i, loc, graph_object, copy_store, env_var, env_algo, env_graph)
                            return store, env_var, env_algo, env_graph, v, loc                              

        case WhileStatement():
            copy_store = deepcopy(store)
            expression, copy_store = evaluator.categories.expression.execute_expression(node.condition, loc, graph_object, store, env_var, env_algo, env_graph)
            match expression:
                case True:
                    for i in node.statements:
                        store, env_var, env_algo, env_graph, v, loc = execute_statement(i, loc, graph_object, copy_store, env_var, env_algo, env_graph)
                    execute_statement(node, loc, graph_object, copy_store, env_var, env_algo, env_graph)
                case False:
                    return store, env_var, env_algo, env_graph, None, loc
        case ForEachNormal():
            pass

        case ForEachEdge():
            pass

        case RepeatStatement():
            copy_env_var = deepcopy(env_var)
            copy_env_algo = deepcopy(env_algo)
            copy_env_graph = deepcopy(env_graph)
            copy_loc = deepcopy(loc)
            v, modified_store = evaluator.categories.expression.execute_expression(node.repeat_expression, env_graph, env_var, env_algo, loc, graph_object, store)
            
            if v > 0:
                while v > 0:
                    for statement in node.repeat_statements:
                        modified_store, env_var, env_algo, env_graph, modified_v, loc  = execute_statement(statement, loc, graph_object, modified_store, env_var, env_algo, env_graph)
                    env_var = copy_env_var
                    env_algo = copy_env_algo
                    env_graph = copy_env_graph
                    loc = copy_loc
                    v -= 1
                modified_store2 = modified_store
                return modified_store2, copy_env_var, copy_env_algo, copy_env_graph, modified_v, loc
            else:
                v = None
                return modified_store, copy_env_var, copy_env_algo, copy_env_graph, v, loc 

        case Algorithm():
            ph_env_algo = evaluator.categories.algorithm.execute_algorithm(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return store, env_var, ph_env_algo, env_graph, None, loc
        
        case GraphDecl():
            env_graph_new, store_new = evaluator.categories.graph_declaration.execute_graph_decl(node, env_var, env_algo, loc, env_graph, graph_object, store)
            return store_new, env_var, env_algo, env_graph_new, None, loc
        case Expression():
            v,exp_store = evaluator.categories.expression.execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return exp_store, env_var, env_algo, env_graph, None, loc

        case EdgeDecl():
            pass

        case NodeDecl():
            D = evaluator.categories.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return D.store, D.env_var, env_algo, env_graph, None, D.location

        case GraphStatement():
            pass

        case LoopModifier():
            pass

        case DisplayStatement():
            v,exp_store = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
            print(v)
            return exp_store, env_var, env_algo, env_graph, None, loc

        case ReturnStatement():
            v,exp_store = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
            return exp_store, env_var, env_algo, env_graph, v, loc
        case _:
            print("Error: No statement case match!")
            return store, env_var, env_algo, env_graph, None, loc