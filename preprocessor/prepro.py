from __future__ import annotations
import re
import copy

def preprocessor(file_input, source_map: SourceMap, file_output="output.gsl"):
    indent_counter = 0
    spaces_or_tabs = 0 # 1 for spaces, 2 for tabs
    spaces_amount = None
    line_number = 0
    final_string = ""

    with open(file_input, "r") as input_file:
        inside_comment = False
        inside_text = False
        source_offset = 0
        source_end_location = 0
        processed_offset = 0

        for i, line in enumerate (input_file, 1):
            source_offset = source_end_location
            source_end_location += len(line)
            processed_offset = len(final_string)
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
                for index, char in enumerate(temp_str):
                    if char == "\"" and inside_text == False:
                        inside_text = True
                        continue
                    if char == "/" and inside_text == False:
                        if temp_str[index+1] == "/": # Remove single-line comments "//":
                            temp_str = temp_str[:index] # Splice removes the hidden character \n so need to manually add after
                            temp_str += "\n"
                            source_map.add_span(processed_offset, source_offset, processed_offset + len(temp_str), source_offset + len(temp_str))
                            break
                        if temp_str[index+1] == "*":
                            if "*/" in temp_str[index:]:
                                # Check if code comes after single-line multi-line comments "/* */"
                                multi_line = re.split(r"/\*.*\*/", temp_str)
                                if re.split(r"/\*.*\*/", temp_str)[1].strip() != "":
                                    exit(f"ERROR LINE {i}: No code must follow a multi-line comment")

                                # Remove single-line multi-line comments "/* */"
                                temp_str = re.sub(r"/\*.*?\*/.*", "", temp_str)
                                source_map.safe_remove(processed_offset)
                                break
                            else:
                                # Remove start-of multi-line comments "/*"
                                temp_str = temp_str[:index] # Splice removes the hidden character \n so need to manually add after
                                temp_str += "\n"
                                inside_comment = True
                                source_map.add_span(processed_offset, source_offset, processed_offset + len(temp_str), source_offset + len(temp_str))
                                break
                    if char == "\"" and inside_text == True:
                        inside_text = False
                        continue
            else:
                # Remove single-line comments "//":
                temp_str = re.sub(r"//.*", "", temp_str)
                source_map.add_span(processed_offset, source_offset, processed_offset + len(temp_str), source_offset + len(temp_str))


                # Check if code comes after single-line multi-line comments "/* */"
                multi_line = re.split(r"/\*.*\*/", temp_str)
                if len(multi_line) > 1:
                    if re.split(r"/\*.*\*/", temp_str)[1].strip() != "":
                        exit(f"ERROR LINE {i}: No code must follow a multi-line comment")

                # Remove multi-line comments on 1 line "/* */"
                temp_str = re.sub(r"/\*.*?\*/.*", "", temp_str)
                source_map.add_span(processed_offset, source_offset, processed_offset + len(temp_str), source_offset + len(temp_str))

                # Remove start-of multi-line comments "/*"
                if "/*" in temp_str:
                    temp_str = re.sub(r"/\*.*","", temp_str)
                    inside_comment = True
                    source_map.add_span(processed_offset, source_offset, processed_offset + len(temp_str), source_offset + len(temp_str))


            # Removes a line of white-space
            if temp_str.strip() == "":
                continue

            # Replaces new/missing tabs / x spaces with "@INDENT"/"@DEDENT"
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
                source_map.add_span(processed_offset, source_offset, processed_offset + change_indents * 8, source_offset + len(indents))
                source_map.add_span(processed_offset + change_indents * 8, source_offset + len(indents), processed_offset + len(temp_str), source_offset + len(temp_str))


            if change_indents < 0:
                temp_str = re.sub(rf"^(\t|\ {{{spaces_amount}}})*", abs(change_indents) * "@DEDENT ", temp_str)
                source_map.add_span(processed_offset, source_offset, processed_offset + change_indents * 8, source_offset + len(indents))
                source_map.add_span(processed_offset + change_indents * 8, source_offset + len(indents), processed_offset + len(temp_str), source_offset + len(temp_str))

            # Updates indent counter
            indent_counter += change_indents

            # Add '@NEWLINE' token before newline escape '\n'
            source_map.remove_newline(processed_offset, source_offset, processed_offset + len(temp_str), source_end_location, temp_str)
            temp_str = re.sub(r"(\n)"," @NEWLINE\n",temp_str)
            source_map.add_span(processed_offset + len(temp_str) - 10, source_end_location -1, processed_offset+len(temp_str), source_end_location)


            # Appends to final string
            final_string += temp_str

    # If the document does not end on a newline, add one 
    if final_string.endswith("@NEWLINE\n") is False:
        final_string += " @NEWLINE\n"

    # If the document does not end unindentet, it adds the missing dedents
    if indent_counter != 0:
        final_string += indent_counter * "@DEDENT "
        source_map.add_span(processed_offset, source_end_location, processed_offset + change_indents * 8, source_end_location )


    # Adds the EOD sign '$'
    final_string += "$"

    # Output to file
    with open(file_output, "w") as output_file:
        output_file.write(final_string)



class SourceMap:
    map = dict()

    def add_span(self, processed_offset, original_offset, processed_end, original_end):
        segment = SourceSegment(processed_offset, original_offset, processed_end, original_end)
        self.map.update({processed_offset: segment})

    def get_map(self):
        return copy.deepcopy(map)
    
    def get_original_offset(self, processed_offset):
        return None
    
    def safe_remove(self, processed_offset):
        self.map.pop(processed_offset, None)

    def remove_newline(self, processed_offset, original_offset, processed_end, original_end, string):
        remove_char = 0
        if string[-1] == '\n': remove_char = 1

        old_seg: SourceSegment = self.map.get(processed_offset, None)
        if old_seg is None:
            self.add_span(processed_offset, original_offset, processed_end - remove_char, original_end - remove_char)
        else:
            new_seg = SourceSegment(old_seg.processed_start, old_seg.original_start, old_seg.processed_end - remove_char, old_seg.original_end - remove_char)
            self.map.update({processed_offset: new_seg})

class SourceSegment:
    def __init__(self, ps, os, pe, oe):
        self.processed_start = ps
        self.original_start = os
        self.processed_end = pe
        self.original_end = oe