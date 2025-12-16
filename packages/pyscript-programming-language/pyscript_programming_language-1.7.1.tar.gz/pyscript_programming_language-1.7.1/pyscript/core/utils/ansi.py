from collections.abc import Iterable

DEFAULT = 0
BACKGROUND = 1 << 0
BOLD = 1 << 1
ITALIC = 1 << 2
UNDER = 1 << 3
STRIKET = 1 << 4

def acolor(arg, style=DEFAULT):
    from ..mapping import ANSI_NAMES_MAP

    styles = ''

    if style & BOLD:
        styles += '1'
    if style & ITALIC:
        styles += '3'
    if style & UNDER:
        styles += '4'
    if style & STRIKET:
        styles += '9'

    offset = 10 if style & BACKGROUND else 0
    style = f'\x1b[{";".join(styles)}m' if styles else ''

    if isinstance(arg, str):
        arg = arg.strip().replace(' ', '-').replace('_', '-').lower()
        if arg in ANSI_NAMES_MAP:
            return f'{style}\x1b[{ANSI_NAMES_MAP[arg] + offset}m'

    elif isinstance(arg, Iterable):
        arg = tuple(map(int, arg))
        if len(arg) == 3 and all(0 <= c <= 255 for c in arg):
            return f'{style}\x1b[{38 + offset};2;{";".join(map(str, arg))}m'

    raise TypeError("acolor(): arg is invalid for ansi color")