from collections.abc import MutableMapping
from functools import reduce


def deepmerge(*dicts) -> dict:
    """TODO: 需要解释为什么需要这个方法"""

    def _deepmerge(source: dict, destination: dict) -> dict:
        """Updates two dicts of dicts recursively (https://stackoverflow.com/a/24088493/8965861)."""
        for k, v in source.items():
            if k in destination:
                # this next check is the only difference!
                if all(isinstance(e, MutableMapping) for e in (v, destination[k])):
                    destination[k] = deepmerge(v, destination[k])
                # we could further check types and merge as appropriate here.
        d3 = source.copy()
        d3.update(destination)
        return d3

    return reduce(_deepmerge, tuple(dicts))


def merge_dict_from_dict(base_dict: dict, new_dict: dict):
    """合并两个字典"""
    if new_dict:
        tmp_dict = {}
        for k, v in new_dict.items():
            tmp_dict[k] = v
        _d = deepmerge(base_dict, tmp_dict)
        base_dict.update(_d)
    return base_dict
