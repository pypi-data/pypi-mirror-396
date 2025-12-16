from .bases import Pys
from .constants import DEFAULT
from .utils.decorators import immutable
from .utils.generic import setimuattr

@immutable
class PysContext(Pys):

    __slots__ = ('file', 'name', 'qualname', 'flags', 'symbol_table', 'parent', 'parent_entry_position')

    def __init__(
        self,
        file,
        name=None,
        qualname=None,
        flags=None,
        symbol_table=None,
        parent=None,
        parent_entry_position=None
    ):
        if flags is None and parent:
            flags = parent.flags

        setimuattr(self, 'file', file)
        setimuattr(self, 'name', name)
        setimuattr(self, 'qualname', qualname)
        setimuattr(self, 'flags', DEFAULT if flags is None else flags)
        setimuattr(self, 'symbol_table', symbol_table)
        setimuattr(self, 'parent', parent)
        setimuattr(self, 'parent_entry_position', parent_entry_position)

    def __repr__(self):
        return f'<Context {self.name!r}>'

class PysClassContext(PysContext):

    __slots__ = ()

    def __init__(
        self,
        name,
        symbol_table,
        parent,
        parent_entry_position
    ):
        qualname = parent.qualname
        super().__init__(
            file=parent.file,
            name=name,
            qualname=('' if qualname is None else qualname + '.') + name,
            symbol_table=symbol_table,
            parent=parent,
            parent_entry_position=parent_entry_position
        )