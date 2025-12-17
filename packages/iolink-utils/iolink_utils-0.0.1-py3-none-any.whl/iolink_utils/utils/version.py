import re
from functools import total_ordering


@total_ordering
class Version:
    VERSION_PATTERN = re.compile(r"^V?(\d+(?:\.\d+){0,4})$")

    def __init__(self, version_str: str = '0.0.0.0'):
        match = self.VERSION_PATTERN.match(version_str)
        if not match:
            raise ValueError(f"Invalid version string: {version_str}")
        self.parts = [int(p) for p in match.group(1).split(".")]

    def _padded_parts(self, length):
        return self.parts + [0] * (length - len(self.parts))

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        max_len = max(len(self.parts), len(other.parts))
        return self._padded_parts(max_len) == other._padded_parts(max_len)

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        max_len = max(len(self.parts), len(other.parts))
        return self._padded_parts(max_len) < other._padded_parts(max_len)

    def __repr__(self):  # pragma: no cover
        return f"Version({'V' + '.'.join(map(str, self.parts))})"
