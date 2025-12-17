import re


class Splitter:
    def __init__(self, separators, keep_ends=True, maxsplit=0):
        self.separators = separators
        self.keep_ends = keep_ends
        self.maxsplit = maxsplit

        if self.keep_ends:
            self.pattern = re.compile('(' + '|'.join(map(re.escape, self.separators)) + ')')

        else:
            self.pattern = re.compile('|'.join(map(re.escape, self.separators)))

    def split(self, text):
        if not self.keep_ends:
            return self.pattern.split(text, maxsplit=self.maxsplit)

        matches = list(self.pattern.finditer(text))
        parts = []
        last_index = 0
        split_count = 0

        for match in matches:
            if self.maxsplit and split_count >= self.maxsplit:
                break
            # Add the text before the current splitter, including the splitter itself
            start, end = match.span()
            parts.append(text[last_index:end])
            last_index = end
            split_count += 1

        # Add the remainder of the text if any
        if last_index < len(text):
            parts.append(text[last_index:])

        return parts
