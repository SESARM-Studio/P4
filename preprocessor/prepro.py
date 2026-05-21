from __future__ import annotations
import re
from exceptions.preprocessor_exception import PreprocessorException
from pathlib import Path
from preprocessor.source_map import SourceMap

def preprocessor(file_input, source_map: SourceMap, return_file=False, file_output="output.gsl"):
    current_indent_level = 0
    indent_type = None # Undefined, spaces or tabs
    spaces_amount = None
    line_number = 0
    final_string = ""
    source_map.input_file = str(Path(file_input).resolve())

    with open(file_input, "r") as input_file:
        inside_comment = False
        inside_text = False
        source_offset = 0
        source_end_location = 0
        processed_offset = 0

        for i, line in enumerate (input_file, 1):
            source_map.source_array.append(line)
            source_offset = source_end_location
            source_end_location += len(line)
            processed_offset = len(final_string)
            source_map.newline_array.append(source_offset)
            temp_str = line

            # Checks if inside multiline comment. Then check if there is an end. Otherwise skip
            if inside_comment == True:
                if "*/" not in temp_str:
                    continue
                else:
                    temp_str = re.sub(r".*\*\/","", temp_str)
                    if temp_str.strip() != "":
                        raise PreprocessorException("No code must follow a multi-line comment", [source_offset, source_end_location])
                    inside_comment = False
            
            # If the line contains a double quote (") then make a thorough check of each character to allow // or /* */ inside double quotes ("")
            if "\"" in temp_str:
                for index, char in enumerate(temp_str):
                    if char == "\"" and inside_text == False:
                        inside_text = True
                        continue
                    if char == "/" and inside_text == False:
                        if temp_str[index+1] == "/": # Remove single-line comments "//":
                            temp_str = temp_str[:index] # Splice removes the hidden character \n so need to manually add after
                            temp_str += "\n"
                            break
                        if temp_str[index+1] == "*":
                            if "*/" in temp_str[index:]:
                                # Check if code comes after single-line multi-line comments "/* */"
                                multi_line = re.split(r"/\*.*\*/", temp_str)
                                if re.split(r"/\*.*\*/", temp_str)[1].strip() != "":
                                    raise PreprocessorException("No code must follow a multi-line comment", [source_offset, source_end_location])

                                # Remove single-line multi-line comments "/* */"
                                temp_str = re.sub(r"/\*.*?\*/.*", "", temp_str)
                                break
                            else:
                                # Remove start-of multi-line comments "/*"
                                temp_str = temp_str[:index] # Splice removes the hidden character \n so need to manually add after
                                temp_str += "\n"
                                inside_comment = True
                                break
                    if char == "\"" and inside_text == True:
                        inside_text = False
                        continue
            else:
                # Remove single-line comments "//":
                temp_str = re.sub(r"//.*", "", temp_str)

                # Check if code comes after single-line multi-line comments "/* */"
                multi_line = re.split(r"/\*.*\*/", temp_str)
                if len(multi_line) > 1:
                    if re.split(r"/\*.*\*/", temp_str)[1].strip() != "":
                        raise PreprocessorException("No code must follow a multi-line comment",[source_offset, source_end_location])

                # Remove multi-line comments on 1 line "/* */"
                temp_str = re.sub(r"/\*.*?\*/.*", "", temp_str)

                # Remove start-of multi-line comments "/*"
                if "/*" in temp_str:
                    temp_str = re.sub(r"/\*.*","", temp_str)
                    inside_comment = True

            # Removes a line of white-space
            if temp_str.strip() == "":
                continue

            # Replaces new/missing tabs / x spaces with "@INDENT"/"@DEDENT"
            number_indents = 0
            indents = ""
            line_number += 1

            if re.match(r"(\t|\ )+", temp_str) and line_number == 1:
                raise PreprocessorException("Unexpected indentation",[source_offset, source_end_location])

            if m:= re.match(r"(\t|\ )+", temp_str):
                # Creates string from the match
                indents = m.group(0)

                # If it has not yet been defined if the document uses spaces or tabs
                if indent_type is None:
                    if "\t" in indents and " " in indents:
                        raise PreprocessorException("Tabs and spaces cannot be combined", [source_offset, source_end_location])

                    if "\t" in indents:
                        indent_type = "Tabs"
                    else:
                        indent_type = "Spaces"
                        spaces_amount = len(indents)
                
                # If the document uses spaces
                if indent_type == "Spaces":
                    if "\t" in indents:
                        raise PreprocessorException("Tabs and spaces cannot be combined", [source_offset, source_end_location])
                    if (len(indents) / spaces_amount) % 1 != 0:
                        raise PreprocessorException("Inconsistent use of spaces", [source_offset, source_end_location])
                    number_indents = len(indents) // spaces_amount
                
                # If the document uses tabs
                if indent_type == "Tabs":
                    if " " in indents:
                        raise PreprocessorException("Tabs and spaces cannot be combined", [source_offset, source_end_location])
                    number_indents = len(indents)

            token_amount = number_indents - current_indent_level

            # Adds @INDENT or @DEDENT tokens for each indent / dedent
            if token_amount >= 0:
                temp_str = re.sub(rf"^(\t|\ {{{spaces_amount}}})*", abs(token_amount) * "@INDENT ", temp_str)

            if token_amount < 0:
                temp_str = re.sub(rf"^(\t|\ {{{spaces_amount}}})*", abs(token_amount) * "@DEDENT ", temp_str)

            # Updates indent counter
            current_indent_level += token_amount

            # Add '@NEWLINE' token before newline escape '\n'
            token_str = re.sub(r"(\n)"," @NEWLINE\n",temp_str)
            if token_str != temp_str:
                temp_str = token_str

            # Appends to final string
            final_string += temp_str
            source_map.add_span(processed_offset, source_offset, processed_offset + len(temp_str), source_end_location)

    # If the document does not end on a newline, add one 
    if final_string.endswith("@NEWLINE\n") is False:
        final_string += " @NEWLINE\n"

    # If the document does not end unindentet, it adds the missing dedents
    if current_indent_level > 0:
        final_string += current_indent_level * "@DEDENT "

    # Adds the EOD sign '$'
    final_string += "$"

    # Output to file
    if return_file is False:
        return final_string
    else:
        with open(file_output, "w") as output_file:
            output_file.write(final_string)