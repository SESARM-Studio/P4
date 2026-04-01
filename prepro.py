import re
indent_counter = 0

final_string = ""
with open("./Preprosessor/test.gsl", "r") as input_file:
    inside_comment = False
    for line in input_file:
        temp_str = line

        # Checks if inside multiline comment. Then check if there is an end. Otherwise skip
        if (inside_comment == True):
            if "*/" not in temp_str:
                continue
            else:
                temp_str = re.sub(r".*\*/.*","", temp_str, flags=re.DOTALL)
                inside_comment = False

        # Remove multi-line comments "/*  */"
        temp_str = re.sub(r"/\*.*?\*/.*", "", temp_str, flags=re.DOTALL)
        if "/*" in temp_str:
            temp_str = re.sub(r"/\*.*","", temp_str, flags=re.DOTALL)
            inside_comment = True

        # Remove single-line comments "//":
        temp_str = re.sub(r"//.*", "", temp_str)

        # Removes a line of white-space
        if (re.fullmatch(r"\s*", temp_str)):
            continue

        # Replaces new/missing tabs / 4 spaces with "@INDENT"/"@DEDENT"
        number_indents = ""
        indents = ""
        SPACES_INDENT = 4

        if m := re.match(rf"(\t|\ {{{SPACES_INDENT}}})+", temp_str):
            indents = m.group(0)
            number_indents = re.sub(rf"(\ {{{SPACES_INDENT}}})", "\t", indents)

        change_indents = len(number_indents) - indent_counter
        if (change_indents > 0):
            temp_str = re.sub(rf"^(\t|\ {{{SPACES_INDENT}}})+", abs(change_indents) * "@INDENT ", temp_str)
        else:
            temp_str = re.sub(rf"^(\t|\ {{{SPACES_INDENT}}})+", abs(change_indents) * "@DEDENT ", temp_str)

        indent_counter += change_indents

        # Replaces 1+ newlines wit one "@NEWLINE"
        temp_str = re.sub(r"(\n)+"," @NEWLINE\n",temp_str)

        # Appends to final string
        final_string += temp_str


if indent_counter != 0:
    final_string += indent_counter * " @DEDENT"
final_string += " @NEWLINE $"
    
#print(repr(final_string))
print((final_string))

# Output to file
with open("output.gsl", "w") as output_file:
    output_file.write(final_string)
