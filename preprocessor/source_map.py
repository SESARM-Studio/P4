class SourceMap:
    map = dict()
    newline_array = []
    input_file = ''
    source_array = []

    def add_span(self, processed_offset, original_offset, processed_end, original_end):
        segment = SpanSegment(processed_offset, original_offset, processed_end, original_end)
        self.map.update({processed_offset: segment})


    def get_line(self, original_offset):
        i = 0
        while i < len(self.newline_array):
            if original_offset < self.newline_array[i]:
                break
            i += 1
        return i

    def get_source_spans_from_processed(self, processed_offset, processed_end):
        all_spans = list(self.map.keys())

        key_offset = 0
        start_index = None

        for i, offset in enumerate(all_spans):
            if processed_offset >= offset:
                key_offset = offset
                start_index = i
            else:
                break

        span_segment = self.map.get(key_offset)
        if span_segment.processed_end >= processed_end:
            return [span_segment]

        result = [span_segment]
        start_index += 1

        while start_index < len(all_spans):
            next_seg = self.map.get(all_spans[start_index])
            result.append(next_seg)

            if next_seg.processed_end >= processed_end:
                break

            start_index += 1

        return result

    def get_source_info(self, processed_start, processed_end):
        span_segments = self.get_source_spans_from_processed(processed_start, processed_end)
        span_lines = []
        string_lines = []
        for span in span_segments:
            span_lines.append(self.get_line(span.original_start))

        for line in span_lines:
            string_lines.append(self.source_array[line-1])

        return {
            "start_line": span_lines[0],
            "end_line": span_lines[-1],
            "lines_text": string_lines
        }

    def print_error(self, message, span_start, span_end, processed=True, error_type = None):
        if processed is True:
            error_info = self.get_source_info(span_start, span_end)
        else:
            text_lines = []
            start_line = self.get_line(span_start); end_line = self.get_line(span_end)
            for line in range(start_line -1, end_line): # Minus 1, cause lines start from 1, Python does from 0
                text_lines.append(self.source_array[line])
            error_info = {
                "start_line": start_line,
                "end_line": end_line,
                "lines_text": text_lines
            }

        if error_info["start_line"] == error_info["end_line"]:
            print(f'File "{self.input_file}", line {error_info["start_line"]}')
        else:
            print(f'File "{self.input_file}", lines {error_info["start_line"]}-{error_info["end_line"]}')

        for line in error_info["lines_text"]:
            print(f"> {line.rstrip()}")

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