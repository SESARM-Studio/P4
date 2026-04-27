# P4

## How to run the parser
To run the parser you write in the terminal:
python .\gsl_program.py -debug INPUT
INPUT is either a filepath to a .gsl file or literal text enclosed in curly brackets.
The option -debug is whether to print the abstract syntax tree in the terminal.
Testing CI

## Setting environment up
```bash
# 1. Create virtual environment
python3 -m venv env

# 2. Enter environment
source env/bin/activate # linux / mac

./env/Scripts/activate.bat # windows

# 3. install requirements
python3 -m pip install -r requirements
```
