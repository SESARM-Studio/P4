import parser.ast_builder
from parser.ast_builder import *
from copy import deepcopy

import evaluator.categories.algorithm
import evaluator.categories.expression
import evaluator.categories.declaration
import evaluator.categories.graph_declaration
import evaluator.categories.edge_declaration
import evaluator.categories.graph_statement

def execute_statement(node: ASTNode, loc, graph_object, store, env_var, env_algo, env_graph):
    match node:
        case DeclarationInit():
            if node.is_list:
                # dec-ass-list
                print("dec-ass-list")
                #D = evaluator.categories.declaration.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
                #D.store.update({loc: })

            else:
                print("dec-ass")
                # dec-ass
                if len(node.expression) > 1: #  Ligegyldigt hvis type-checkeren tjekker det?
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
            if len(node.identifiers) > 1: # Ligegyldigt hvis type-checkeren gør det?
                raise RuntimeError("Can only assign one identifier at a time")

            if isinstance(node.identifiers[0], parser.ast_builder.ArrayAccess):
                # list-index-ass
                store_copy = store.copy()
                indexes = []

                for term in node.identifiers[0].indexes:
                    v, store_copy = evaluator.categories.expression.execute_expression(term, env_graph,env_var, env_algo, loc, graph_object, store_copy)
                    indexes.append(v-1) # Minus 1, beacuse GSL indexes from 1 instead of 0, as python does

                v, store_copy = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo,loc, graph_object, store_copy)
                map = store_copy.get(env_var.get(node.identifiers[0].identifier))
                ref = map
                #TODO: Add index out of range / catch exception
                for index in indexes[:-1]:
                    ref = ref[index]
                ref[indexes[-1]] = v
                store_copy.update({env_var.get(node.identifiers[0].identifier): map})
                return store_copy, env_var, env_algo, env_graph, None, loc

            else:
                # list-ass
                # ass
                v, exp_store = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                # Formoder at typecheckeren tjekker at identifieren allerede er erklæret
                exp_store.update({env_var.get(node.identifiers[0]): v})
                return exp_store, env_var, env_algo, env_graph, None, loc


            #if node.children[0].token == 'ArrayAccess':
            #    print(node.children[0].children[0].token, "Array")

        case IfStatement():
            copy_store = deepcopy(store)
            expression, copy_store = evaluator.categories.expression.execute_expression(node.condition, env_graph, env_var, env_algo, loc, graph_object, store) 
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
            expression, copy_store = evaluator.categories.expression.execute_expression(node.condition, env_graph, env_var, env_algo, loc, graph_object, store)
            expression, copy_store = evaluator.categories.expression.execute_expression(node.condition, env_graph, env_var, env_algo, loc, graph_object, store)
            match expression:
                case True:
                    for i in node.statements:
                        store, env_var, env_algo, env_graph, v, loc = execute_statement(i, loc, graph_object, copy_store, env_var, env_algo, env_graph)
                    execute_statement(node, loc, graph_object, copy_store, env_var, env_algo, env_graph)
                case False:
                    return store, env_var, env_algo, env_graph, None, loc
        case ForEachNormal():
            v, store = evaluator.categories.expression.execute_expression(node.iterable, env_graph, env_var, env_algo, loc, graph_object, store)
            #Thought that v = env_var.get(node.iterable.arg1.value) after the line above, but it is just v = [].
            for i1 in v:
                for i2 in node.statements:
                    store, env_var, env_algo, env_graph, v, loc = execute_statement(i2, loc, graph_object, store, env_var, env_algo, env_graph)
                store, env_var, env_algo, env_graph, v, loc = execute_statement(i2, loc, graph_object, store, env_var, env_algo, env_graph)
            return store, env_var, env_algo, env_graph, v, loc
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
            v = evaluator.categories.edge_declaration.execute_edge_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return store, env_var, env_algo, env_graph, v, loc

        case NodeDecl():
            D = evaluator.categories.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return D.store, D.env_var, env_algo, env_graph, None, D.location

        case GraphStatement():
            evaluator.categories.graph_statement.execute_graph_statement(node, env_graph, env_var, env_algo, loc, graph_object, store)
            v = None
            return store, env_var, env_algo, env_graph, v, loc

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
            exit("Error: No statement case match!")