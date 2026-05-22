class SourceMap:
    map = dict() # Maps offsets in the processed code to SpanSegment objects
    newline_array = [] # Array passed from the preprocessor, with the original offset at each newline
    input_file = '' # Input file used by the preprocessor
    source_array = [] # Array containing each line of original code, to print for error messages

    def add_span(self, processed_offset_start, original_offset_start, processed_offset_end, original_offset_end):
        segment = SpanSegment(processed_offset_start, original_offset_start, processed_offset_end, original_offset_end)
        self.map.update({processed_offset_start: segment})

    def get_line(self, original_offset):
        for i in range(len(self.newline_array)):
            if original_offset < self.newline_array[i]:
                return i

        return len(self.newline_array)

    def get_spans_from_processed_segment(self, processed_offset_start, processed_offset_end):
        """
        Returns the SpanSegments based on a processed start and end offset
        """

        offsets = list(self.map.keys()) # List of all processed offsets

        # Finds the span containing the processed start, and sets start_index to that offset
        start_index = 0
        for i, offset in enumerate(offsets):
            if processed_offset_start >= offset:
                start_index = i
            else:
                break

        spans = []

        # Collects spans from start_index, until processed_end is covered
        for offset in offsets[start_index:]:
            span = self.map.get(offset)
            spans.append(span)

            if span.processed_end >= processed_offset_end:
                break

        return spans

    def get_error_info_from_processed_segment(self, processed_start, processed_end):
        """
        Returns information about the original coded needed for error messages, based on a processed segment
        """
        span_segments = self.get_spans_from_processed_segment(processed_start, processed_end)

        span_lines = [] # Array containing line numbers in original source code for the processed span
        source_code_lines = [] # Array containing source code representing the span segments

        for span in span_segments:
            span_lines.append(self.get_line(span.original_start))

        for line in span_lines:
            source_code_lines.append(self.source_array[line-1]) # -1 Because Python indexes from 0, and lines begin at 1

        return {
            "start_line": span_lines[0],
            "end_line": span_lines[-1],
            "lines_text": source_code_lines
        }

    def print_error(self, message, span_start, span_end, processed=True, error_type = None):
        """
        Function for printing error messages based on either processed or original code segments
        """
        if processed is True:
            error_info = self.get_error_info_from_processed_segment(span_start, span_end)
        else: # If processed = False, we must format information and gather all text lines to be printed
            text_lines = []
            start_line = self.get_line(span_start); end_line = self.get_line(span_end)
            for line in range(start_line -1, end_line): # Minus 1, cause lines start from 1, Python does from 0
                text_lines.append(self.source_array[line])

            error_info = {
                "start_line": start_line,
                "end_line": end_line,
                "lines_text": text_lines
            }

        # Prints file location information, in VS Code clickable format
        if error_info["start_line"] == error_info["end_line"]:
            print(f'File "{self.input_file}", line {error_info["start_line"]}')
        else:
            print(f'File "{self.input_file}", lines {error_info["start_line"]}-{error_info["end_line"]}')

        # Prints each line of code
        for line in error_info["lines_text"]:
            print(f"> {line.rstrip()}")

        # Prints error type and message
        if error_type:
            print(f"Error {error_type}: {message}")
        else:
            print(f"Error: {message}")

class SpanSegment:
    def __init__(self, ps, os, pe, oe):
        self.processed_start = ps
        self.original_start = os
        self.processed_end = pe
        self.original_end = oe