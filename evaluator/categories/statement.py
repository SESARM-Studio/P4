from parser.ast_builder import *

from . import *

def execute_statement(node: ASTNode, loc, graph_object, store, env_var, env_algo, env_graph):
    match node:

        case Declaration():
            pass
        case DeclarationInit():
            pass
        case Assignment():
            pass
        case IfStatement():
            pass
        case WhileStatement():
            pass
        case ForEachNormal():
            pass
        case ForEachEdge():
            pass
        case RepeatStatement():
            pass
        case Algorithm():
            return execute_algorithm(node, env_graph, env_var, env_algo, loc, graph_object, store)
        case GraphDecl():
            pass
        case Expression():
            v,exp_store = execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return exp_store, env_var, env_algo, env_graph, None, loc
        
        case EdgeDecl():
            pass
        case NodeDecl():
            pass
        case GraphStatement():
            pass
        case LoopModifier():
            pass
        case DisplayStatement():
            pass
        case ReturnStatement():
            pass