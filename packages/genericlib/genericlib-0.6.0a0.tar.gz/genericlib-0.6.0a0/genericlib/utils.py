"""Module containing the logic for utilities."""

import platform
import sys
import re
import copy

import subprocess

from io import StringIO

from textwrap import wrap
from textwrap import indent
from pprint import pprint

import typing

from .constant import ECODE
from .constant import STRING
# from .constnum import NUMBER
from .text import Text
from .collection import DotObject

from time import time


class Printer:
    """A printer class.

    Methods
    Printer.get(data, header='', footer='', failure_msg='', width=80, width_limit=20) -> str
    Printer.print(data, header='', footer='', failure_msg='', width=80, width_limit=20, print_func=None) -> None
    """
    @classmethod
    def get(cls, data, header='', footer='',
            width=80, width_limit=20, failure_msg=''):
        """Decorate data by organizing header, data, footer, and failure_msg

        Parameters
        ----------
        data (str, list): a text or a list of text.
        header (str): a header text.  Default is empty.
        footer (str): a footer text.  Default is empty.
        width (int): width of displayed text.  Default is 80.
        width_limit (int): minimum width of displayed text.  Default is 20.
        failure_msg (str): a failure message.  Default is empty.
        """
        lst = []
        result = []

        if width > 0:
            right_bound = width - 4
        else:
            right_bound = 76

        headers = []
        if header:
            if Misc.is_mutable_sequence(header):
                for item in header:
                    for line in str(item).splitlines():
                        headers.extend(wrap(line, width=right_bound))
            else:
                headers.extend(wrap(str(header), width=right_bound))

        footers = []
        if footer:
            if Misc.is_mutable_sequence(footer):
                for item in footer:
                    for line in str(item).splitlines():
                        footers.extend(wrap(line, width=right_bound))
            else:
                footers.extend(wrap(str(footer), width=right_bound))

        if data:
            data = data if Misc.is_mutable_sequence(data) else [data]
        else:
            data = []

        for item in data:
            if width > 0:
                if width >= width_limit:
                    for line in str(item).splitlines():
                        lst.extend(wrap(line, width=right_bound + 4))
                else:
                    lst.extend(line.rstrip() for line in str(item).splitlines())
            else:
                lst.append(str(item))
        length = max(len(str(i)) for i in lst + headers + footers)

        if width >= width_limit:
            length = right_bound if right_bound > length else length

        result.append(Text.format('+-{}-+', '-' * length))
        if header:
            for item in headers:
                result.append(Text.format('| {} |', item.ljust(length)))
            result.append(Text.format('+-{}-+', '-' * length))

        for item in lst:
            result.append(item)
        result.append(Text.format('+-{}-+', '-' * length))

        if footer:
            for item in footers:
                result.append(Text.format('| {} |', item.ljust(length)))
            result.append(Text.format('+-{}-+', '-' * length))

        if failure_msg:
            result.append(failure_msg)

        txt = str.join(STRING.NEWLINE, result)
        return txt

    @classmethod
    def print(cls, data, header='', footer='',
              width=80, width_limit=20, failure_msg='', print_func=None):
        """Decorate data by organizing header, data, footer, and failure_msg

        Parameters
        ----------
        data (str, list): a text or a list of text.
        header (str): a header text.  Default is empty.
        footer (str): a footer text.  Default is empty.
        width (int): width of displayed text.  Default is 80.
        width_limit (int): minimum width of displayed text.  Default is 20.
        failure_msg (str): a failure message.  Default is empty.
        print_func (function): a print function.  Default is None.
        """

        txt = Printer.get(data, header=header, footer=footer,
                          failure_msg=failure_msg, width=width,
                          width_limit=width_limit)

        print_func = print_func if callable(print_func) else print
        print_func(txt)

    @classmethod
    def get_message(cls, fmt, *args, style='format', prefix=''):
        """Get a message

        Parameters
        ----------
        fmt (str): string format.
        args (tuple): list of parameters for string interpolation.
        style (str): either format or %.
        prefix (str): a prefix.

        Returns
        -------
        str: a message.
        """

        if args:
            message = fmt.format(*args) if style == 'format' else fmt % args
        else:
            message = fmt

        message = '{} {}'.format(prefix, message) if prefix else message
        return message

    @classmethod
    def print_message(cls, fmt, *args, style='format', prefix='', print_func=None):
        """Print a message

        Parameters
        ----------
        fmt (str): string format.
        args (tuple): list of parameters for string interpolation.
        style (str): either format or %.
        prefix (str): a prefix.
        print_func (function): a print function.
        """
        message = cls.get_message(fmt, *args, style=style, prefix=prefix)
        print_func = print_func if callable(print_func) else print
        print_func(message)


class Misc:

    message = ''

    @classmethod
    def is_dict(cls, obj):
        return isinstance(obj, typing.Dict)

    @classmethod
    def is_mapping(cls, obj):
        return isinstance(obj, typing.Mapping)

    @classmethod
    def is_list(cls, obj):
        return isinstance(obj, typing.List)

    @classmethod
    def is_mutable_sequence(cls, obj):
        return isinstance(obj, (typing.List, typing.Tuple, typing.Set))

    @classmethod
    def is_sequence(cls, obj):
        return isinstance(obj, typing.Sequence)

    @classmethod
    def try_to_get_number(cls, obj, return_type=None):
        """Try to get a number

        Parameters
        ----------
        obj (object): a number or text number.
        return_type (int, float, bool): a referred return type.

        Returns
        -------
        tuple: status of number and value of number per referred return type
        """
        chk_lst = [int, float, bool]

        if cls.is_string(obj):
            data = obj.strip()
            try:
                if data.lower() == 'true' or data.lower() == 'false':
                    result = True if data.lower() == 'true' else False
                else:
                    result = float(data) if '.' in data else int(data)

                num = return_type(result) if return_type in chk_lst else result
                return True, num
            except Exception as ex:     # noqa
                cls.message = Text(ex)
                return False, obj
        else:
            is_number = cls.is_number(obj)
            num = return_type(obj) if return_type in chk_lst else obj

            if not is_number:
                txt = obj if cls.is_class(obj) else type(obj)
                cls.message = Text.format('Expecting number type, but got {}', txt)
            return is_number, num

    @classmethod
    def is_integer(cls, obj):
        if isinstance(obj, int):
            return True
        elif cls.is_string(obj):
            chk = obj.strip().isdigit()
            return chk
        else:
            return False

    @classmethod
    def is_boolean(cls, obj):
        if isinstance(obj, bool):
            return True
        elif cls.is_string(obj):
            val = obj.strip().lower()
            chk = val == 'true' or val == 'false'
            return chk
        elif cls.is_integer(obj):
            chk = int(obj) == 0 or int(obj) == 1
            return chk
        elif cls.is_float(obj):
            chk = float(obj) == 0 or float(obj) == 1
            return chk
        else:
            return False

    @classmethod
    def is_float(cls, obj):
        if isinstance(obj, (float, int)):
            return True
        elif cls.is_string(obj):
            try:
                float(obj)
                return True
            except Exception as ex:     # noqa
                return False
        else:
            return False

    @classmethod
    def is_number(cls, obj):
        result = cls.is_boolean(obj)
        result |= cls.is_integer(obj)
        result |= cls.is_float(obj)
        return result

    @classmethod
    def is_string(cls, obj):
        return isinstance(obj, typing.Text)

    @classmethod
    def is_class(cls, obj):
        return isinstance(obj, typing.Type)     # noqa

    @classmethod
    def is_callable(cls, obj):
        return isinstance(obj, typing.Callable)

    @classmethod
    def is_iterator(cls, obj):
        return isinstance(obj, typing.Iterator)

    @classmethod
    def is_generator(cls, obj):
        return isinstance(obj, typing.Generator)

    @classmethod
    def is_iterable(cls, obj):
        return isinstance(obj, typing.Iterable)

    @classmethod
    def is_none_type(cls, obj):
        return isinstance(obj, type(None))

    @classmethod
    def is_string_or_none(cls, obj):
        return isinstance(obj, (type(None), str))

    @classmethod
    def join_string(cls, *args, **kwargs):
        if not args:
            return ''
        if len(args) == 1:
            return str(args[0])

        sep = kwargs.get('separator', '')
        sep = kwargs.get('sep', sep)
        return str.join(sep, [str(item) for item in args])

    @classmethod
    def indent_string(cls, *args, width=2):
        width = width if width >= 0 else 0
        lst = []
        for item in args:
            item = item or ''
            lst.extend(str(item).splitlines())

        data = str.join(STRING.NEWLINE, lst)
        result = indent(data, ' ' * width)
        return result

    @classmethod
    def indent_string_level2(cls, *args, width=2, start_pos=1, other_width=4):

        start_pos = start_pos if start_pos >= 0 else 0
        other_width = other_width if other_width > width else width

        if start_pos == 0 or other_width == width:
            result = cls.indent_string(*args, width=width)
            return result

        lines = cls.indent_string(*args, width=0).splitlines()

        txt1 = indent(str.join(STRING.NEWLINE, lines[:start_pos]), ' ' * width)
        txt2 = indent(str.join(STRING.NEWLINE, lines[start_pos:]), ' ' * other_width)
        result = '%s\n%s' % (txt1, txt2)
        return result

    @classmethod
    def is_string_multiline(cls, txt):
        if not cls.is_string(txt):
            return False
        lines_count = len(txt.splitlines())
        return lines_count > 1

    @classmethod
    def skip_first_line(cls, data):
        if not cls.is_string(data):
            return data
        else:
            new_data = str.join(STRING.NEWLINE, data.splitlines()[1:])
            return new_data

    @classmethod
    def is_window_os(cls):
        chk = platform.system().lower() == 'windows'
        return chk

    @classmethod
    def is_mac_os(cls):
        chk = platform.system().lower() == 'darwin'
        return chk

    @classmethod
    def is_linux_os(cls):
        chk = platform.system().lower() == 'linux'
        return chk

    @classmethod
    def is_nix_os(cls):
        chk = cls.is_linux_os() or cls.is_mac_os()
        return chk

    @classmethod
    def escape_double_quote(cls, data):
        if not isinstance(data, str):
            return data
        new_data = data.replace('"', '\\"')
        return new_data

    @classmethod
    def escape_single_quote(cls, data):
        if not isinstance(data, str):
            return data
        new_data = data.replace("'", "\\'")
        return new_data

    @classmethod
    def escape_quote(cls, data):
        if not isinstance(data, str):
            return data
        new_data = re.sub('([\'"])', r'\\\1', data)
        return new_data

    @classmethod
    def get_first_char(cls, data, to_string=True, on_failure=False):
        if cls.is_string(data):
            result = data[:1]
            return result
        else:
            if to_string:
                txt = str(data)
                result = txt[:1]
                return result
            else:
                if on_failure:
                    fmt = ('Type of this data is %r.  Data must '
                           'be string type or to_string=True')
                    cls_name = data.__name__ if cls.is_class(data) else type(data).__name__
                    failure = fmt % cls_name
                    raise Exception(failure)
                else:
                    return ''

    @classmethod
    def get_last_char(cls, data, to_string=True, on_failure=False):
        if cls.is_string(data):
            result = data[-1:]
            return result
        else:
            if to_string:
                txt = str(data)
                result = txt[-1:]
                return result
            else:
                if on_failure:
                    fmt = ('Type of this data is %r.  Data must '
                           'be string type or to_string=True')
                    cls_name = data.__name__ if cls.is_class(data) else type(data).__name__
                    failure = fmt % cls_name
                    raise Exception(failure)
                else:
                    return ''

    @classmethod
    def get_clock_tick_str(cls, precision=10, dot_replaced='_',
                           prefix='', postfix=''):
        clock_tick_str = '%.*f' % (precision, time())
        clock_tick_str = clock_tick_str.replace(STRING.DOT_CHAR, dot_replaced)
        clock_tick_str = '%s%s' % (prefix, clock_tick_str) if prefix else clock_tick_str
        clock_tick_str = '%s%s' % (clock_tick_str, postfix) if postfix else clock_tick_str
        return clock_tick_str

    @classmethod
    def get_uniq_number_str(cls):
        uniq_str = cls.get_clock_tick_str()
        return uniq_str

    @classmethod
    def get_instance_class_name(cls, obj):
        cls_name = obj.__class__.__name__
        return cls_name

    @classmethod
    def is_data_line(cls, line):
        chk = re.search(r'\S+', str(line))
        return chk

    @classmethod
    def get_list_of_lines(cls, *lines):
        result = []

        for line in lines:
            line = STRING.EMPTY if line is None else str(line)
            result.extend(re.split(r'\r?\n|\r', line))

        if result == [STRING.EMPTY]:
            result = []

        return result

    @classmethod
    def get_list_of_readonly_lines(cls, *lines):
        result = cls.get_list_of_lines(*lines)
        return tuple(result)

    @classmethod
    def get_leading_line(cls, line, start=None, end=None):
        match = re.match(r'([^\S\r\n]+)?', str(line)[start:end])
        leading_spaces = match.group()
        return leading_spaces

    @classmethod
    def get_trailing_line(cls, line, start=None, end=None):
        match = re.search(r'([^\S\r\n]+)?$', str(line)[start:end])
        trailing_spaces = match.group()
        return trailing_spaces

    @classmethod
    def is_leading_line(cls, line, start=None, end=None):
        if not Misc.is_string(line):
            return False

        leading_spaces = cls.get_leading_line(line, start=start, end=end)
        is_leading = leading_spaces != STRING.EMPTY
        is_data_line = line.strip() != STRING.EMPTY
        chk = is_data_line and is_leading
        return chk

    @classmethod
    def is_trailing_line(cls, line, start=None, end=None):
        if not Misc.is_string(line):
            return False

        trailing_spaces = cls.get_trailing_line(line, start=start, end=end)
        is_trailing = trailing_spaces != STRING.EMPTY
        is_data_line = line.strip() != STRING.EMPTY
        chk = is_data_line and is_trailing
        return chk

    @classmethod
    def is_whitespace_in_line(cls, line):
        if not Misc.is_string(line):
            return False

        lst_of_ws = re.findall(r'\s+', line)
        if lst_of_ws:
            chk = any(bool(re.search(r'[^ \r\n]+', ws)) for ws in lst_of_ws)
            return chk
        else:
            return False


class MiscOutput:
    @classmethod
    def execute_shell_command(cls, cmdline):
        exit_code, output = subprocess.getstatusoutput(cmdline)
        result = DotObject(
            output=output,
            exit_code=exit_code,
            is_success=exit_code == ECODE.SUCCESS
        )
        return result


class MiscPlatform:
    @classmethod
    def get_kernel_info(cls):
        result = '{0.system} {0.release}'.format(platform.uname())
        return result

    @classmethod
    def get_python_info(cls):
        result = 'Python {}'.format(platform.python_version())
        return result

    @classmethod
    def get_python_docs_url(cls):
        fmt = 'https://docs.python.org/{0.major}.{0.minor}/'
        result = fmt.format(sys.version_info)
        return result


class MiscFunction:
    @classmethod
    def do_silent_invoke(cls, callable_obj, *args, filename='', **kwargs):
        stdout_bak = sys.stdout
        stderr_bak = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        ret_result = callable_obj(*args, **kwargs)

        sys.stdout.seek(0)
        sys.stderr.seek(0)

        stdout_result = sys.stdout.read()
        stderr_result = sys.stderr.read()

        if stderr_result:
            output_and_error = '%s\n%s' % (stdout_result, stderr_result)
        else:
            output_and_error = stdout_result

        result = DotObject(
            result=ret_result,
            output=stdout_result,
            error=stderr_result,
            output_and_error=output_and_error
        )

        if filename:
            with(open(filename, 'w')) as stream:
                stream.write(result.output_and_error)

        sys.stdout = stdout_bak
        sys.stderr = stderr_bak

        return result

    @classmethod
    def create_runtime_error(cls, obj=None, msg=''):
        cls_name = obj.__class__.__name__
        exc_cls_name = obj if cls_name == 'str' else '%sRTError' % cls_name
        exc_cls = type(exc_cls_name, (Exception,), {})
        exc_obj = exc_cls(msg)
        return exc_obj

    @classmethod
    def raise_runtime_error(cls, obj=None, msg=''):
        exc_obj = cls.create_runtime_error(obj=obj, msg=msg)
        raise exc_obj


class MiscObject:
    @classmethod
    def copy(cls, instance, is_deep_copy=True):
        if is_deep_copy:
            new_instance = copy.deepcopy(instance)
        else:
            new_instance = copy.copy(instance)
        return new_instance

    @classmethod
    def cleanup_list_of_dict(cls, lst_of_dict, chars=None):
        if not Misc.is_list(lst_of_dict):
            return lst_of_dict
        lst = []
        for node in lst_of_dict:
            if Misc.is_dict(node):
                new_node = dict()
                for key, val in node.items():
                    if Misc.is_string(val):
                        new_node[key] = str.strip(val, chars)
                    else:
                        new_node[key] = cls.copy(val)
                lst.append(new_node)
            else:
                lst.append(cls.copy(node))
        return lst


class Tabular:
    """Construct Tabular Format

    Attributes
    _________
    data (list): a list of dictionary or a dictionary.
    columns (list): a list of selecting headers.  Default is None.
    justify (str): left|right|center.  Default is a left justification.
    missing (str): report missing value if column is not found.
            Default is not_found.

    Methods
    -------
    validate_argument_list_of_dict() -> None
    build_width_table(columns) -> dict
    align_string(value, width) -> str
    build_headers_string(columns, width_tbl) -> str
    build_tabular_string(columns, width_tbl) -> str
    process() -> None
    get() -> str or raw data
    print() -> None

    """
    def __init__(self, data, columns=None, justify='left', missing='not_found'):
        self.result = ''
        if isinstance(data, dict):
            self.data = [data]
        else:
            self.data = data
        self.columns = columns
        self.justify = str(justify).lower()
        self.missing = missing
        self.is_ready = True
        self.is_tabular = False
        self.failure = ''
        self.validate_argument_list_of_dict()
        self.process()

    def validate_argument_list_of_dict(self):
        """Validate a list of dictionary for tabular format."""
        if not isinstance(self.data, (list, tuple)):
            self.is_ready = False
            self.failure = 'data MUST be a list.'
            return

        if not self.data:
            self.is_ready = False
            self.failure = 'data MUST be NOT an empty list.'
            return

        chk_keys = list()
        for a_dict in self.data:
            if isinstance(a_dict, dict):
                if not a_dict:
                    self.is_ready = False
                    self.failure = 'all dict elements MUST be NOT empty.'
                    return

                keys = list(a_dict.keys())
                if not chk_keys:
                    chk_keys = keys
                else:
                    if keys != chk_keys:
                        self.is_ready = False
                        self.failure = 'dict element MUST have same keys.'
                        return
            else:
                self.is_ready = False
                self.failure = 'all elements of list MUST be dictionary.'
                return

    def build_width_table(self, columns):
        """return mapping table of string length.

        Parameters
        ----------
        columns (list): headers of tabular data

        Returns
        -------
        dict: a mapping table of string length.
        """
        width_tbl = dict(zip(columns, (len(str(k)) for k in columns)))

        for a_dict in self.data:
            for col, width in width_tbl.items():
                curr_width = len(str(a_dict.get(col, self.missing)))
                new_width = max(width, curr_width)
                width_tbl[col] = new_width
        return width_tbl

    def align_string(self, value, width):
        """return an aligned string

        Parameters
        ----------
        value (Any): a data.
        width (int): a width for data alignment.

        Returns
        -------
        str: a string.
        """
        value = str(value)
        if self.justify == 'center':
            return str.center(value, width)
        elif self.justify == 'right':
            return str.rjust(value, width)
        else:
            return str.ljust(value, width)

    def build_headers_string(self, columns, width_tbl):
        """Return headers as string

        Parameters
        ----------
        columns (list): a list of headers.
        width_tbl (dict): a mapping table of string length.

        Returns
        -------
        str: headers as string.
        """
        lst = []
        for col in columns:
            width = width_tbl.get(col)
            new_col = self.align_string(col, width)
            lst.append(new_col)
        return '| {} |'.format(str.join(' | ', lst))

    def build_tabular_string(self, columns, width_tbl):
        """Build data to tabular format

        Parameters
        ----------
        columns (list): a list of headers.
        width_tbl (dict): a mapping table of string length.

        Returns
        -------
        str: a tabular data.
        """
        lst_of_str = []
        for a_dict in self.data:
            lst = []
            for col in columns:
                val = a_dict.get(col, self.missing)
                width = width_tbl.get(col)
                new_val = self.align_string(val, width)
                lst.append(new_val)
            lst_of_str.append('| {} |'.format(str.join(' | ', lst)))

        return str.join(STRING.NEWLINE, lst_of_str)

    def process(self):
        """Process data to tabular format."""
        if not self.is_ready:
            return

        try:
            keys = list(self.data[0].keys())
            columns = self.columns or keys
            width_tbl = self.build_width_table(columns)
            deco = ['-' * width_tbl.get(c) for c in columns]
            deco_str = '+-{}-+'.format(str.join('-+-', deco))
            headers_str = self.build_headers_string(columns, width_tbl)
            tabular_data = self.build_tabular_string(columns, width_tbl)

            lst = [deco_str, headers_str, deco_str, tabular_data, deco_str]
            self.result = str.join(STRING.NEWLINE, lst)
            self.is_tabular = True
        except Exception as ex:
            self.failure = '{}: {}'.format(type(ex).__name__, ex)
            self.is_tabular = False

    def get(self):
        """Return result if a provided data is tabular format, otherwise, data"""
        tabular_data = self.result if self.is_tabular else self.data
        return tabular_data

    def print(self):
        """Print the tabular content"""
        tabular_data = self.get()
        if isinstance(tabular_data, (dict, list, tuple, set)):
            pprint(tabular_data)
        else:
            print(tabular_data)


def get_data_as_tabular(data, columns=None, justify='left', missing='not_found'):
    """translate data (i.e a list of string or dictionary) to tabular format

    Parameters
    __________
    data (list): a list of dictionary or a dictionary.
    columns (list): a list of selecting headers.  Default is None.
    justify (str): left|right|center.  Default is a left justification.
    missing (str): report missing value if column is not found.
            Default is not_found.

    Returns:
        str: tabular format
    """
    node = Tabular(data, columns=columns, justify=justify, missing=missing)
    result = node.get()
    return result


def print_data_as_tabular(data, columns=None, justify='left', missing='not_found'):
    """print data (i.e a list of string or dictionary) as tabular format

    Parameters
    __________
    data (list): a list of dictionary or a dictionary.
    columns (list): a list of selecting headers.  Default is None.
    justify (str): left|right|center.  Default is a left justification.
    missing (str): report missing value if column is not found.
            Default is not_found.
    """
    node = Tabular(data, columns=columns, justify=justify, missing=missing)
    node.print()
