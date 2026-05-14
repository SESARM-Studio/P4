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
                # dec-list-ass
                env_var_copy = env_var.copy()
                store_copy = store.copy()

                v, exp_store = evaluator.categories.expression.execute_expression(node.expression[0], env_graph, env_var_copy, env_algo, loc, graph_object, store_copy)
                D = evaluator.categories.declaration.execute_declaration(node, env_graph, env_var_copy, env_algo, loc, graph_object, exp_store)

                D.store.update({loc: v})
                return D.store, D.env_var, env_algo, env_graph, v, D.location

            else:
                # dec-ass
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

                for num in indexes:
                    if num < 0:
                        raise IndexError("Indexing starts from 1")

                try:
                    for index in indexes[:-1]:
                        ref = ref[index]
                    ref[indexes[-1]] = v
                except(IndexError, TypeError):
                    raise RuntimeError(
                        f"Invalid indexing {indexes} out of range"
                    )

                store_copy.update({env_var.get(node.identifiers[0].identifier): map})
                return store_copy, env_var, env_algo, env_graph, None, loc

            else:
                # ass
                v, exp_store = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                exp_store.update({env_var.get(node.identifiers[0]): v})
                return exp_store, env_var, env_algo, env_graph, None, loc

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
            copy_env_var = deepcopy(env_var)
            copy_env_algo = deepcopy(env_algo)
            copy_env_graph = env_graph.copy()
            copy_loc = deepcopy(loc)
            v1, modified_store = evaluator.categories.expression.execute_expression(node.condition, env_graph, env_var, env_algo, loc, graph_object, store)
            match v1:
                case True:
                    for i in node.statements:

                        modified_store, env_var, env_algo, env_graph, v2, loc = execute_statement(i, loc, graph_object, modified_store, env_var, env_algo, env_graph)
                        if v2 == "stop":
                            v2 = None
                            return modified_store, copy_env_var, copy_env_algo, copy_env_graph, v2, copy_loc
                    env_var = copy_env_var
                    env_algo = copy_env_algo
                    env_graph = copy_env_graph
                    loc = copy_loc
                    execute_statement(node, loc, graph_object, modified_store, env_var, env_algo, env_graph)
                case False:
                    v2 = None
                    return modified_store, copy_env_var, copy_env_algo, copy_env_graph, v2, copy_loc

            return modified_store, copy_env_var, copy_env_algo, copy_env_graph, v2, copy_loc

        case ForEachNormal():
            cpy_env_graph = env_graph.copy
            cpy_env_var = deepcopy(env_var)
            cpy_env_algo= deepcopy(env_algo)
            cpy_loc = deepcopy(loc)

            v1, store = evaluator.categories.expression.execute_expression(node.iterable, cpy_env_graph, cpy_env_var, cpy_env_algo, loc, graph_object, store)
            for i1 in v1:
                cpy_env_var.update({node.loop_identifier:loc})
                loc = loc.next_location()
                store.update({cpy_env_var.get(node.loop_identifier):i1})

                for i2 in node.statements:
                    store, cpy_env_var, cpy_env_algo, cpy_env_graph, v2, loc = execute_statement(i2, loc, graph_object, store, cpy_env_var, cpy_env_algo, cpy_env_graph)
                loc = cpy_loc
            return store, env_var, env_algo, env_graph, v2, cpy_loc

        case ForEachEdge():
            #cpy_env_graph = deepcopy(env_graph)
            cpy_env_graph = env_graph.copy()
            cpy_env_var = deepcopy(env_var)
            cpy_env_algo= deepcopy(env_algo)
            cpy_loc = deepcopy(loc)
            flag11 = []
            flag12 = []
            flag21 = []
            flag22 = []
            first_i = True
            
            graph_object = cpy_env_graph.get(node.graph_identifier)
            edges = deepcopy(graph_object.get_edges())

            for i1 in edges:
                for i_statement in range(0, len(node.statements)):
                    for i_node in range(0,len(node.statements[i_statement].argument.nodes)):
                        if first_i == False:    
                            for i_flag in range(0,len(flag12)):
                                if flag12[i_flag] == (i_statement, i_node):
                                    node.statements[i_statement].argument.nodes[i_node], node2 = i1

                            for i_flag in range(0,len(flag22)):
                                if flag22[i_flag] == (i_statement, i_node):
                                    node2, node.statements[i_statement].argument.nodes[i_node] = i1
                            
                            for i_flag in range(0,len(flag11)):
                                if flag11[i_flag] == (i_statement, i_node):
                                    node.statements[i_statement].argument.initial_node, node2 = i1
                            
                            for i_flag in range(0,len(flag21)):
                                if flag21[i_flag] == (i_statement, i_node):
                                    node2, node.statements[i_statement].argument.initial_node = i1
                        
                        if first_i == True:
                            if node.edge.last_node == node.statements[i_statement].argument.nodes[i_node]:
                                    node2, node.statements[i_statement].argument.nodes[i_node] = i1
                                    flag22.append((i_statement, i_node))
                            if node.edge.initial_node == node.statements[i_statement].argument.nodes[i_node]:
                                    node.statements[i_statement].argument.nodes[i_node], node2 = i1
                                    flag12.append((i_statement, i_node))
                            if node.edge.last_node == node.statements[i_statement].argument.initial_node:
                                    node2, node.statements[i_statement].argument.initial_node = i1
                                    flag21.append((i_statement, i_node))
                            if node.edge.initial_node == node.statements[i_statement].argument.initial_node:
                                    node.statements[i_statement].argument.initial_node, node2 = i1
                                    flag11.append((i_statement, i_node))
                
                first_i = False

                for i2 in node.statements:
                    store, cpy_env_var, cpy_env_algo, cpy_env_graph, v2, loc = execute_statement(i2, loc, graph_object, store, cpy_env_var, cpy_env_algo, cpy_env_graph)
                loc = cpy_loc
                print(graph_object.get_edges())    
            return store, env_var, env_algo, env_graph, v2, cpy_loc
        

        case RepeatStatement():
            copy_env_var = deepcopy(env_var)
            copy_env_algo = deepcopy(env_algo)
            copy_env_graph = env_graph.copy()
            copy_loc = deepcopy(loc)
            v1, modified_store = evaluator.categories.expression.execute_expression(node.repeat_expression, env_graph, env_var, env_algo, loc, graph_object, store)
            
            if v1 > 0:
                while v1 > 0:
                    for statement in node.repeat_statements:
                        modified_store, env_var, env_algo, env_graph, v2, loc  = execute_statement(statement, loc, graph_object, modified_store, env_var, env_algo, env_graph)
                        if v2 == "stop":
                            v1 = 0
                            break
                    env_var = copy_env_var
                    env_algo = copy_env_algo
                    env_graph = copy_env_graph
                    loc = copy_loc
                    v1 -= 1
                modified_store2 = modified_store
                return modified_store2, copy_env_var, copy_env_algo, copy_env_graph, v2, copy_loc
            else:
                v2 = None
                return modified_store, copy_env_var, copy_env_algo, copy_env_graph, v2, copy_loc

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
            v = node.modifier
            return store, env_var, env_algo, env_graph, v, loc

        case DisplayStatement():
            v,exp_store = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
            print(v)
            return exp_store, env_var, env_algo, env_graph, None, loc

        case ReturnStatement():
            v,exp_store = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
            return exp_store, env_var, env_algo, env_graph, v, loc

        case _:
            exit("Error: No statement case match!")