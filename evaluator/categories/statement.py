import parser.ast_builder
from parser.ast_builder import *
from copy import deepcopy
from evaluator.functions import assign_nested_attribute

import evaluator.categories.algorithm
import evaluator.categories.expression
import evaluator.categories.declaration
import evaluator.categories.graph_declaration
import evaluator.categories.edge_declaration
import evaluator.categories.graph_statement
#import evaluator.categories.edge_loop

class LoopException(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, store, env_var, env_algo, env_graph, v, loc):
        self.store = store
        self.env_var = env_var
        self.env_algo = env_algo
        self.env_graph = env_graph
        self.v = v
        self.loc = loc

def execute_statement(node: ASTNode, loc, graph_object, store, env_var, env_algo, env_graph):
    match node:
        case DeclarationInit():
            if node.is_list:
                # dec-list-ass
                env_var_copy = env_var.copy()

                E = evaluator.categories.expression.execute_expression(node.expression[0], env_graph, env_var_copy, env_algo, loc, graph_object, store)
                D = evaluator.categories.declaration.execute_declaration(node, env_graph, env_var_copy, env_algo, loc, graph_object, E.modified_store)

                D.store.update({loc: E.v})
                return D.store, D.env_var, env_algo, env_graph, E.v, D.location

            else:
                # dec-ass
                env_var_copy = env_var.copy()

                E = evaluator.categories.execute_expression(node.expression[0], env_graph, env_var_copy, env_algo, loc, graph_object, store)
                D = evaluator.categories.declaration.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, E.modified_store)
                env_var_copy = D.env_var
                store_copy = D.store
                loc_prime = D.location

                store_copy.update({loc: E.v})

                return store_copy, env_var_copy, env_algo, env_graph, None, loc_prime

        case Declaration():
            D = evaluator.categories.declaration.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return D.store, D.env_var, env_algo, env_graph, None, D.location

        case Assignment():
            if len(node.identifiers) > 1:
                E = evaluator.categories.expression.execute_expression(
                    node.expression,
                    env_graph,
                    env_var,
                    env_algo,
                    loc,
                    graph_object,
                    store,
                )

                # Outside graph object: G.x or G.x.a.b
                if graph_object.graph is None:
                    graph_identifier = node.identifiers[0]
                    node_identifier = node.identifiers[1]
                    attribute_path = node.identifiers[2:]

                    if graph_identifier not in env_graph:
                        raise RuntimeError(f"Unknown graph object: {graph_identifier}")

                    go = env_graph[graph_identifier]

                    if node_identifier not in go.get_nodes():
                        raise RuntimeError(
                            f"Unknown node/member '{node_identifier}' "
                            f"in graph '{graph_identifier}'"
                        )

                    # G.x := v
                    if not attribute_path:
                        raise RuntimeError(
                            f"A node cannot be assigned, only its attributes"
                        )

                    # G.x.a.b := v
                    else:
                        assign_nested_attribute(
                            go.get_nodes()[node_identifier],
                            attribute_path,
                            E.v,
                        )

                # Inside graph object: x or x.a.b
                else:
                    go = graph_object
                    node_identifier = node.identifiers[0]
                    node_location = env_var.get(node_identifier)
                    node_value = store.get(node_location)
                    attribute_path = node.identifiers[1:]

                    if node_value not in go.get_nodes():
                        raise RuntimeError(
                            f"Unknown node/member '{node_value}' "
                            f"in current graph object"
                        )

                    # x := v
                    if not attribute_path:
                        raise RuntimeError(
                            f"A node cannot be assigned, only its attributes"
                        )

                    # x.a.b := v
                    else:
                        assign_nested_attribute(
                            go.get_nodes()[node_value],
                            attribute_path,
                            E.v,
                        )

                return E.modified_store, env_var, env_algo, env_graph, None, loc

            elif isinstance(node.identifiers[-1], parser.ast_builder.ArrayAccess):
                # list-index-ass
                indexes = []

                E = evaluator.categories.expression.ExpressionReturn(None, store)

                for term in node.identifiers[0].indexes:
                    E = evaluator.categories.expression.execute_expression(term, env_graph,env_var, env_algo, loc, graph_object, E.modified_store)
                    indexes.append(E.v)

                E = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo,loc, graph_object, E.modified_store)
                map = E.modified_store.get(env_var.get(node.identifiers[0].identifier))
                ref = map

                for index in indexes[:-1]:
                    if index < 1:
                        raise IndexError("Indexing starts from 1")

                    if index > len(ref):
                        for i in range(len(ref), index):
                            ref.append([])

                    ref = ref[index -1] # Minus 1, because Python indexes from 0, and GSL do from 1


                if indexes[-1] > len(ref):
                    for i in range(len(ref), indexes[-1]):
                        ref.append(None)
                ref[indexes[-1] -1] = E.v # Minus 1, because Python indexes from 0, and GSL do from 1

                E.modified_store.update({env_var.get(node.identifiers[0].identifier): map})
                return E.modified_store, env_var, env_algo, env_graph, None, loc

            else:
                # ass
                E = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
                E.modified_store.update({env_var.get(node.identifiers[0]): E.v})
                return E.modified_store, env_var, env_algo, env_graph, None, loc

        case IfStatement():
            E = evaluator.categories.expression.execute_expression(node.condition, env_graph, env_var, env_algo, loc, graph_object, store)
            match E.v:
                case True: # IF-T and IFE-T
                    for statement in node.then_statements:
                        E.modified_store, env_var, env_algo, env_graph, E.v, loc = execute_statement(statement, loc, graph_object, E.modified_store, env_var, env_algo, env_graph)
                    return E.modified_store, env_var, env_algo, env_graph, E.v, loc
                case False:
                    match node.else_statements:
                        case []: #IF_F
                            return E.modified_store, env_var, env_algo, env_graph, None, loc
                        case node.else_statements: # IFE-F
                            for i in node.else_statements:
                                E.modified_store, env_var, env_algo, env_graph, E.v, loc = execute_statement(i, loc, graph_object, E.modified_store, env_var, env_algo, env_graph)
                            return E.modified_store, env_var, env_algo, env_graph, E.v, loc                              

        case WhileStatement():
            copy_env_var = deepcopy(env_var)
            copy_env_algo = deepcopy(env_algo)
            copy_env_graph = env_graph.copy()
            copy_loc = deepcopy(loc)
            E = evaluator.categories.expression.execute_expression(node.condition, env_graph, env_var, env_algo, loc, graph_object, store)
            try:
                match E.v:
                    case True:
                        for statement in node.statements:
                            E.modified_store, copy_env_var, copy_env_algo, copy_env_graph, E.v, copy_loc = execute_statement(statement, copy_loc, graph_object, E.modified_store, copy_env_var, copy_env_algo, copy_env_graph)
                        
                        E.modified_store, copy_env_var, copy_env_algo, copy_env_graph, E.v, copy_loc = execute_statement(node, loc, graph_object, E.modified_store, env_var, env_algo, env_graph)
                        return E.modified_store, env_var, env_algo, env_graph, E.v, loc
                    case False:
                        return E.modified_store, env_var, env_algo, env_graph, None, loc
            except LoopException:
                v2 = None
                return E.modified_store, env_var, env_algo, env_graph, v2, loc
            
        case ForEachNormal():
            copy_env_graph = env_graph.copy()
            copy_env_var = deepcopy(env_var)
            copy_env_algo= deepcopy(env_algo)
            copy_loc = deepcopy(loc)


            E = evaluator.categories.expression.execute_expression(node.iterable, copy_env_graph, copy_env_var, copy_env_algo, copy_loc, graph_object, store)
            
            copy_env_var.update({node.loop_identifier:copy_loc})
            copy_loc = copy_loc.next_location()

            try:
                for value in E.v:
                    E.modified_store.update({copy_env_var.get(node.loop_identifier):value})

                    for statement in node.statements:
                        E.modified_store, copy_env_var, copy_env_algo, copy_env_graph, E.v, copy_loc = execute_statement(statement, copy_loc, E.graph_object, E.modified_store, copy_env_var, copy_env_algo, copy_env_graph)
            except LoopException:
                return E.modified_store, env_var, env_algo, env_graph, None, loc

            return E.modified_store, env_var, env_algo, env_graph, E.v, loc

        case ForEachEdge():
            copy_env_graph = env_graph.copy()
            copy_env_var = deepcopy(env_var)
            copy_env_algo= deepcopy(env_algo)
            copy_loc = deepcopy(loc)

            graph_object = copy_env_graph.get(node.graph_identifier)
            copy_graph_object = graph_object.copy()

            # Switch last_node and initial_node if the direction is 'opposite'
            if node.edge.direction == '<--':
                node.edge.last_node, node.edge.initial_node = node.edge.initial_node, node.edge.last_node
           
            # Find all the symmetric edges and keep one of them. Also takes into consideration weights
            if node.edge.direction == '<->':
                copy_graph_object.clear_edges()
                if node.weight_identifier != None:
                    for edge1 in graph_object.get_edges():
                        for edge2 in graph_object.get_edges():
                            if edge1[0] == edge2[1] and edge1[1] == edge2[0]:
                                if copy_graph_object.get_edge_data(edge2[0],edge2[1]) != None:
                                    break
                                copy_graph_object.add_weighted_edge(edge1[0], edge1[1], graph_object.get_edge_data(edge1[0], edge1[1])['weight'])
                else:
                    for edge1 in graph_object.get_edges():
                        for edge2 in graph_object.get_edges():
                            if edge1[0] == edge2[1] and edge1[1] == edge2[0]:
                                if copy_graph_object.get_edge_data(edge2[0],edge2[1]) != None:
                                    break
                                copy_graph_object.add_edge(edge1[0], edge1[1])

            edges = deepcopy(copy_graph_object.get_edges())

            # Add the initial_node and last_node from ForEachEdge() to a copy of env_var,
            # so that they can be accessed in statements that don't use env_graph


            copy_env_var.update({node.edge.initial_node: loc})
            copy_loc = loc.next_location()
            copy_env_var.update({node.edge.last_node:copy_loc})
            copy_loc = copy_loc.next_location()
            if node.weight_identifier != None:
                copy_env_var.update({node.weight_identifier: copy_loc})
                copy_loc = copy_loc.next_location()

            for edge in edges:
                # Update store to match the edges in edge
                store.update({copy_env_var.get(node.edge.initial_node):edge[0]})
                store.update({copy_env_var.get(node.edge.last_node):edge[1]})
                if node.weight_identifier != None:
                    weight_value = copy_graph_object.get_edge_data(edge[0], edge[1])["weight"]
                    store.update({copy_env_var.get(node.weight_identifier):weight_value})
                # If the current statement inside the loop is a GraphStatement,
                # we change the values in a copy of it (copy_statement) to match the edges in edge,
                # because they are the only ones that don't access env_var and store


                try: 
                    for statement in node.statements:
                        copy_statement = deepcopy(statement)
                        match statement:
                            case GraphStatement():
                                match statement.argument: # It matches the argument in the current GraphStatement, which is either an EdgeDecl or Declaration
                                    case EdgeDecl():
                                        for i_node in range(0,len(copy_statement.argument.nodes)):
                                            if node.edge.last_node == copy_statement.argument.nodes[i_node]:
                                                    node2, copy_statement.argument.nodes[i_node] = edge
                                            elif node.edge.initial_node == copy_statement.argument.nodes[i_node]:
                                                    copy_statement.argument.nodes[i_node], node2 = edge
                                            if node.edge.last_node == copy_statement.argument.initial_node:
                                                    node2, copy_statement.argument.initial_node = edge
                                            elif node.edge.initial_node == copy_statement.argument.initial_node:
                                                    copy_statement.argument.initial_node, node2 = edge
                                    case Declaration():
                                        for i_identifiers in range(0,len(copy_statement.argument.identifiers)):
                                            if node.edge.last_node == copy_statement.argument.identifiers[i_identifiers]:
                                                    node2, copy_statement.argument.identifiers[i_identifiers] = edge
                                            elif node.edge.initial_node == copy_statement.argument.identifiers[i_identifiers]:
                                                    copy_statement.argument.identifiers[i_identifiers], node2 = edge
                        store, copy_env_var, copy_env_algo, copy_env_graph, v, loc = execute_statement(copy_statement, loc, graph_object, store, copy_env_var, copy_env_algo, copy_env_graph)
                except LoopException:
                    v2 = None
                    return store, env_var, env_algo, copy_env_graph, v, loc

            return store, env_var, env_algo, copy_env_graph, v, loc
        

        case RepeatStatement():

            E = evaluator.categories.expression.execute_expression(node.repeat_expression, env_graph, env_var, env_algo, loc, graph_object, store)
            
            if E.v > 0: # (REP-T)
                while E.v > 0:
                    copy_env_var = deepcopy(env_var)
                    copy_env_algo = deepcopy(env_algo)
                    copy_env_graph = env_graph.copy()
                    copy_loc = deepcopy(loc)
                    try:
                        for statement in node.repeat_statements:
                            E.modified_store, copy_env_var, copy_env_algo, copy_env_graph, v2, copy_loc  = execute_statement(statement, copy_loc, graph_object, E.modified_store, copy_env_var, copy_env_algo, copy_env_graph)
                    except LoopException:
                        v2 = None
                        return E.modified_store, env_var, env_algo, env_graph, v2, loc
                    E.v -= 1
                modified_store2 = E.modified_store
                return modified_store2, env_var, env_algo, env_graph, v2, loc
            else: # (REP-F)
                return E.modified_store, env_var, env_algo, env_graph, None, loc

        case Algorithm():
            ph_env_algo = evaluator.categories.algorithm.execute_algorithm(node, env_graph, env_var, env_algo)
            return store, env_var, ph_env_algo, env_graph, None, loc
        
        case GraphDecl(): # (GD)
            env_graph_new, store_new = evaluator.categories.graph_declaration.execute_graph_decl(node, env_var, env_algo, loc, env_graph, graph_object, store)
            return store_new, env_var, env_algo, env_graph_new, None, loc

        case Expression():
            E = evaluator.categories.expression.execute_expression(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return E.modified_store, env_var, env_algo, env_graph, None, loc

        case EdgeDecl(): # (D)_e
            v, modified_store = evaluator.categories.edge_declaration.execute_edge_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return modified_store, env_var, env_algo, env_graph, None, loc

        case NodeDecl():
            D = evaluator.categories.declaration.execute_declaration(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return D.store, D.env_var, env_algo, env_graph, None, D.location

        case GraphStatement(): # (S)_g
            evaluator.categories.graph_statement.execute_graph_statement(node, env_graph, env_var, env_algo, loc, graph_object, store)
            return store, env_var, env_algo, env_graph, None, loc

        case LoopModifier():
            raise LoopException()

        case DisplayStatement():
            E = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
            print(E.v)
            return E.modified_store, env_var, env_algo, env_graph, None, loc

        case ReturnStatement():
            E = evaluator.categories.expression.execute_expression(node.expression, env_graph, env_var, env_algo, loc, graph_object, store)
            raise ReturnException(E.modified_store, env_var, env_algo, env_graph, E.v, loc)

        case _:
            exit("Error: No statement case match!")