from .bases import Pys
from .mapping import TAG_VERSION_MAP
from .utils.decorators import immutable, inheritable, singleton
from .utils.generic import version_match

__version__ = '1.7.1'
__date__ = '13 December 2025, 15:45 UTC+7'

version = f'{__version__} ({__date__})'

@singleton
@immutable
@inheritable
class PysVersionInfo(Pys, tuple):

    __slots__ = ()

    def __new_singleton__(cls):
        match = version_match(__version__)
        if not match:
            raise ValueError(f"invalid format version {__version__!r}")

        major, minor, micro, pre_full, pre_num1, pre_tag2, pre_num2 = match.groups()

        if pre_full:

            if pre_tag2:
                pre_num = int(pre_num2)
                pre_tag_full = TAG_VERSION_MAP[pre_tag2]

            else:
                pre_num = int(pre_num1)
                pre_tag_full = (
                    TAG_VERSION_MAP[pre_full[0]]
                    if pre_full.startswith(('a', 'b')) else
                    TAG_VERSION_MAP['rc']
                )

        else:
            pre_tag_full = pre_num = None

        global version_info
        version_info = tuple.__new__(cls, (int(major), int(minor), int(micro), pre_tag_full, pre_num))
        return version_info

    @property
    def major(self):
        return self[0]

    @property
    def minor(self):
        return self[1]

    @property
    def micro(self):
        return self[2]

    @property
    def pre_tag(self):
        return self[3]

    @property
    def pre_num(self):
        return self[4]

    @property
    def release(self):
        return self[0:3]

    def __lt__(self, other):
        return self.release < other

    def __gt__(self, other):
        return self.release > other

    def __le__(self, other):
        return self.release <= other

    def __ge__(self, other):
        return self.release >= other

    def __eq__(self, value):
        return self.release == value

    def __ne__(self, value):
        return self.release != value

    def __repr__(self):
        return (
            f'VersionInfo(major={self.major!r}, minor={self.minor!r}, micro={self.micro!r}' +
            ('' if self.pre_tag is None else f', pre_tag={self.pre_tag!r}, pre_num={self.pre_num!r}') +
            ')'
        )

PysVersionInfo()