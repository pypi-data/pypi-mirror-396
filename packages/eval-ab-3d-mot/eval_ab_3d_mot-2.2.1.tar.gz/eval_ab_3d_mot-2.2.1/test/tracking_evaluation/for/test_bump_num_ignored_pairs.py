"""."""

from eval_ab_3d_mot.core.bump_num_ignored_pairs import bump_num_ignored_pairs


def test_bump_num_ignored_pairs() -> None:
    assert bump_num_ignored_pairs(0, 2) == 2
    assert bump_num_ignored_pairs(1, 3) == 4
