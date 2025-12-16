import re

from .utils import Misc
from .constant import STRING
from .constnum import NUMBER
from .constsymbol import SYMBOL
from .constpattern import PATTERN

from .conststruct import SLICE


class Wildcard:
    def __init__(self, data, is_leading=False, is_trailing=False,
                 ignore_case=True, relax=False, used_whitespace=False,
                 from_start_to_end=True):
        self.data = str(data)
        self.is_leading = is_leading
        self.is_trailing = is_trailing
        self.ignore_case = ignore_case
        self.is_multiline = bool(re.search(PATTERN.CRNL, self.data))
        self.relax = relax
        self.used_whitespace = used_whitespace
        self.from_start_to_end = from_start_to_end

        self.ws_placeholder = '__placeholder_whitespace_pat__'
        self.multi_ws_placeholder = '__placeholder_whitespaces_pat__'

        self.ws_repl = PATTERN.WHITESPACE if used_whitespace else PATTERN.SPACE
        self.multi_ws_repl = PATTERN.WHITESPACES if used_whitespace else PATTERN.SPACES
        self.ws_pattern = self.ws_repl
        self.multi_ws_pattern = self.multi_ws_repl

        if self.relax:
            self.ws_repl = self.multi_ws_repl

        self._pattern = STRING.EMPTY
        self.failure_fmt = 'unsupported parsing integers (%s, %s)'
        self.process()

    @property
    def pattern(self):
        return self._pattern

    def process(self):
        p = r'(?i)(?P<start>^ *--regex *)|(?P<end> +--regex *$)|(?P<middle> *--regex +)'
        match = re.search(p, self.data)
        if match:
            start = match.groupdict().get(STRING.START, STRING.EMPTY)
            end = match.groupdict().get(STRING.END, STRING.EMPTY)
            middle = match.groupdict().get(STRING.MIDDLE, STRING.EMPTY)
            if start:
                replaced = PATTERN.ZOSPACES if len(start) > NUMBER.EIGHT else STRING.EMPTY
            elif end:
                replaced = PATTERN.ZOSPACES if len(end) > NUMBER.EIGHT else STRING.EMPTY
            else:
                replaced = PATTERN.ZOSPACES if len(middle) > NUMBER.EIGHT else STRING.EMPTY
            self._pattern = re.sub(p, replaced, self.data)
        else:
            method = self.parse_multiline if self.is_multiline else self.parse_line
            pattern = method(self.data)     # noqa

            if self.from_start_to_end and pattern[SLICE.GET_FIRST] != SYMBOL.CARET:
                pattern = '^%s' % pattern

            if self.from_start_to_end and pattern[SLICE.GET_LAST] != SYMBOL.DOLLAR_SIGN:
                pattern = '%s$' % pattern

            if self.ignore_case:
                pattern = '(?i)%s' % pattern
            self._pattern = pattern

    def escape_data(self, data):        # noqa
        if re.match(PATTERN.SPACESATEOS, data):
            return data if len(data) <= NUMBER.ONE else PATTERN.SPACES

        start = NUMBER.ZERO
        item = None
        lst = []
        for item in re.finditer(r'(\\?)([.*+?\[{}\]^$)(])', data):
            pre_matched = data[start:item.start()]
            lst.append(pre_matched)
            matched_data = item.group()
            first, last = item.groups()
            if first == SYMBOL.BACK_SLASH:
                lst.append(matched_data)
            else:
                if last == SYMBOL.QUESTION_MARK:
                    lst.append(PATTERN.ZOANYTHING)
                elif last == SYMBOL.ASTERISK:
                    lst.append(PATTERN.SOMETHING)
                elif last == SYMBOL.PLUS:
                    lst.append(PATTERN.EVERYTHING)
                else:
                    escaped_txt = re.escape(matched_data)
                    lst.append(escaped_txt)
            start = item.end()

        if lst:
            post_matched = data[item.end():]
            lst.append(post_matched)
        else:
            lst.append(data)

        pattern = str.join(STRING.EMPTY, lst)
        return pattern

    def get_pattern_for_two_unsigned_int(self, v1, v2):     # noqa
        small, large = min(v1, v2), max(v1, v2)
        first_small = int(Misc.get_first_char(small))
        last_small = int(Misc.get_last_char(small))
        first_large = int(Misc.get_first_char(large))
        last_large = int(Misc.get_last_char(large))
        small_width, large_width = len(str(small)), len(str(large))

        repl_pat = r'(\[(\d)-\2\])'
        repl_val = r'\2'

        if v1 == v2:
            return str(v1)
        elif small_width == NUMBER.ONE and large_width == NUMBER.ONE:
            pattern = '[%s-%s]' % (small, large)
            return pattern
        elif small_width == NUMBER.ONE and large_width == NUMBER.TWO:
            if first_large == NUMBER.ONE:
                args = (small, last_large)
                pattern = '[%s-9]|(1[0-%s])' % args
                pattern = re.sub(repl_pat, repl_val, pattern)
                return pattern
            elif first_large == NUMBER.TWO:
                if last_large != NUMBER.NINE:
                    args = (small, first_large, last_large)
                    pattern = '[%s-9]|(1[0-9])|(%s[0-%s])' % args
                    pattern = re.sub(repl_pat, repl_val, pattern)
                    return pattern
                else:
                    pattern = '[%s-9]|([1-2][0-9])' % small
                    pattern = re.sub(repl_pat, repl_val, pattern)
                    return pattern
            else:
                if last_large != NUMBER.NINE:
                    args = (small, first_large - NUMBER.ONE, first_large, last_large)
                    pattern = '[%s-9]|([1-%s][0-9])|(%s[0-%s])' % args
                    pattern = re.sub(repl_pat, repl_val, pattern)
                    return pattern
                else:
                    args = (small, first_large)
                    pattern = '[%s-9]|([1-%s][0-9])' % args
                    pattern = re.sub(repl_pat, repl_val, pattern)
                    return pattern

        elif small_width == NUMBER.TWO and large_width == NUMBER.TWO:
            if first_small == first_large:
                args = (first_small, last_small, last_large)
                pattern = '%s[%s-%s]' % args
                pattern = re.sub(repl_pat, repl_val, pattern)
                return pattern
            elif first_small + NUMBER.ONE == first_large:
                args = (first_small, last_small,
                        first_large, last_large)
                pattern = '(%s[%s-9])|(%s[0-%s])' % args
                pattern = re.sub(repl_pat, repl_val, pattern)
                return pattern
            else:
                if last_large != NUMBER.NINE:
                    args = (first_small,
                            last_small, first_small + NUMBER.ONE,
                            first_large - NUMBER.ONE, first_large, last_large)
                    pattern = '(%s[%s-9])|([%s-%s][0-9])|(%s[0-%s])' % args
                    pattern = re.sub(repl_pat, repl_val, pattern)
                    return pattern
                else:
                    args = (first_small, last_small, first_small + 1, first_large)
                    pattern = '(%s[%s-9])|([%s-%s][0-9])' % args
                    pattern = re.sub(repl_pat, repl_val, pattern)
                    return pattern

        elif small < NUMBER.HUNDRED and large == NUMBER.HUNDRED:
            pattern = self.get_pattern_for_two_unsigned_int(small, 99)
            pattern = ('(%s)|(100)' if pattern.isdigit() else '%s|(100)') % pattern
            pattern = re.sub(repl_pat, repl_val, pattern)
            return pattern

        return self.failure_fmt

    def get_pattern_for_two_numbers(self, v1, v2):
        lst = [int(v1), int(v2)]
        small, large = min(lst), max(lst)

        if small == large:
            pattern = str(small)
            return pattern
        if small >= NUMBER.ZERO and large >= NUMBER.ZERO:
            pattern = self.get_pattern_for_two_unsigned_int(small, large)
            if pattern.startswith(STRING.UNSUPPORTED_PARSING):
                failure = self.failure_fmt % (small, large)
                return failure
            pattern = '(%s)' % pattern if SYMBOL.LEFT_PARENTHESIS in pattern else pattern
            return pattern
        elif small <= NUMBER.ZERO and large <= NUMBER.ZERO:
            pattern = self.get_pattern_for_two_numbers(abs(small), abs(large))
            if pattern.startswith(STRING.UNSUPPORTED_PARSING):
                failure = self.failure_fmt % (small, large)
                return failure
            pattern = '(-%s)' % pattern if pattern else pattern
            return pattern
        else:
            pattern1 = self.get_pattern_for_two_numbers(NUMBER.ZERO, small)
            pattern2 = self.get_pattern_for_two_numbers(NUMBER.ZERO, large)
            if pattern1.startswith(STRING.UNSUPPORTED_PARSING):
                failure = self.failure_fmt % (small, large)
                return failure
            if pattern2.startswith(STRING.UNSUPPORTED_PARSING):
                failure = self.failure_fmt % (small, large)
                return failure

            pattern1 = '(%s)' % pattern1 if pattern1[SLICE.GET_FIRST] == '-' else pattern1
            pattern = '(%s|%s)' % (pattern1, pattern2)
            return pattern

    def parse_shell_expansion(self, data):
        match1 = re.match(r'(?i)\{(?P<first>[a-z])[.]{2}(?P<last>[a-z])}', data)
        match2 = re.match(r'(?i)\{(?P<first>-?\d+)[.]{2}(?P<last>-?\d+)}', data)
        match3 = re.match(r'(?i)\{[^,]*(,[^,]*)+}', data)

        if match1:
            first = match1.group(STRING.FIRST)
            last = match1.group(STRING.LAST)
            v1 = first if first < last else last
            v2 = last if first < last else first
            total = ord(v2) - ord(v1)
            if total > 26:
                other = re.escape('[\\]^_`')
                pattern = '[%s-Za-%s%s]' % (v1, v2, other)
            else:
                pattern = '[%s-%s]' % (v1, v2)
            return pattern
        elif match2:
            first = int(match2.group(STRING.FIRST))
            last = int(match2.group(STRING.LAST))
            pattern = self.get_pattern_for_two_numbers(first, last)
            return pattern
        elif match3:
            is_empty_item = False
            lst = []
            for item in str.split(data[SLICE.FIRST_TO_LAST], SYMBOL.COMMA):
                if item:
                    escaped_txt = self.escape_data(item)
                    lst.append(escaped_txt)
                else:
                    is_empty_item = True
            if lst:
                pattern = '(%s)' % str.join(SYMBOL.VERTICAL_LINE, lst)
                pattern = '%s?' % pattern if is_empty_item else pattern
                return pattern
            else:
                return STRING.EMPTY
        else:
            pattern = self.escape_data(data)
            return pattern

    def has_curly_bracket(self, data):      # noqa
        match = re.search(r'(\\?)[{][^}]+\1[}]', data)
        result = bool(match)
        return result

    def parse_curly_bracket(self, data):
        if re.search(r'\{.+?}', data):
            lst = []
            start = NUMBER.ZERO
            item = None
            for item in re.finditer(r'(\\?)[{][^}]+\1[}]', data):
                pre_matched = data[start:item.start()]
                # escaped_txt = re.escape(pre_matched)
                escaped_txt = self.escape_data(pre_matched)
                lst.append(escaped_txt)
                matched_txt = item.group()
                match_a = re.match(r'(\\?)[{] *(, *)+\1[}]', matched_txt)
                match1 = re.match(r'(\\?)[{] *\d+ *\1[}]', matched_txt)
                match2 = re.match(r'(\\?)[{] *\d* *, *\d* *\1[}]', matched_txt)
                match3 = re.match(r'[{][^}]+[}]', matched_txt)

                if match_a:
                    lst.append(STRING.EMPTY)
                elif match1 or match2:
                    new_matched_txt = matched_txt.replace('\\', '')
                    lst.append(new_matched_txt)
                elif match3:
                    expanded_txt = self.parse_shell_expansion(matched_txt)
                    lst.append(expanded_txt)
                else:
                    escaped_txt = self.escape_data(matched_txt)
                    lst.append(escaped_txt)
                start = item.end()
            if lst:
                post_matched = data[item.end():]
                escaped_txt = self.escape_data(post_matched)
                lst.append(escaped_txt)
            else:
                escaped_txt = self.escape_data(data)
                lst.append(escaped_txt)
            data = str.join(STRING.EMPTY, lst)
        else:
            data = self.escape_data(data)
        return data

    def parse_round_bracket(self, data):
        line = data
        if not line:
            return STRING.EMPTY
        elif re.match(PATTERN.SPACESATEOS, line):
            return PATTERN.SPACES

        lst = []
        start = NUMBER.ZERO
        item = None

        for item in re.finditer(r'(\\?)\((.+)(\1\))', line):
            pre_matched = line[start:item.start()]
            parsed_pre_matched = self.parse_square_bracket(pre_matched)
            parsed_pre_matched = self.replace_whitespace(parsed_pre_matched)
            lst.append(parsed_pre_matched)
            left, middle, right = item.groups()
            sub_pat = self.parse_round_bracket(middle)
            if sub_pat == SYMBOL.BACK_SLASH:
                parsed_matched_txt = '\\(%s\\)' % sub_pat
            else:
                parsed_matched_txt = '(%s)' % sub_pat
            lst.append(parsed_matched_txt)
            start = item.end()

        if lst:
            post_matched = line[item.end():]
            parsed_post_matched = self.parse_square_bracket(post_matched)
            parsed_post_matched = self.replace_whitespace(parsed_post_matched)
            lst.append(parsed_post_matched)
        else:
            parsed_txt = self.parse_square_bracket(line)
            parsed_txt = self.replace_whitespace(parsed_txt)
            lst.append(parsed_txt)

        pattern = str.join(STRING.EMPTY, lst)

        return pattern

    def parse_square_bracket(self, data):

        line = data
        if not line:
            return STRING.EMPTY
        elif re.match(PATTERN.SPACESATEOS, line):
            return PATTERN.SPACES

        lst = []
        start = NUMBER.ZERO
        item = None

        for item in re.finditer(r'\[.+?]', line):
            pre_matched = line[start:item.start()]
            parsed_pre_matched = self.parse_data(pre_matched)
            parsed_pre_matched = self.replace_whitespace(parsed_pre_matched)
            lst.append(parsed_pre_matched)
            matched_txt = item.group()
            if matched_txt.startswith('[!'):
                matched_txt = '[^%s' % matched_txt[SLICE.SKIP_FROM_SECOND]
            lst.append(matched_txt)
            start = item.end()

        if lst:
            post_matched = line[item.end():]
            parsed_post_matched = self.parse_data(post_matched)
            parsed_post_matched = self.replace_whitespace(parsed_post_matched)
            lst.append(parsed_post_matched)
        else:
            parsed_txt = self.parse_data(line)
            parsed_txt = self.replace_whitespace(parsed_txt)
            lst.append(parsed_txt)

        pattern = str.join(STRING.EMPTY, lst)

        return pattern

    def parse_data(self, data):
        if re.match(PATTERN.SPACESATEOS, data):
            return data if len(data) <= NUMBER.ONE else PATTERN.SPACES

        start = NUMBER.ZERO
        item = None
        lst = []
        for item in re.finditer(r'(\\?)[(].*\1[)]', data):
            pre_matched = data[start:item.start()]
            parsed_pre_matched = self.parse_curly_bracket(pre_matched)
            lst.append(parsed_pre_matched)

            parsed_matched = self.parse_curly_bracket(item.group())
            lst.append(parsed_matched)
            start = item.end()

        if lst:
            post_matched = data[item.end():]
            parsed_post_match = self.parse_curly_bracket(post_matched)
            lst.append(parsed_post_match)
        else:
            parsed_data = self.parse_curly_bracket(data)
            lst.append(parsed_data)

        pattern = str.join(STRING.EMPTY, lst)
        return pattern

    def mark_posix_char_class(self, line):      # noqa
        lst = ['alpha', 'alnum', 'blank', 'cntrl', 'digit', 'graph',
               'lower', 'print', 'space', 'upper', 'xdigit']

        for item in lst:
            pat = r'(?i)\[:%s:\]' % item
            placeholder = '__placeholder_%s_pat__' % item
            line = re.sub(pat, placeholder, line)

        return line

    def replace_posix_char_class(self, line):   # noqa
        tbl = dict(
            alpha=r'a-zA-Z',
            alnum=r'a-zA-Z0-9',
            blank=r' \t',
            cntrl=r'\x00-\x1f\x7f',
            digit=r'0-9',
            graph=r'\x21-\x7e',
            lower=r'a-z',
            print=r'\x20-\x7e',
            space=r' \t',
            upper=r'A-Z',
            xdigit=r'a-fA-F0-9'
        )
        for key, replaced in tbl.items():
            replacing = '__placeholder_%s_pat__' % key
            line = line.replace(replacing, replaced)
        return line

    def mark_word_bound(self, line):        # noqa
        pat = r'(\\<)(.*?)(\\>)'
        line = re.sub(pat, r'__placeholder_wb_pat__\2__placeholder_wb_pat__', line)
        return line

    def replace_word_bound(self, line):     # noqa
        line = line.replace('__placeholder_wb_pat__', r'\b')
        return line

    def replace_whitespace(self, line):
        start = NUMBER.ZERO
        item = None
        lst = []
        for item in re.finditer(r'( +)([+*?]?)', line):
            pre_matched = line[start:item.start()]
            lst.append(pre_matched)
            matched_txt = item.group()
            first, last = item.groups()
            is_single_ws = len(matched_txt) == NUMBER.ONE
            if last:
                lst.append(matched_txt)
            else:
                lst.append(self.ws_pattern if is_single_ws else self.multi_ws_pattern)
            start = item.end()
        if lst:
            post_matched = line[item.end():]
            lst.append(post_matched)
            pattern = str.join(STRING.EMPTY, lst)
            return pattern
        else:
            return line

    def parse_line(self, data):
        line = data
        if not line:
            return STRING.EMPTY
        elif re.match(PATTERN.SPACESATEOS, line):
            return PATTERN.SPACES

        is_start_of_line = False
        if line[SLICE.GET_FIRST] == SYMBOL.CARET:
            line = line[SLICE.SKIP_FROM_FIRST]
            is_start_of_line = True

        is_end_of_line = False
        if line[SLICE.GET_LAST] == SYMBOL.DOLLAR_SIGN:
            line = line[SLICE.TAKE_TO_LAST]
            is_end_of_line = True

        is_started_space = bool(re.match(PATTERN.SPACE, line))
        is_ended_space = bool(re.search(PATTERN.SPACEATEOS, line))
        line = line.strip()

        line = self.mark_posix_char_class(line)
        line = self.mark_word_bound(line)

        pattern = self.parse_round_bracket(line)

        if is_started_space or self.is_leading:
            pattern = '%s*%s' % (self.ws_pattern, pattern)
        if is_ended_space or self.is_trailing:
            pattern = '%s%s*' % (pattern, self.ws_pattern)

        pattern = self.replace_posix_char_class(pattern)
        pattern = self.replace_word_bound(pattern)

        if is_start_of_line and pattern and pattern[SLICE.GET_FIRST] != SYMBOL.CARET:
            pattern = '^%s' % pattern

        if is_end_of_line and pattern and pattern[SLICE.GET_LAST] != SYMBOL.DOLLAR_SIGN:
            pattern = '%s$' % pattern

        return pattern

    def parse_multiline(self, data):
        lst = []
        for line in re.split(PATTERN.MULTICRNL, data):
            pat = self.parse_line(line)
            lst.append(pat)

        pattern = str.join(PATTERN.MULTICRNL, lst)
        return pattern
