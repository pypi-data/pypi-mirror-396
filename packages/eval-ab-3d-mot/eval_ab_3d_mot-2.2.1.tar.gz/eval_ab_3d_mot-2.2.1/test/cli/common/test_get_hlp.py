"""."""

from eval_ab_3d_mot.cli.common.get_hlp import get_hlp


def test_get_hlp() -> None:
    assert get_hlp('help message', 'def value') == 'help message {def value}'
