class ASTNode:
    def __init__(self, token, children=None, value=None):
        self.token = token
        self.value = value
        self.children = children or []
        self.parent = None

        for c in self.children:
            c.parent = self

class IfStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.if_part = []
        self.then_part = []
        self.else_part = []

class WhileStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.condition = []
        self.statements = []

class RepeatStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.repeat_expression = []
        self.repeat_statements = []

class ForEachNormal(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.loop_variable = None
        self.iterable = []
        self.statements = []


class ForEachEdge(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.edge = []
        self.weight_identifier = None
        self.graph_identifier = None
        self.statements = []

class GraphDecl(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.graph_type = None
        self.identifier = None
        self.weight_type = None
        self.nodes = []
        self.edges = []

class DisplayStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.expression = []

class ReturnStatement(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.expression = []

class FunctionCall(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.identifier = None
        self.arguments = None

class NodeDecl(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.type = "node"
        self.identifiers = []
        self.assignment = None

class ExprGraph(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.graph_variable = None
        self.operator = None
        self.argument = []

class ExprNode(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.variable = []
        self.direction = None

class ExprEdge(ASTNode):
    def __init__(self, token):
        super().__init__(token)
        self.type = "edge"
        self.src = None
        self.dst = []
        self.direction = None
        self.weight = []



def print_ast(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "

    # label shown
    label = node.token
    if node.value is not None:
        label += f" ({node.value})"

    print(prefix + connector + label)

    new_prefix = prefix + ("    " if is_last else "│   ")

    if node.children is not None:
        for i, child in enumerate(node.children):
            last = i == len(node.children) - 1
            print_ast(child, new_prefix, last)
    


# Class for the abstract syntax
class AbstractSyntaxTreeBuilder:
    def __init__(self, input_string):
        self.input = input_string

    # After parsing completes successfully, the single remaining node in the stack is the non-terminal representing the start symbol.
    # Therefore, the AST is build on the single element in the stack.
    def build_tree(self, stack):
        if not stack:
            exit("Stack is empty")
        if len(stack) > 1:
            exit("Stack should only contain 1 element")
        program = stack[0]
        return self.recursive_builder(program)

    # Splices the input_string from begin to end index, and returns that string.
    def characters(self, b, e):
        return self.input[b:e]
    
    # Recursive function, which builds the AST from last non-terminal of the stack, in the ASTNode format.
    def recursive_builder(self, symbol):
        symbol_children = []
        accepted_children = []

        # Base case: If symbol does not have attribute children, it is a terminal.
        if hasattr(symbol, "children") is False:
            return ASTNode(symbol.name, [], self.characters(symbol.getBegin(), symbol.getEnd()))

        # Creates a new array of the symbols children, and reduces redundant tokens.
        for child in symbol.children:
            if child.name not in self.SKIP_WORDS:
                symbol_children.append(child)

        match symbol.name:
            case "IfStatement":
                if_statement = IfStatement(symbol.name)
                if_index = then_index = else_index = None

                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "'if'":
                            if_index = index
                        case "'then'":
                            then_index = index
                        case "'else'":
                            else_index = index
                for child in symbol_children[if_index+1:then_index]:
                    if_statement.if_part.append(self.recursive_builder(child))
                
                if else_index is not None:
                    for child in symbol_children[then_index+1:else_index]:
                        if_statement.then_part.append(self.recursive_builder(child))
                    for child in symbol_children[else_index+1:]:
                        if_statement.else_part.append(self.recursive_builder(child))
                else:
                    for child in symbol_children[then_index+1:]:
                        if_statement.then_part.append(self.recursive_builder(child))
                return if_statement
            
            case "WhileStatement":
                while_statement = WhileStatement(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "Expression":
                            while_statement.condition.append(self.recursive_builder(child))
                        case "Statement":
                            while_statement.statements.append(self.recursive_builder(child))
                return while_statement
            
            case "ForEachNormal":
                for_each_normal = ForEachNormal(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            for_each_normal.loop_variable = self.characters(child.begin, child.end)
                        case "Expression":
                            for_each_normal.iterable.append(self.recursive_builder(child))
                        case "Statement":
                            for_each_normal.statements.append(self.recursive_builder(child))

            case "ForEachEdge":
                for_each_edge = ForEachEdge(symbol.name)
                for index, child in enumerate(symbol_children):
                    match child.name:
                        case "ExprEdge":
                            for_each_edge.edge.append(self.recursive_builder(child))
                        case "'with weight'":
                            for_each_edge.weight_identifier = self.characters(symbol_children[index+1].begin, symbol_children[index+1].end)
                        case "'in'":
                            for_each_edge.graph_identifier = self.characters(symbol_children[index+1].begin, symbol_children[index+1].end)
                        case "Statement":
                            for_each_edge.statements.append(self.recursive_builder(child))

            case "RepeatStatement":
                repeat_statement = RepeatStatement(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "Expression":
                            repeat_statement.repeat_expression.append(self.recursive_builder(child))
                        case "Statement":
                            repeat_statement.repeat_statements.append(self.recursive_builder(child))
                return repeat_statement

            case "GraphDecl":
                graph_decl = GraphDecl(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "TYPE_GRAPH":
                            graph_decl.graph_type = self.characters(child.begin, child.end)
                        case "IDENTIFIER":
                            graph_decl.identifier = self.characters(child.begin, child.end)
                        case "TYPE_ARITH":
                            graph_decl.weight_type = self.characters(child.begin, child.end)
                        case "NodeDec":
                            graph_decl.nodes.append(self.recursive_builder(child))
                        case "ExprEdge":
                            graph_decl.edges.append(self.recursive_builder(child))
                return graph_decl
            
            case "DisplayStatement":
                display_statement = DisplayStatement(symbol.name)
                for child in symbol_children:
                    if child.name == "Expression":
                        display_statement.expression = self.recursive_builder(child)
                return display_statement

            case "ReturnStatement":
                return_statement = ReturnStatement(symbol.name)
                for child in symbol_children:
                    if child.name == "Expression":
                        return_statement.expression = self.recursive_builder(child)
                return return_statement
            




                

            case "NodeDec":
                node_decl = NodeDecl(symbol.name)
                for child in symbol_children:
                    if child.name == "IDENTIFIER":
                        node_decl.identifiers.append(self.characters(child.begin, child.end))
                    if child.name == "Expression":
                        node_decl.assignment = self.recursive_builder(child)
                return node_decl
            case "ExprGraph":
                expr_graph = ExprGraph(symbol.name)
                # Work in progress

            case "ExprNode":
                expr_node = ExprNode(symbol.name)
                for child in symbol_children:
                    if child.name == "Expression":
                        expr_node.variable.append(self.recursive_builder(child))
                    else:
                        expr_node.direction = self.characters(child.begin, child.end).strip(")")
                return expr_node
            case "ExprEdge":
                helper_counter = 0
                edge_expr = ExprEdge(symbol.name)
                for child in symbol_children:
                    if child.name == "IdentifierAccess":
                        identifier = self.recursive_access("", child)
                        if helper_counter == 0:
                            edge_expr.src = identifier
                            helper_counter += 1
                        else:
                            edge_expr.dst.append(identifier)
                    if child.name in ["'-->'", "'<--'", "'<->'", "'---'"]:
                        edge_expr.direction = child.name.strip("'")
                    if child.name == "Expression":
                        edge_expr.weight = self.recursive_builder(child)
                return edge_expr
            
                        
            
            case "FunctionCall":
                function_call = FunctionCall(symbol.name)
                for child in symbol_children:
                    match child.name:
                        case "IDENTIFIER":
                            function_call.identifier = self.characters(child.begin, child.end)
                        case "ArgList":
                            function_call.arguments = self.recursive_builder(child)
                return function_call
            case "ArgList":
                arguments = []
                for child in symbol_children:
                    arguments.append(self.recursive_builder(child))
                return arguments
                    
                    

                

                


                    


        if len(symbol_children) == 1:
            return self.recursive_builder(symbol_children[0])

        for child in symbol_children:
            accepted_children.append(self.recursive_builder(child))

        # Return the non-terminal as a ASTNode with the array of ASTNode children.
        return ASTNode(symbol.name, accepted_children)


    SKIP_WORDS = [
        "'('", "')'", "','", "'@NEWLINE'", "'@INDENT'", "'@DEDENT'"
    ]

    def recursive_access(self, string, node):

        string += self.characters(node.begin, node.end)

        if hasattr(node,"children") and node.children is not None:
            for child in node.children:
                self.recursive_access(string, child)
        return string
