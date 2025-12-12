import bisect


class SortedKeyDict:
    def __init__(self):
        self._dict = {}
        self._keys = []  # 升序排列

    def __setitem__(self, key, value):
        if key not in self._dict:
            bisect.insort_right(self._keys, key)
        self._dict[key] = value

    def __getitem__(self, key):
        return self._dict[key]

    def __delitem__(self, key):
        del self._dict[key]
        idx = bisect.bisect_left(self._keys, key)
        del self._keys[idx]

    def __iter__(self):
        # 遍历时降序
        for key in reversed(self._keys):
            yield key, self._dict[key]

    def items(self):
        for key in self:
            yield key, self._dict[key]

    def __len__(self):
        return len(self._keys)

    def get(self, key, default=None):
        return self._dict.get(key, default)
