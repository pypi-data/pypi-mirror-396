"""."""

from argparse import Namespace
from typing import Any


def init_coinciding_attrs(ns: Namespace, obj: Any) -> None:
    """."""
    vars_obj = vars(obj)
    vars_ns = vars(ns)
    update_dict = {}
    for key in vars_obj:
        val = vars_ns.get(key, None)
        if val is not None:
            update_dict[key] = val

    vars_obj.update(update_dict)
