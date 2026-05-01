import sys

from preprocessor.prepro import preprocessor
from abstract_syntax_tree.ast_builder import AbstractSyntaxTreeBuilder, print_ast
from abstract_syntax_tree.gsl_parser import gsl_parser

def read(arg):
  if arg.startswith("{") and arg.endswith("}"):
    return arg[1:len(arg) - 1]
  else:
    content = preprocessor(arg)
    if len(content) > 0 and content[0] == "\ufeff":
      content = content[1:]
    return content

def main(args):
    debug = False
    for arg in args[1:]:
        if arg == "-debug":
           debug = True
           continue
        b = gsl_parser.ParseTreeBuilder()
        inputString = read(arg)
        parser = gsl_parser(inputString, b)
        ast = AbstractSyntaxTreeBuilder(inputString)
        try:
           parser.parse_Program()
           tree = ast.build_tree(b.stack)
           if debug is True:
              print_ast(tree)
        except gsl_parser.ParseException as pe:
            raise Exception ("ParseException while processing " + arg + ":\n" + parser.getErrorMessage(pe)) from pe
        
if __name__ == '__main__':
  sys.exit(main(sys.argv))
