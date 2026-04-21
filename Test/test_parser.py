import pytest

import subprocess # Used to run the generated parser
import filecmp # Used to compare parsed output and correct output

from test.prepro import preprocessor

# Current naming uses parse tree, as this test is 
# not adapted to an AST as output from parser.

PARSED_OUTPUT_FILE_NAME = "test/parsed_input.xml"

def program_parser(inputProgram: str, expectedOutput: str):
    # Run the preprocessor on GSL input
    preprocessor(inputProgram, PARSED_OUTPUT_FILE_NAME)

    # Run the GSL parser as a subprocess and capture the output in the console
    x = subprocess.run(["python3", "./gsl_parser.py", "-i", PARSED_OUTPUT_FILE_NAME], capture_output=True)


    # Debug print
    # print(x.stdout)


    # Write produced AST to a file
    with open(PARSED_OUTPUT_FILE_NAME, "w") as output:
      output.write(str(x.stdout))

    # Compare parsed GSL program to expected correct parse tree
    rc = filecmp.cmp(PARSED_OUTPUT_FILE_NAME, expectedOutput, shallow=False)
    assert rc == True

    return rc

# Expected output could be CorrectParseTrees/CorrectBellmanFOrd.xml
def test_parser():
    test_program_names = ["test/gsl_programs/bellman_ford.gsl", "test/gsl_programs/simple_graph.gsl"]
    correct_parse_tree_name = ["test/correct_parse_trees/correct_bellman_ford.xml", "test/correct_parse_trees/correct_simple_graph.xml"]
    results = []
    
    for idx, fname in enumerate(test_program_names):
        print(fname)
        print(correct_parse_tree_name[idx])
        results.append((fname, program_parser(fname, correct_parse_tree_name[idx])))
        
    print("\n")
    for gsl_input, test_result in results:
        print(gsl_input + ": " + str(test_result))