from .constant import STRING
import re
import string

from .exceptions import LineArgumentError


class BaseText(str):
    def __new__(cls, *args, **kwargs):
        arg0 = args[0] if args else None
        if args and isinstance(arg0, BaseException):
            txt = str.__new__(cls, '{}: {}'.format(type(arg0).__name__, arg0))
            return txt
        else:
            txt = str.__new__(cls, *args, **kwargs)
            return txt


class Text(BaseText):
    @classmethod
    def format(cls, *args, **kwargs):
        if not args:
            text = ''
            return text
        else:
            if kwargs:
                fmt = args[0]
                try:
                    text = str(fmt).format(args[1:], **kwargs)
                    return text
                except Exception as ex:
                    text = cls(ex)
                    return text
            else:
                if len(args) == 1:
                    text = cls(args[0])
                    return text
                else:
                    fmt = args[0]
                    t_args = tuple(args[1:])
                    try:
                        if len(t_args) == 1 and isinstance(t_args[0], dict):
                            text = str(fmt) % t_args[0]
                        else:
                            text = str(fmt) % t_args

                        if text == fmt:
                            text = str(fmt).format(*t_args)
                        return text
                    except Exception as ex1:
                        try:
                            text = str(fmt).format(*t_args)
                            return text
                        except Exception as ex2:
                            text = '%s\n%s' % (cls(ex1), cls(ex2))
                            return text

    @classmethod
    def wrap_html(cls, tag, data, *args):
        data = str(data)
        tag = str(tag).strip()
        attributes = [str(arg).strip() for arg in args if str(arg).strip()]
        if attributes:
            attrs_txt = str.join(STRING.SPACE_CHAR, attributes)
            if data.strip():
                result = '<{0} {1}>{2}</{0}>'.format(tag, attrs_txt, data)
            else:
                result = '<{0} {1}/>'.format(tag, attrs_txt)
        else:
            if data.strip():
                result = '<{0}>{1}</{0}>'.format(tag, data)
            else:
                result = '<{0}/>'.format(tag)
        return result

    def do_finditer_split(self, pattern):
        result = []
        start = 0
        m = None
        for m in re.finditer(pattern, self):
            pre_match = self[start:m.start()]
            match = m.group()
            result.append(pre_match)
            result.append(match)
            start = m.end()

        if m:
            post_match = self[m.end():]
            result.append(post_match)
        else:
            result.append(str(self))
        return result


class BaseLine(str):
    def __new__(cls, data, *args):
        new_base_line_obj = str.__new__(cls, data)
        lines = new_base_line_obj.splitlines(keepends=True)
        if len(lines) == 1:
            __line = lines[0] if lines else ''
            cls.__raw_data = __line
            cls.__data = re.match(r"([^\r\n]+)?", __line)
            cls.__joiner = re.search(r"([\r\n]+)?$", __line)
            return new_base_line_obj
        else:
            error = "data argument is multi-lines.  MUST be a single line."
            raise LineArgumentError(error)


class Line(BaseLine):

    @property
    def joiner(self):
        return self.__joiner

    @property
    def raw_data(self):
        return self.__raw_data

    @property
    def clean_line(self):
        return self.strip()

    @property
    def is_empty(self):
        return self == ""

    @property
    def is_optional_empty(self):
        return bool(re.match(r"\s+$", self))

    @property
    def leading(self):
        leading_chars = re.match(r'(\s+)?', self).group()
        return leading_chars

    @property
    def trailing(self):
        trailing_chars = re.search(r'(\s+)?$', self).group()
        return trailing_chars

    @property
    def is_leading(self):
        return len(self.leading) > 0

    @property
    def is_trailing(self):
        return len(self.trailing) > 0

    @classmethod
    def is_line(cls, data, on_failure=False):
        lines = str(data).splitlines(keepends=True)
        if len(lines) == 1:
            return True

        if on_failure:
            error = "data argument is multi-lines.  MUST be a single line."
            raise LineArgumentError(error)
        else:
            return False

    def convert_to_regex_pattern(self):
        result = []
        punct_pat = BaseMatchedObject.punctuation_pattern
        pat = f'({punct_pat}+ +)\\1+'
        other_pat = r'\s+'
        if re.search(pat, self):
            items = self.do_finditer_split(self, pattern=pat)
            for item in items:
                if isinstance(item, (PreMatchedObject, PostMatchedObject)):
                    lst = self.do_finditer_split(item.data, pattern=other_pat)
                    result.extend(lst)
                else:
                    result.append(item)
        elif re.search(other_pat, self):
            result = self.do_finditer_split(self, pattern=other_pat)
        else:
            result = [BaseMatchedObject(self)]
        text_pattern = ''.join(elmt.to_pattern() for elmt in result)
        return text_pattern

    def do_finditer_split(self, data, pattern=r'\s+'):  # noqa
        result = []
        start = 0
        match = None
        for match in re.finditer(pattern, data):
            pre_obj = PreMatchedObject(match, start)
            not pre_obj.is_empty and result.append(pre_obj)

            matched_obj = MatchedObject(match)
            result.append(matched_obj)
            start = match.end()

        if match is not None:
            post_obj = PostMatchedObject(match, start)
            not post_obj.is_empty and result.append(post_obj)
        else:
            result.append(BaseMatchedObject(data))
        return result


class BaseMatchedObject:

    punctuation_pattern = r'[!\"#$%&\'()*+,./:;<=>?@\[\\\]\^_`{|}~-]'
    repeated_punctuation_pattern = f'({punctuation_pattern}+?)\\1+'
    repeated_punctuations_space_pattern = f'({punctuation_pattern}+ +)\\1+'
    default_separator = ''
    user_separator = ''

    def __init__(self, match):
        self.match = None if isinstance(match, str) else match
        self.data = match if isinstance(match, str) else ''

    @property
    def is_empty(self):
        return self.data == ''

    def change_separator(self, separator=' ', user_pattern=''):
        self.user_separator = user_pattern
        self.default_separator = separator

    def to_pattern(self):
        result = dict()
        result.update(self.get_whitespace_pattern())
        result.update(self.get_repeated_puncts_space_pattern())
        result.update(self.get_repeated_puncts_pattern())
        result.update(self.get_text_pattern())
        pattern = [key for key, value in result.items() if value][0]
        return pattern

    def get_whitespace_pattern(self):
        if not re.match(r'\s+$', self.data):
            return {'': False}

        if self.user_separator:
            return self.user_separator, True

        total = len(self.data)
        is_space = self.data[0] == ' ' and len(set(self.data)) == 1
        if self.default_separator:
            pattern = self.default_separator
        else:
            pattern = ' ' if is_space else r'\s'
        pattern = f'{pattern}+' if total > 1 else pattern

        return {pattern: True}

    def get_text_pattern(self):
        pattern = do_soft_regex_escape(self.data)
        return {pattern: True}

    def get_repeated_puncts_pattern(self):
        if not re.match(f'{self.punctuation_pattern}+$', self.data):
            return {'': False}
        else:
            start, m, pattern = 0, None, ''
            for m in re.finditer(self.repeated_punctuation_pattern, self.data):
                pattern += do_soft_regex_escape(self.data[start:m.start()])
                found = m.group()
                repeated = str.join('', dict(zip(found, found)))
                fmt = '%s{2,}' if len(repeated) == 1 else '(%s){2,}'
                pattern += fmt % do_soft_regex_escape(repeated)
                start = m.end()
            else:
                if m:
                    pattern += do_soft_regex_escape(self.data[m.end():])
                    return {pattern: True}
                else:
                    pattern = do_soft_regex_escape(self.data)
                    return {pattern: True}

    def get_repeated_puncts_space_pattern(self):
        match = re.match(f'{self.repeated_punctuations_space_pattern}$', self.data)
        if not match:
            return {'': False}
        found = match.groups()[0]
        puncts_pat = do_soft_regex_escape(found.strip())
        space_pat = ' +' if '  ' in found else ' '
        pattern = '(%s%s){2,}' % (puncts_pat, space_pat)
        return {pattern: True}


class MatchedObject(BaseMatchedObject):
    def __init__(self, match):
        super().__init__(match)
        self.data = match.group()


class PreMatchedObject(BaseMatchedObject):
    def __init__(self, match, start):
        super().__init__(match)
        self.data = match.string[start: match.start()]


class PostMatchedObject(BaseMatchedObject):
    def __init__(self, match, start):
        super().__init__(match)
        self.data = match.string[start:]


def get_generic_error_msg(instance, fmt, *other):
    args = ['%sError' % instance.__class__.__name__]
    args.extend(other)
    new_fmt = '%%s - %s' % fmt
    err_msg = new_fmt % tuple(args)
    return err_msg


def get_whitespace_chars(k=8, to_list=True):
    lst = [chr(i) for i in range(pow(2, k)) if re.search(r"\s", chr(i))]
    return frozenset(lst) if to_list else str.join('', lst)


ASCII_WHITESPACE_CHARS = get_whitespace_chars(k=8, to_list=True)
ASCII_WHITESPACE_STRING = get_whitespace_chars(k=8, to_list=False)
WHITESPACE_CHARS = get_whitespace_chars(k=16, to_list=True)
WHITESPACE_STRING = get_whitespace_chars(k=16, to_list=False)


def get_non_whitespace_chars(k=8, to_list=True):
    lst = [chr(i) for i in range(pow(2, k)) if not re.search(r"\s", chr(i))]
    return frozenset(lst) if to_list else str.join('', lst)


ASCII_NON_WHITESPACE_CHARS = get_non_whitespace_chars(k=8, to_list=True)
ASCII_NON_WHITESPACE_STRING = get_non_whitespace_chars(k=8, to_list=False)
NON_WHITESPACE_CHARS = get_non_whitespace_chars(k=16, to_list=True)
NON_WHITESPACE_STRING = get_non_whitespace_chars(k=16, to_list=False)


def do_soft_regex_escape(pattern):
    """Escape special characters in a string.  This method will help
    consistency pattern during invoking re.escape on different Python version.
    """
    chk1 = f'{string.punctuation} '
    chk2 = '^$.?*+|{}[]()\\'
    result = []
    for char in pattern:
        escape_char = re.escape(char)
        if char in chk1:
            result.append(escape_char if char in chk2 else char)
        else:
            result.append(escape_char)
    new_pattern = ''.join(result)
    re.compile(new_pattern)
    return new_pattern


def enclose_string(text, quote='"', is_new_line=False):
    """enclose text with either double-quote or triple double-quote

    Parameters
    ----------
    text (str): a text

    Returns
    -------
    str: a new string with enclosed double-quote or triple double-quote
    """
    text = str(text)
    reformat_txt = text.replace(quote, '\\' + quote)

    if len(re.split(r'\r?\n|\r', text)) > 1:
        fmt = f'{quote*3}\n%s\n{quote*3}' if is_new_line else f'{quote*3}%s{quote*3}'
        enclosed_txt = fmt % reformat_txt
        return enclosed_txt
    else:
        enclosed_txt = f'{quote}{reformat_txt}{quote}'
        return enclosed_txt
