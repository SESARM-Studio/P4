from parser.ast_builder import *

from . import *

def execute_statement(node: ASTNode, env_graph, env_var, env_algo, loc, graph_object, store):
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
            pass
        case GraphDecl():
            pass
        case Expression():
<<<<<<< HEAD
            return execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store)
=======
            v,exp_store = execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store)
>>>>>>> 4ed91a63d132ddb31586243cfc0056964b1f6a9a

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