import csv
import re
import os
import filecmp
import shutil
import functools

from pathlib import Path
from pathlib import PurePath
from pathlib import WindowsPath
from datetime import datetime

import yaml
import json

from genericlib import Text
from genericlib import DotObject
from genericlib import substitute_variable

from .constant import STRING


def try_to_call(func):
    """Wrap the classmethod and return False if on_failure is false.

    Parameters
    ----------
    func (function): a callable function
    """
    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):
        """A Wrapper Function"""
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as ex:
            if kwargs.get('on_failure', False):
                raise ex
            else:
                if len(args) >= 1:
                    args[0].message = Text(ex)
                    args[0].on_failure = False
                    return False
                else:
                    raise ex
    return wrapper_func


def try_to_other_call(func):
    """Wrap the classmethod and return empty string if on_failure is false.

    Parameters
    ----------
    func (function): a callable function
    """
    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):
        """A Wrapper Function"""
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as ex:
            if kwargs.get('on_failure', False):
                raise ex
            else:
                if len(args) >= 1:
                    args[0].message = Text(ex)
                    args[0].on_failure = False
                    return ''
                else:
                    raise ex
    return wrapper_func


class File:
    message = ''
    on_failure = False

    @classmethod
    def clean(cls):
        cls.message = ''

    @classmethod
    @try_to_call
    def is_file(cls, filename, on_failure=False):
        """Check filename is a file

        Parameters
        ----------
        filename (str): a file name

        Returns
        -------
        bool: True if it is a file, otherwise False
        """
        cls.clean()
        cls.on_failure = on_failure
        file_obj = Path(filename)
        return file_obj.is_file()

    @classmethod
    @try_to_call
    def is_dir(cls, file_path, on_failure=False):
        """Check file_path is a directory

        Parameters
        ----------
        file_path (str): a location of file

        Returns
        -------
        bool: True if it is a directory, otherwise False
        """
        cls.clean()
        cls.on_failure = on_failure
        file_obj = Path(file_path)
        return file_obj.is_dir()

    @classmethod
    @try_to_call
    def is_exist(cls, filename, on_failure=False):
        """Check file existence

        Parameters
        ----------
        filename (str): a file name

        Returns
        -------
        bool: True if existed, otherwise False
        """
        cls.clean()
        cls.on_failure = on_failure
        file_obj = Path(filename)
        return file_obj.exists()

    @classmethod
    @try_to_other_call
    def copy_file(cls, src, dst, on_failure=False):
        """copy source file to destination

        Parameters
        ----------
        src (str): a source of file
        dst (str): a destination file or directory

        Returns
        -------
        str: a copied file if successfully copied, otherwise empty string
        """
        cls.clean()
        cls.on_failure = on_failure
        copied_file = shutil.copy2(src, dst)
        return copied_file

    @classmethod
    def copy_files(cls, src, dst, on_failure=False):
        """copy source file(s) to destination

        Parameters
        ----------
        src (str, list): a source of file or files
        dst (str): a destination directory

        Returns
        -------
        list: a list of a copied file if successfully copied, otherwise empty list
        """
        cls.clean()
        cls.make_directory(dst, showed=False)

        empty_list = []
        if isinstance(src, list):
            copied_files = empty_list
            for file in src:
                copied_file = cls.copy_file(file, dst, on_failure=on_failure)
                if cls.message:
                    return copied_files
                copied_files.append(copied_file)
            return copied_files
        else:
            copied_file = cls.copy_file(src, dst)
            if cls.message:
                return empty_list
            else:
                return [copied_file]

    @classmethod
    @try_to_call
    def make_directory(cls, file_path, showed=True, on_failure=False):
        """create a directory

        Parameters
        ----------
        file_path (str): a file location
        showed (bool): showing the message of creating folder

        Returns
        -------
        bool: True if created, otherwise False
        """
        cls.clean()
        cls.on_failure = on_failure

        if cls.is_exist(file_path):
            if cls.is_dir(file_path):
                cls.message = Text.format('%r directory is already existed.', file_path)
                return True
            else:
                cls.message = Text.format('Existing %r IS NOT a directory.', file_path)
                return False

        file_obj = Path(file_path)
        file_obj.mkdir(parents=True, exist_ok=True)
        fmt = '{:%Y-%m-%d %H:%M:%S.%f} - {} folder is created.'
        showed and print(fmt.format(datetime.now(), file_path))
        cls.message = Text.format('{} folder is created.', file_path)
        return True

    @classmethod
    def make_dir(cls, file_path, showed=True, on_failure=False):
        """create a directory

        Parameters
        ----------
        file_path (str): a file location
        showed (bool): showing the message of creating folder

        Returns
        -------
        bool: True if created, otherwise False
        """
        result = cls.make_directory(file_path, showed=showed, on_failure=on_failure)
        return result

    @classmethod
    @try_to_call
    def create(cls, filename, showed=True, on_failure=False):
        """Check file existence

        Parameters
        ----------
        filename (str): a file name
        showed (bool): showing the message of creating file

        Returns
        -------
        bool: True if created, otherwise False
        """
        cls.clean()
        cls.on_failure = on_failure

        filename = cls.get_path(str(filename).strip())
        if cls.is_exist(filename):
            cls.message = 'File is already existed.'
            return True

        file_obj = Path(filename)
        if not file_obj.parent.exists():
            file_obj.parent.mkdir(parents=True, exist_ok=True)
        file_obj.touch()
        fmt = '{:%Y-%m-%d %H:%M:%S.%f} - {} file is created.'
        showed and print(fmt.format(datetime.now(), filename))
        cls.message = Text.format('{} file is created.', filename)
        return True

    @classmethod
    def get_path(cls, *args, is_home=False):
        """Create a file path

        Parameters
        ----------
        args (tuple): a list of file items
        is_home (bool): True will include Home directory.  Default is False.

        Returns
        -------
        str: a file path.
        """
        lst = [Path.home()] if is_home else []
        lst.extend(list(args))
        file_path = str(Path(PurePath(*lst)).expanduser().absolute())
        return file_path

    @classmethod
    def get_dir(cls, file_path):
        """get directory from existing file path

        Parameters
        ----------
        file_path (string): file path

        Returns
        -------
        str: directory
        """
        file_obj = Path(file_path).expanduser().absolute()
        if file_obj.is_dir():
            return str(file_obj)
        elif file_obj.is_file():
            return str(file_obj.parent)
        else:
            fmt = 'FileNotFoundError: No such file or directory "{}"'
            cls.message = Text.format(fmt, file_path)
            return ''

    @classmethod
    def get_filepath_timestamp_format1(cls, *args, prefix='', extension='',
                                       is_full_path=False, ref_datetime=None):
        """Create a file path with timestamp format1

        Parameters
        ----------
        args (tuple): a list of file items
        prefix (str): a prefix for base name of file path.  Default is empty.
        extension (str): an extension of file.  Default is empty.
        is_full_path (bool): show absolute full path.  Default is False.
        ref_datetime (datetime.datetime): a reference datetime instance.

        Returns
        -------
        str: a file path with timestamp format1.
        """
        lst = list(args)

        ref_datetime = ref_datetime if isinstance(ref_datetime, datetime) else datetime.now()

        basename = '{:%Y%b%d_%H%M%S}'.format(ref_datetime)
        if prefix.strip():
            basename = '%s_%s' % (prefix.strip(), basename)

        if extension.strip():
            basename = '%s.%s' % (basename, extension.strip().strip('.'))

        lst.append(basename)
        file_path = cls.get_path(*lst) if is_full_path else str(Path(*lst))
        return file_path

    @classmethod
    @try_to_other_call
    def get_content(cls, file_path, on_failure=False):
        """get content of file

        Parameters
        ----------
        file_path (string): file path

        Returns
        -------
        str: content of file
        """
        cls.clean()
        cls.on_failure = on_failure

        filename = cls.get_path(file_path)
        with open(filename) as stream:
            content = stream.read()
            return content

    @classmethod
    def get_result_from_yaml_file(
        cls, file_path, base_dir='', is_stripped=True, dot_datatype=False,
        default=None, var_substitution=False, root_var_name='self'
    ):
        """get result of YAML file

        Parameters
        ----------
        file_path (string): file path
        base_dir (str): a based directory
        is_stripped (bool): removing leading or trailing space.  Default is True.
        dot_datatype (bool): convert a return_result to DotObject if
                return_result is dictionary.  Default is False.
        default (object): a default result file is not found.  Default is empty dict.
        var_substitution (bool): internal variable substitution.  Default is False.
        root_var_name (str): root variable of data structure for
                variable substitution.  Default is self.

        Returns
        -------
        object: YAML result
        """
        default = default or dict()

        cls.clean()
        yaml_result = default

        try:
            if base_dir:
                filename = cls.get_path(cls.get_dir(base_dir), file_path)
            else:
                filename = cls.get_path(file_path)

            with open(filename) as stream:
                content = stream.read()
                if is_stripped:
                    content = content.strip()

                if content:
                    yaml_result = yaml.safe_load(content)
                    cls.message = Text.format('loaded {}', filename)
                else:
                    cls.message = Text.format('"{}" file is empty.', filename)

        except Exception as ex:
            cls.message = Text(ex)

        if var_substitution:
            yaml_result = substitute_variable(yaml_result,
                                              root_var_name=root_var_name)

        if isinstance(yaml_result, dict) and dot_datatype:
            dot_result = DotObject(yaml_result)
            return dot_result
        else:
            return yaml_result

    @classmethod
    @try_to_call
    def save(cls, filename, data, on_failure=False):
        """save data to file

        Parameters
        ----------
        filename (str): filename
        data (str): data.

        Returns
        -------
        bool: True if successfully saved, otherwise, False
        """
        cls.clean()
        cls.on_failure = on_failure

        if isinstance(data, list):
            content = str.join(STRING.NEWLINE, [str(item) for item in data])
        else:
            content = str(data)

        filename = cls.get_path(filename)
        if not cls.create(filename):
            return False

        file_obj = Path(filename)
        file_obj.touch()
        file_obj.write_text(content)
        cls.message = Text.format('Successfully saved data to "{}" file', filename)
        return True

    @classmethod
    @try_to_call
    def delete(cls, filename, on_failure=False):
        """Delete file

        Parameters
        ----------
        filename (str): filename

        Returns
        -------
        bool: True if successfully deleted, otherwise, False
        """
        cls.clean()
        cls.on_failure = on_failure

        filepath = File.get_path(filename)
        file_obj = Path(filepath)
        if file_obj.is_dir():
            shutil.rmtree(filename)
            cls.message = Text.format('Successfully deleted "{}" folder', filename)
        else:
            file_obj.unlink()
            cls.message = Text.format('Successfully deleted "{}" file', filename)
        return True

    @classmethod
    def change_home_dir_to_generic(cls, filename):
        """change HOME DIRECTORY in filename to generic name
        ++++++++++++++++++++++++++++++++++++++++++++++
        Note: this function only uses for displaying.
        ++++++++++++++++++++++++++++++++++++++++++++++
        """
        node = Path.home()
        home_dir = str(node)
        if isinstance(node, WindowsPath):
            replaced = '%HOMEDRIVE%\\%HOMEPATH%'
        else:
            replaced = '${HOME}'
        new_name = filename.replace(home_dir, replaced)
        return new_name

    @classmethod
    def is_duplicate_file(cls, file, source):
        if isinstance(source, list):
            for other_file in source:
                chk = filecmp.cmp(file, other_file)
                if chk:
                    return True
            return False
        else:
            chk = filecmp.cmp(file, source)
            return chk

    @classmethod
    def get_list_of_filenames(cls, top='.', pattern='', excluded_duplicate=True):
        cls.clean()

        empty_list = []

        if not cls.is_exist(top):
            File.message = 'The provided path IS NOT existed.'
            return empty_list

        if cls.is_file(top):
            if pattern:
                result = [top] if re.search(pattern, top) else empty_list
            else:
                result = [top]
            return result

        try:
            lst = []
            for dir_path, _dir_names, file_names in os.walk(top):
                for file_name in file_names:
                    if pattern and not re.search(pattern, file_name):
                        continue
                    file_path = str(Path(dir_path, file_name))

                    if excluded_duplicate:
                        is_duplicated = cls.is_duplicate_file(file_path, lst)
                        not is_duplicated and lst.append(file_path)
                    else:
                        lst.append(file_path)
            return lst

        except Exception as ex:
            cls.message = Text(ex)
            return empty_list

    @classmethod
    @try_to_call
    def quicklook(cls, filename, lookup='', on_failure=False):

        cls.on_failure = on_failure

        if not cls.is_exist(filename):
            cls.message = Text.format('%r file is not existed.', filename)
            return False

        content = cls.get_content(filename)

        if not content.strip():
            if content.strip() == lookup.strip():
                return True
            else:
                return False

        if not lookup.strip():
            return True

        if cls.message:
            return False

        if lookup in content:
            return True
        else:
            match = re.search(lookup, content)
            return bool(match)

    @classmethod
    def get_new_filename(cls, filename, new_name='', prefix='',
                         postfix='', new_extension=''):
        if File.is_dir(filename):
            return filename

        file_obj = Path(filename)

        if new_name:
            file_obj = file_obj.with_name(new_name)
            new_filename = str(file_obj)
            return new_filename

        new_ext = new_extension.strip()
        if new_ext:
            new_ext = '.%s' % new_ext.lstrip('.')
            file_obj = file_obj.with_suffix(new_ext)

        prefix = prefix.strip()
        if prefix:
            fn = file_obj.name
            if not fn.startswith(prefix):
                fn = '%s%s' % (prefix, fn)
                file_obj = file_obj.with_name(fn)

        postfix = postfix.strip()
        if postfix:
            fn_wo_ext = file_obj.stem
            ext = file_obj.suffix
            if not fn_wo_ext.endswith(postfix):
                fn = '%s%s%s' % (fn_wo_ext, postfix, ext)
                file_obj = file_obj.with_name(fn)

        new_filename = str(file_obj)
        return new_filename

    @classmethod
    def get_extension(cls, filename):
        """
        Return the file extension
        Parameters:
          filename (str): file name
        Returns:
          str: the file extension.
        Robot Framework Usage:
        # import library snippet in settings section: Library   genericlib.RFFile
        ${result}=   rf generic lib file get extension   filename.txt
        """
        file_obj = Path(filename)
        extension = file_obj.suffix[1:]
        return extension

    rf_generic_lib_file_get_extension = get_extension

    @classmethod
    def build_open_file_kwargs_from(cls, kwargs):
        file_kwargs = dict(mode='r', buffering=-1,
                           encoding=None, errors=None,
                           newline=None, closefd=True,
                           opener=None)
        if isinstance(kwargs, dict):
            for key in file_kwargs:
                if key in kwargs:
                    file_kwargs[key] = kwargs.pop(key)
        return file_kwargs

    @classmethod
    def load_text(cls, filename, **kwargs):
        """
        Load text file and return content of file as text.
        Parameters:
          filename (str): file name
          kwargs (dict): full open document, check this link
            + https://docs.python.org/3/library/functions.html#open
        Returns:
          str: content of file.
        Robot Framework Usage:
        # import library snippet in settings section: Library   genericlib.RFFile
        ${result}=   rf generic lib file load text   filename.txt
        # or
        ${result}=   rf generic lib file load text   filename.txt   mode=r   encoding=utf-8   errors=strict
        """
        file_kwargs = cls.build_open_file_kwargs_from(kwargs)
        with open(filename, **file_kwargs) as stream:
            content = stream.read()
            if isinstance(content, str):
                return content
            else:
                encoding = file_kwargs.get('encoding') or 'utf-8'
                errors = file_kwargs.get('errors') or 'strict'
                content = content.decode(encoding=encoding, errors=errors)
                return content

    rf_generic_lib_file_load_text = load_text

    @classmethod
    def load_json(cls, filename, **kwargs):
        """
        Load JSON file and return JSON object.
        Parameters:
          filename (str): file name
          kwargs (dict): full open document, check these links
            + https://docs.python.org/3/library/json.html#module-json
            + https://docs.python.org/3/library/functions.html#open
        Returns:
          object: json object.
        Robot Framework Usage:
        # import library snippet in settings section: Library   genericlib.RFFile
        ${result}=   rf generic lib file load json   filename.json
        """
        file_kwargs = cls.build_open_file_kwargs_from(kwargs)
        json_content = cls.load_text(filename, **file_kwargs)
        json_obj = json.loads(json_content, **kwargs)
        return json_obj

    rf_generic_lib_file_load_json = load_json

    @classmethod
    def load_yaml(cls, filename, **kwargs):
        """
        Load YAML file and return YAML object.
        Parameters:
          filename (str): file name
          kwargs (dict): full open document, check this link
            + https://docs.python.org/3/library/functions.html#open
        Returns:
          object: yaml object.
        Robot Framework Usage:
        # import library snippet in settings section: Library   genericlib.RFFile
        ${result}=   rf generic lib file load yaml   filename.yaml
        """
        yaml_content = cls.load_text(filename, **kwargs)
        yaml_obj = yaml.safe_load(yaml_content)
        return yaml_obj

    rf_generic_lib_file_load_yaml = load_yaml

    @classmethod
    def load_csv(cls, filename, **kwargs):
        """
        Load CSV file and return list of dictionary.
        Parameters:
          filename (str): file name
          kwargs (dict): full open document,
            check these links
              + https://docs.python.org/3/library/csv.html#module-csv
              + https://docs.python.org/3/library/functions.html#open
        Returns:
          list: list of dictionary.
        Robot Framework Usage:
        # import library snippet in settings section: Library   genericlib.RFFile
        ${result}=   rf generic lib file load csv   filename.csv
        """
        lst = []
        file_kwargs = cls.build_open_file_kwargs_from(kwargs)
        csv_content = cls.load_text(filename, **file_kwargs)
        stream = csv.StringIO(csv_content)
        rows = csv.DictReader(stream, **kwargs)
        for row in rows:
            lst.append(row)
        return lst

    rf_generic_lib_file_load_csv = load_csv
