import re
indent_counter = 0
SPACES_OR_TABS = 0 # 1 for spaces, 2 for tabs
SPACES_AMOUNT = None

final_string = ""
with open("./Preprocessor/test.gsl", "r") as input_file:
    inside_comment = False
    for line in input_file:
        temp_str = line

        # Checks if inside multiline comment. Then check if there is an end. Otherwise skip
        if inside_comment == True:
            if "*/" not in temp_str:
                continue
            else:
                temp_str = re.sub(r".*\*\/.*","", temp_str, flags=re.DOTALL)
                inside_comment = False

        # Remove multi-line comments "/*  */"
        temp_str = re.sub(r"/\*.*?\*/.*", "", temp_str, flags=re.DOTALL)
        if "/*" in temp_str:
            temp_str = re.sub(r"/\*.*","", temp_str, flags=re.DOTALL)
            inside_comment = True

        # Remove single-line comments "//":
        temp_str = re.sub(r"//.*", "", temp_str)

        # Removes a line of white-space
        if temp_str.strip() == "":
            continue

        # Replaces new/missing tabs / 4 spaces with "@INDENT"/"@DEDENT"
        number_indents = 0
        indents = ""


        if m:= re.match(r"(\t|\ )+", temp_str):
            # Creates string from the match
            indents = m.group(0)

            # If it has not yet been defined if the document uses spaces or tabs
            if SPACES_OR_TABS == 0:
                if "\t" in indents and " " in indents:
                    exit("ERROR: Tabs and spaces cannot be combined")

                if "\t" in indents:
                    SPACES_OR_TABS = 2
                else:
                    SPACES_OR_TABS = 1
                    SPACES_AMOUNT = len(indents)
                    print("Number of spaces for this file: " + str(SPACES_AMOUNT))
            
            # If the document uses spaces
            if SPACES_OR_TABS == 1:
                if "\t" in indents:
                    exit("ERROR: Tabs and spaces cannot be combined")
                number_indents = len(indents) / SPACES_AMOUNT
                if number_indents % 1 != 0:
                    exit("ERROR: Inconsistent use of spaces")
            
            # If the document uses tabs
            if SPACES_OR_TABS == 2:
                if " " in indents:
                    exit("ERROR: Tabs and spaces cannot be combined")

        change_indents = int(number_indents) - indent_counter

        # Adds @INDENT or @DEDENT tokens for each indent / dedent
        if change_indents > 0:
            temp_str = re.sub(rf"^(\t|\ {{{SPACES_AMOUNT}}})*", abs(change_indents) * "@INDENT ", temp_str)
        else:
            temp_str = re.sub(rf"^(\t|\ {{{SPACES_AMOUNT}}})*", abs(change_indents) * "@DEDENT ", temp_str)

        # Updates indent counter
        indent_counter += change_indents

        # Replaces 1+ newlines wit one "@NEWLINE"
        temp_str = re.sub(r"(\n)+"," @NEWLINE\n",temp_str)

        # Appends to final string
        final_string += temp_str

# If the document does not end on a newline, add one 
if final_string.endswith("@NEWLINE\n") is False:
    final_string += " @NEWLINE\n"

# If the document does not end unindentet, it adds the missing dedents
if indent_counter != 0:
    final_string += indent_counter * "@DEDENT "

# Adds the EOD sign '$'
final_string += "$"
    
# Prints final string to terminal
print(final_string)

# Output to file
with open("output.gsl", "w") as output_file:
    output_file.write(final_string)