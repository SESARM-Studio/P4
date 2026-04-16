import re
indent_counter = 0
spaces_or_tabs = 0 # 1 for spaces, 2 for tabs
spaces_amount = None
line_number = 0

final_string = ""
with open("./Preprocessor/test.gsl", "r") as input_file:
    inside_comment = False
    inside_text = False

    for i, line in enumerate (input_file, 1):
        temp_str = line

        # Checks if inside multiline comment. Then check if there is an end. Otherwise skip
        if inside_comment == True:
            if "*/" not in temp_str:
                continue
            else:
                temp_str = re.sub(r".*\*\/","", temp_str)
                if temp_str.strip() != "":
                    exit(f"ERROR LINE {i}: No code must follow a multi-line comment")
                inside_comment = False
        
        # If the line contains a double quote (") then make a thorough check of each character to allow // or /* */ inside double quotes ("")
        if "\"" in temp_str:
            for c in enumerate(temp_str): # c is a tuple where c[0] is the index and c[1] is the character
                if c[1] == "\"" and inside_text == False:
                    inside_text = True
                    continue
                if c[1] == "/" and inside_text == False:
                    if temp_str[c[0]+1] == "/": # Remove single-line comments "//":
                        temp_str = temp_str[:c[0]] # Splice removes the hidden character \n so need to manually add after
                        temp_str += "\n"
                        break
                    if temp_str[c[0]+1] == "*":
                        if "*/" in temp_str:
                            # Check if code comes after single-line multi-line comments "/* */"
                            multi_line = re.split(r"/\*.*\*/", temp_str)
                            if re.split(r"/\*.*\*/", temp_str)[1].strip() != "":
                                exit(f"ERROR LINE {i}: No code must follow a multi-line comment")

                            # Remove single-line multi-line comments "/* */"
                            temp_str = re.sub(r"/\*.*?\*/.*", "", temp_str)
                            break
                        else:
                            # Remove start-of multi-line comments "/*"
                            temp_str = temp_str[:c[0]] # Splice removes the hidden character \n so need to manually add after
                            temp_str += "\n"
                            inside_comment = True
                            break
                if c[1] == "\"" and inside_text == True:
                    inside_text = False
                    continue
        else:
            # Remove single-line comments "//":
            temp_str = re.sub(r"//.*", "", temp_str)

            # Remove single-line multi-line comments "/* */"
            temp_str = re.sub(r"/\*.*?\*/.*", "", temp_str)

            # Check if code comes after single-line multi-line comments "/* */"
            multi_line = re.split(r"/\*.*\*/", temp_str)
            if len(multi_line) > 1:
                if re.split(r"/\*.*\*/", temp_str)[1].strip() != "":
                    exit(f"ERROR LINE {i}: No code must follow a multi-line comment")

            # Remove start-of multi-line comments "/*"
            if "/*" in temp_str:
                temp_str = re.sub(r"/\*.*","", temp_str)
                inside_comment = True

        # Removes a line of white-space
        if temp_str.strip() == "":
            continue

        # Replaces new/missing tabs / 4 spaces with "@INDENT"/"@DEDENT"
        number_indents = 0
        indents = ""
        line_number += 1

        if re.match(r"(\t|\ )+", temp_str) and line_number == 1:
            exit(f"ERROR LINE {i}: Unexpected indentation")

        if m:= re.match(r"(\t|\ )+", temp_str):
            # Creates string from the match
            indents = m.group(0)

            # If it has not yet been defined if the document uses spaces or tabs
            if spaces_or_tabs == 0:
                if "\t" in indents and " " in indents:
                    exit(f"ERROR LINE {i}: Tabs and spaces cannot be combined")

                if "\t" in indents:
                    spaces_or_tabs = 2
                else:
                    spaces_or_tabs = 1
                    spaces_amount = len(indents)
                    print("Number of spaces for this file: " + str(spaces_amount))
            
            # If the document uses spaces
            if spaces_or_tabs == 1:
                if "\t" in indents:
                    exit(f"ERROR LINE {i}: Tabs and spaces cannot be combined")
                number_indents = len(indents) / spaces_amount
                if number_indents % 1 != 0:
                    exit(f"ERROR LINE {i}: Inconsistent use of spaces")
            
            # If the document uses tabs
            if spaces_or_tabs == 2:
                if " " in indents:
                    exit(f"ERROR LINE {i}: Tabs and spaces cannot be combined")
                number_indents = len(indents)

        change_indents = int(number_indents) - indent_counter

        # Adds @INDENT or @DEDENT tokens for each indent / dedent
        if change_indents > 0:
            temp_str = re.sub(rf"^(\t|\ {{{spaces_amount}}})*", abs(change_indents) * "@INDENT ", temp_str)
        else:
            temp_str = re.sub(rf"^(\t|\ {{{spaces_amount}}})*", abs(change_indents) * "@DEDENT ", temp_str)

        # Updates indent counter
        indent_counter += change_indents

        # Replaces 1+ newlines wit one "@NEWLINE"
        temp_str = re.sub(r"(\n)"," @NEWLINE\n",temp_str)

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