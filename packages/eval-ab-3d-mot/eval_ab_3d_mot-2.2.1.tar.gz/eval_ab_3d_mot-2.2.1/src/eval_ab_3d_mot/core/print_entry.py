"""."""

from typing import Union


def print_entry(key: str, val: Union[int, float, str], width=(70, 10)) -> str:
    """
    Pretty print an entry in a table fashion.
    """

    s_out = key.ljust(width[0])
    if isinstance(val, int):
        s = '%%%dd' % width[1]
        s_out += s % val
    elif isinstance(val, float):
        s = '%%%d.4f' % (width[1])
        s_out += s % val
    else:
        s_out += ('%s' % val).rjust(width[1])
    return s_out
