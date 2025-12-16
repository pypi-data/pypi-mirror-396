"""
PyScript is a programming language written in Python. \
This language is not isolated and is directly integrated with the Python's library and namespace levels.
"""

if __import__('sys').version_info < (3, 10):
    raise ImportError("Python version 3.10 and above is required to run PyScript")

from . import core

from .core.constants import DEFAULT, DEBUG, SILENT, RETRES, HIGHLIGHT, NO_COLOR, REVERSE_POW_XOR
from .core.cache import undefined
from .core.highlight import HLFMT_HTML, HLFMT_ANSI, HLFMT_BBCODE, pys_highlight, PygmentsPyScriptLexer
from .core.runner import pys_exec, pys_eval, pys_require, pys_shell
from .core.version import version_info, __version__, __date__

__all__ = (
    'core',
    'DEFAULT',
    'DEBUG',
    'SILENT',
    'RETRES',
    'HIGHLIGHT',
    'NO_COLOR',
    'REVERSE_POW_XOR',
    'HLFMT_HTML',
    'HLFMT_ANSI',
    'HLFMT_BBCODE',
    'undefined',
    'version_info',
    'pys_highlight',
    'pys_exec',
    'pys_eval',
    'pys_require',
    'pys_shell',
    'PygmentsPyScriptLexer'
)