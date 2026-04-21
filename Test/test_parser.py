import pytest

import subprocess # Used to run the generated parser
import filecmp # Used to compare parsed output and correct output

from prepro import preprocessor

# Current naming uses parse tree, as this test is 
# not adapted to an AST as output from parser.

PARSED_OUTPUT_FILE_NAME = "Test/parsedInput.xml"

def programParser(inputProgram: str, expectedOutput: str):
    # Run the preprocessor on GSL input
    preprocessor(inputProgram, PARSED_OUTPUT_FILE_NAME)

    # Run the GSL parser as a subprocess and capture the output in the console
    x = subprocess.run(["python3", "./gslParser.py", "-i", PARSED_OUTPUT_FILE_NAME], capture_output=True)


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
    testProgramNames = ["Test/GslPrograms/bellmanFord.gsl", "Test/GslPrograms/simpleGraph.gsl"]
    correctParseTreeName = ["Test/CorrectParseTrees/correctBellmanFord.xml", "Test/CorrectParseTrees/correctSimpleGraph.xml"]
    results = []
    
    for idx, fname in enumerate(testProgramNames):
        print(fname)
        print(correctParseTreeName[idx])
        results.append((fname, programParser(fname, correctParseTreeName[idx])))
        
    print("\n")
    for gslINput, testResult in results:
        print(gslINput + ": " + str(testResult))