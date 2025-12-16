from os.path import isdir, isfile, join
from sys import path as pypath

from .path import normpath, base, extension

def get_module_name_from_path(path):
    return base(normpath(path, absolute=False))

def get_module_path(path):
    from ..checks import is_python_extensions

    if isfile(path) and not is_python_extensions(extension(path)):
        return path

    candidate = path + '.pys'
    if isfile(candidate):
        return candidate

    candidate = join(path, '__init__.pys')
    if isdir(path) and isfile(candidate):
        return candidate

def set_python_path(path):
    if path not in pypath:
        pypath.insert(0, path)