"""."""

from argparse import Namespace

from eval_ab_3d_mot.cli.common.init_coinciding_attrs import init_coinciding_attrs


class MyClass:
    def __init__(self) -> None:
        self.second_arg = 77


def test_init_coinciding_attrs() -> None:
    ns = Namespace(first_arg=1, second_arg=2)
    obj = MyClass()
    init_coinciding_attrs(ns, obj)
    assert obj.second_arg == 2
