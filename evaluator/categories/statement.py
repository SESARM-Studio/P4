from parser.ast_builder import *
from copy import deepcopy

import evaluator.categories.algorithm
import evaluator.categories.expression
import evaluator.categories.declaration

def execute_statement(node: ASTNode, loc, graph_object, store, env_var, env_algo, env_graph):
    match node:
        case Declaration():
            ret = evaluator.categories.declaration.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return ret.store, ret.env_var, env_algo, env_graph, None, ret.location
        case DeclarationInit():
            pass
        case Assignment():
            pass
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
                            return store, env_var, env_algo, env_graph, v, loc
                        case node.else_statements:
                            for i in node.else_statements:
                                store, env_var, env_algo, env_graph, v, loc = execute_statement(i, loc, graph_object, copy_store, env_var, env_algo, env_graph)
                            return store, env_var, env_algo, env_graph, v, loc                              

        case WhileStatement():
            copy_store = deepcopy(store)
            expression, copy_store = execute_expression(node.condition, loc, graph_object, store, env_var, env_algo, env_graph)
            match expression:
                case True:
                    for i in node.statements:
                        store, env_var, env_algo, env_graph, v, loc = execute_statement(i, loc, graph_object, copy_store, env_var, env_algo, env_graph)
                    execute_statement(node, loc, graph_object, copy_store, env_var, env_algo, env_graph)
                case False:
                    return store, env_var, env_algo, env_graph, v, loc
        case ForEachNormal():
            pass
        case ForEachEdge():
            pass
        case RepeatStatement():
            pass
        case Algorithm():
            ph_env_algo = evaluator.categories.algorithm.execute_algorithm(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return store, env_var, ph_env_algo, env_graph, None, loc
        
        case Expression():
            exp_store = evaluator.categories.expression.execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return store, env_var, env_algo, env_graph, None, loc
        
        case GraphDecl():
            pass
        case Expression():
            v,exp_store = evaluator.categories.expression.execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return exp_store, env_var, env_algo, env_graph, None, loc

        case EdgeDecl():
            pass
        case NodeDecl():
            ret = evaluator.categories.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return ret.store, ret.env_var, env_algo, env_graph, None, ret.location
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