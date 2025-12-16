
import re
from copy import deepcopy

from .constnum import NUMBER
from .constant import STRING


class DictObject(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def __setattr__(self, attr, value):
        super().__setattr__(attr, value)
        self.update(**{attr: value, 'is_updated_attr': False})

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.update({key: value})

    def update(self, *args, is_updated_attr=True, **kwargs):
        chk_lst = [
            'False', 'None', 'True',
            'and', 'as', 'assert', 'await', 'break', 'class', 'continue',
            'def', 'del', 'else', 'except', 'finally', 'for', 'from',
            'global', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not',
            'pass', 'raise', 'return', 'try', 'while', 'with'
        ]

        obj = dict(*args, **kwargs)
        super().update(obj)
        if is_updated_attr:
            for attr, value in obj.items():
                if isinstance(attr, str) and re.match(r'(?i)[a-z]\w*$', attr):
                    attr = '%s_' % attr if attr in chk_lst else attr
                    setattr(self, attr, value)


class DotObject(DictObject):
    def __getattribute__(self, attr):
        value = super().__getattribute__(attr)
        return DotObject(value) if isinstance(value, dict) else value

    def __getitem__(self, key):
        value = super().__getitem__(key)
        return DotObject(value) if isinstance(value, dict) else value


def substitute_variable(data, root_var_name='self'):
    """substitute variable within data structure if there

    Parameters
    ----------
    data (dict): a dictionary.
    root_var_name (str): root variable of data structure for
            variable substitution.  Default is self.

    Returns
    -------
    dict: a new dictionary if substituted, otherwise, the given data.

    """
    def replace(txt, **kwargs):
        if len(kwargs) == NUMBER.ONE:
            var_name = list(kwargs)[NUMBER.ZERO]
            pattern = r'(?i)[{]%s([.][a-z]\w*)+[}]' % var_name
        else:
            pattern = r'(?i)[{][a-z]\w*([.][a-z]\w*)+[}]'
        lines = txt.splitlines()
        for index, line in enumerate(lines):
            if line.strip():
                lst = []
                start = NUMBER.ZERO
                for match in re.finditer(pattern, line):
                    lst.append(line[start:match.start()])
                    start = match.end()
                    matched_result = match.group()
                    try:
                        val = matched_result.format(**kwargs)
                        lst.append(val)
                    except Exception as ex:     # noqa
                        lst.append(matched_result)
                else:
                    if lst:
                        lst.append(line[start:])
                        lines[index] = str.join(STRING.EMPTY, lst)

        new_txt = str.join(STRING.NEWLINE, lines)
        return new_txt

    def substitute(node, variables_):
        if isinstance(node, dict):
            for key, val in node.items():
                if isinstance(val, dict) or isinstance(val, list):
                    substitute(val, variables_)
                else:
                    if isinstance(val, str):
                        new_val = replace(val, **variables_)
                        node[key] = new_val
        elif isinstance(node, list):
            for index, item in enumerate(node):
                if isinstance(item, dict) or isinstance(item, list):
                    substitute(item, variables_)
                else:
                    if isinstance(item, str):
                        new_item = item.format(obj=variables_)
                        node[index] = new_item
        else:
            return

    if not isinstance(data, dict):
        return data

    substituted_data = DotObject(deepcopy(data))
    substitute(substituted_data, {root_var_name: substituted_data})
    new_data = deepcopy(data)
    variables = {root_var_name: substituted_data}
    substitute(new_data, variables)
    return new_data
