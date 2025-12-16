from .constants import TOKENS, KEYWORDS
from .nodes import PysDictionaryNode, PysSetNode, PysListNode, PysTupleNode

from operator import (
    is_not, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, floordiv, pow, matmul, mod, and_, or_, xor, lshift, rshift,
    iadd, isub, imul, itruediv, ifloordiv, ipow, imatmul, imod, iand, ior, ixor, ilshift, irshift, pos, neg, inv
)
from types import MappingProxyType

BINARY_FUNCTIONS_MAP = MappingProxyType({
    TOKENS['NOT-IN']: lambda a, b : a not in b,
    TOKENS['IS-NOT']: is_not,
    TOKENS['PLUS']: add,
    TOKENS['MINUS']: sub,
    TOKENS['STAR']: mul,
    TOKENS['SLASH']: truediv,
    TOKENS['DOUBLE-SLASH']: floordiv,
    TOKENS['DOUBLE-STAR']: pow,
    TOKENS['AT']: matmul,
    TOKENS['PERCENT']: mod,
    TOKENS['AMPERSAND']: and_,
    TOKENS['PIPE']: or_,
    TOKENS['CIRCUMFLEX']: xor,
    TOKENS['DOUBLE-LESS-THAN']: lshift,
    TOKENS['DOUBLE-GREATER-THAN']: rshift,
    TOKENS['DOUBLE-EQUAL']: eq,
    TOKENS['EQUAL-EXCLAMATION']: ne,
    TOKENS['LESS-THAN']: lt,
    TOKENS['GREATER-THAN']: gt,
    TOKENS['EQUAL-LESS-THAN']: le,
    TOKENS['EQUAL-GREATER-THAN']: ge,
    TOKENS['EQUAL-PLUS']: iadd,
    TOKENS['EQUAL-MINUS']: isub,
    TOKENS['EQUAL-STAR']: imul,
    TOKENS['EQUAL-SLASH']: itruediv,
    TOKENS['EQUAL-DOUBLE-SLASH']: ifloordiv,
    TOKENS['EQUAL-DOUBLE-STAR']: ipow,
    TOKENS['EQUAL-AT']: imatmul,
    TOKENS['EQUAL-PERCENT']: imod,
    TOKENS['EQUAL-AMPERSAND']: iand,
    TOKENS['EQUAL-PIPE']: ior,
    TOKENS['EQUAL-CIRCUMFLEX']: ixor,
    TOKENS['EQUAL-DOUBLE-LESS-THAN']: ilshift,
    TOKENS['EQUAL-DOUBLE-GREATER-THAN']: irshift,
})

UNARY_FUNCTIONS_MAP = MappingProxyType({
    TOKENS['PLUS']: pos,
    TOKENS['MINUS']: neg,
    TOKENS['TILDE']: inv
})

KEYWORDS_TO_VALUES_MAP = MappingProxyType({
    KEYWORDS['True']: True,
    KEYWORDS['False']: False,
    KEYWORDS['None']: None,
    KEYWORDS['true']: True,
    KEYWORDS['false']: False,
    KEYWORDS['none']: None
})

BRACKETS_MAP = MappingProxyType({
    TOKENS['LEFT-PARENTHESIS']: TOKENS['RIGHT-PARENTHESIS'],
    TOKENS['LEFT-SQUARE']: TOKENS['RIGHT-SQUARE'],
    TOKENS['LEFT-CURLY']: TOKENS['RIGHT-CURLY']
})

BRACKETS_ITERABLE_MAP = MappingProxyType({
    'dict': TOKENS['LEFT-CURLY'],
    'set': TOKENS['LEFT-CURLY'],
    'list': TOKENS['LEFT-SQUARE'],
    'tuple': TOKENS['LEFT-PARENTHESIS']
})

NODE_ITERABLE_MAP = MappingProxyType({
    'dict': PysDictionaryNode,
    'set': PysSetNode,
    'list': PysListNode,
    'tuple': PysTupleNode
})

ANSI_NAMES_MAP = MappingProxyType({
    'reset': 0,
    'black': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
    'gray': 90,
    'bright-black': 90,
    'bright-red': 91,
    'bright-green': 92,
    'bright-yellow': 93,
    'bright-blue': 94,
    'bright-magenta': 95,
    'bright-cyan': 96,
    'bright-white': 97
})

HIGHLIGHT_MAP = MappingProxyType({
    'default': '#D4D4D4',
    'keyword': '#C586C0',
    'keyword-constant': '#307CD6',
    'identifier': '#8CDCFE',
    'identifier-constant': '#2EA3FF',
    'identifier-function': '#DCDCAA',
    'identifier-type': '#4EC9B0',
    'number': '#B5CEA8',
    'string': '#CE9178',
    'brackets-0': '#FFD705',
    'brackets-1': '#D45DBA',
    'brackets-2': '#1A9FFF',
    'comment': '#549952',
    'invalid': '#B51819'
})

TAG_VERSION_MAP = MappingProxyType({
    'a': 'alpha',
    'b': 'beta',
    'rc': 'release candidate',
    'dev': 'development',
    'post': 'post'
})

EMPTY_MAP = MappingProxyType({})