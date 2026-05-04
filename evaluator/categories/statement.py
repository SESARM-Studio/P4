from abstract_syntax_tree.ast_builder import *

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
            execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store)

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