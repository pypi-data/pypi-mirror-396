from .bases import Pys
from .constants import TOKENS
from .position import PysPosition
from .utils.decorators import typechecked, immutable
from .utils.generic import setimuattr

from typing import Any, Optional

@immutable
class PysToken(Pys):

    __slots__ = ('type', 'position', 'value')

    @typechecked
    def __init__(self, type: int, position: PysPosition, value: Optional[Any] = None) -> None:
        setimuattr(self, 'type', type)
        setimuattr(self, 'position', position)
        setimuattr(self, 'value', value)

    def __repr__(self):
        name = '<UNKNOWN>'
        type = self.type
        value = self.value

        for token_name, token_type in TOKENS.items():
            if token_type == type:
                name = token_name
                break

        return 'Token({}{})'.format(
            name,
            '' if value is None else f', value={value!r}'
        )

    def match(self, type, value):
        return self.type == type and self.value == value

    def matches(self, type, values):
        return self.type == type and self.value in values