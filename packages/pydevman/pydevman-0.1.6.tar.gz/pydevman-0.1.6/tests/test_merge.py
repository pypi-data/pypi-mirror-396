from copy import deepcopy

from pydevman.helper.merge import deepmerge


def test_deepmerge_v2():
    # given:
    d1 = {"x": 1, "y": {"a": 1, "b": 2}}
    d2 = {"y": {"b": 99}}
    d3 = deepcopy(d1)
    d4 = deepcopy(d2)

    # when:
    r1 = deepmerge(d1, d2)
    d3.update(d4)

    # then:
    assert r1 != d3
