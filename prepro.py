import re

final_str = ""
with open("./Preprosessor/test.gsl", "r") as file:
    indent_counter = 0
    for line in file:

        temp_str = line
        # Remove single-line comments "//":
        temp_str = re.sub(r"//(.)*", "", temp_str)

        # Removes a line of white-space
        if (re.fullmatch(r"\s*", line)):
            continue

        # Replaces new/missing tabs / 4 spaces with "@INDENT"/"@DEDENT"
        number_indents = ""
        indents = ""
        SPACES_INDENT = 4

        m = re.match(rf"(\t|\ {{{SPACES_INDENT}}})+", temp_str)
        if (m):
            indents = m.group(0)
            number_indents = re.sub(rf"(\ {{{SPACES_INDENT}}})", "\t", indents)

        change_indents = len(number_indents) - indent_counter
        if (change_indents >= 0):
            temp_str = re.sub(rf"^(\t|\ {{{SPACES_INDENT}}})+", abs(change_indents) * "@INDENT ", temp_str)
        else:
            temp_str = re.sub(rf"^(\t|\ {{{SPACES_INDENT}}})+", abs(change_indents) * "@DEDENT ", temp_str)

        indent_counter += change_indents

        # Replaces 1+ newlines wit one "@NEWLINE"
        #temp_str = re.sub(r"(\n)+"," @NEWLINE ",temp_str)

        # Appends to final string
        final_str += temp_str


final_str += " @NEWLINE @$"
print(repr(final_str))
