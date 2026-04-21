import subprocess # Used to run the generated parser
import filecmp # Used to compare parsed output and correct output

from test.prepro import preprocessor

# Current naming uses parse tree, as this test is 
# not adapted to an AST as output from parser.

program_names = ["test/gsl_programs/bellman_ford.gsl", "test/gsl_programs/simple_graph.gsl"]
correct_parse_tree_name = ["test/correct_parse_trees/correct_bellman_ford.xml", "test/correct_parse_trees/correct_simple_graph.xml"]

def test_bellman_ford_parser():
    parsed_bellman_ford_file = "test/parsed_programs/parsed_bellman_ford.xml"
    input_program = program_names[0]
    expected_output = correct_parse_tree_name[0]

    # Run the preprocessor on GSL input
    preprocessor(input_program, parsed_bellman_ford_file)

    # Run the GSL parser as a subprocess and capture the output in the console
    x = subprocess.run(["python3", "./gsl_parser.py", "-i", parsed_bellman_ford_file], capture_output=True)


    # Debug print
    # print(x.stdout)


    # Write produced AST to a file
    with open(parsed_bellman_ford_file, "w") as output:
      output.write(str(x.stdout))

    # Compare parsed GSL program to expected correct parse tree
    rc = filecmp.cmp(parsed_bellman_ford_file, expected_output, shallow=False)
    assert rc == True

def test_simple_graph_parser():
    parsed_simple_graph_file = "test/parsed_programs/parsed_simple_graph.xml"
    input_program = program_names[1]
    expected_output = correct_parse_tree_name[1]

    # Run the preprocessor on GSL input
    preprocessor(input_program, parsed_simple_graph_file)

    # Run the GSL parser as a subprocess and capture the output in the console
    x = subprocess.run(["python3", "./gsl_parser.py", "-i", parsed_simple_graph_file], capture_output=True)


    # Debug print
    # print(x.stdout)


    # Write produced AST to a file
    with open(parsed_simple_graph_file, "w") as output:
      output.write(str(x.stdout))

    # Compare parsed GSL program to expected correct parse tree
    rc = filecmp.cmp(parsed_simple_graph_file, expected_output, shallow=False)
    assert rc == True