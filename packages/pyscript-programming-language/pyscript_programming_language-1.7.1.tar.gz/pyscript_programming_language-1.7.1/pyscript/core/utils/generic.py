from collections.abc import Sequence
from inspect import currentframe
from re import compile as re_compile
from sys import platform
from os import environ

from ..constants import ENV_PYSCRIPT_NO_READLINE

delimuattr = object.__delattr__
setimuattr = object.__setattr__
version_match = re_compile(r'^(\d+)\.(\d+)\.(\d+)((?:a|b|rc)(\d+)|\.(dev|post)(\d+))?$').match

def get_frame(deep=0):
    deep += 1
    frame = currentframe()

    while deep > 0 and frame:
        frame = frame.f_back
        deep -= 1

    return frame

def get_locals(deep=0):
    if frame := get_frame(deep + 1):
        locals = frame.f_locals
        return locals if isinstance(locals, dict) else dict(locals)
    return {}

def get_any(object, key, default=None):
    if isinstance(object, dict):
        return object.get(key, default)
    elif isinstance(object, Sequence):
        return object[key] if 0 <= key < len(object) else default
    raise TypeError("unknown object")

def is_object_of(obj, class_or_tuple):
    return (
        isinstance(obj, class_or_tuple) or
        (isinstance(obj, type) and issubclass(obj, class_or_tuple))
    )

_READLINE = environ.get(ENV_PYSCRIPT_NO_READLINE) is None

def import_readline():
    if platform != 'win32' and _READLINE:
        try:
            import readline
        except:
            return False
    return True

def get_error_args(exception):
    if exception is None:
        return None, None, None

    pyexception = exception.exception
    return (
        (pyexception, None, exception)
        if isinstance(pyexception, type) else
        (type(pyexception), pyexception, exception)
    )