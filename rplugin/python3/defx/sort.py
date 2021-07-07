# ============================================================================
# FILE: sort.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import functools
import re
import typing

from defx.util import readable


@functools.total_ordering
class _Reversed:
    def __init__(self, obj: typing.Any) -> None:
        self._obj = obj

    def __lt__(self, other: '_Reversed') -> typing.Any:
        return self._obj > other._obj

    def __eq__(self, other: object) -> typing.Any:
        if not isinstance(other, _Reversed):
            return NotImplemented
        return self._obj == other._obj


def sort(
        method: str, candidates: typing.List[typing.Dict[str, typing.Any]]
) -> typing.List[typing.Dict[str, typing.Any]]:
    key_func = _make_key_func(method)
    dirs = sorted(
        [x for x in candidates if x['is_directory']], key=key_func)
    files = sorted(
        [x for x in candidates if not x['is_directory']], key=key_func)
    return dirs + files


def _make_key_func(
        methods: str
) -> typing.Callable[[typing.Any], typing.List[typing.Any]]:
    key_func: typing.List[typing.Callable[[typing.Any], typing.Any]] = []
    for method in methods.split(':'):
        key = method.lower()
        if key not in SORT_KEY_METHODS:
            continue

        key_method = SORT_KEY_METHODS[key]
        if re.match(r'[A-Z]', method):
            key_func.append(_make_reversed_key(key_method))
        else:
            key_func.append(key_method)
    return lambda x: [f(x) for f in key_func]


def _make_reversed_key(
        key_method: typing.Callable[[typing.Dict[str, typing.Any]], typing.Any]
) -> typing.Callable[[typing.Dict[str, typing.Any]], typing.Any]:
    return lambda x: _Reversed(key_method(x))


def _extension(
        candidate: typing.Dict[str, typing.Any]
) -> typing.Any:
    return str(candidate['action__path'].suffix)


def _filename(
        candidate: typing.Dict[str, typing.Any]
) -> typing.Any:

    def numeric_key(v: str) -> typing.List[typing.Any]:
        keys = re.split(r'(\d+)', v)
        keys[1::2] = [int(x) for x in keys[1::2]]
        return keys

    return numeric_key(candidate['word'].lower())


def _size(
        candidate: typing.Dict[str, typing.Any]
) -> typing.Any:
    return (int(candidate['action__path'].stat().st_size)
            if readable(candidate['action__path']) else -1)


def _time(
        candidate: typing.Dict[str, typing.Any]
) -> typing.Any:
    return (int(candidate['action__path'].stat().st_mtime)
            if readable(candidate['action__path']) else 0)


SORT_KEY_METHODS = {
    'extension': _extension,
    'filename': _filename,
    'size': _size,
    'time': _time,
}
