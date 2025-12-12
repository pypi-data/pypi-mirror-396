"""."""

from eval_ab_3d_mot.core.print_entry import print_entry


def test_print_entry() -> None:
    """."""
    assert print_entry('a', 2, (10, 5)) == 'a             2'
    assert print_entry('a', 3.0, (10, 5)) == 'a         3.0000'
    assert print_entry('a', '4', (10, 5)) == 'a             4'
