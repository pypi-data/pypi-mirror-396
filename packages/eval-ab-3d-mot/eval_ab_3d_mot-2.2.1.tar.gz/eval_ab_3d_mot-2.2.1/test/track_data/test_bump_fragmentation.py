"""."""

from eval_ab_3d_mot.track_data import TrackData


def test_bump_fragmentation(td: TrackData) -> None:
    """."""
    td.fragmentation = 0
    td.bump_fragmentation(0, 0, 3)
    assert td.fragmentation == 0

    td.bump_fragmentation(1, 0, 3)
    assert td.fragmentation == 1

    td.bump_fragmentation(1, 0, -2)
    assert td.fragmentation == 1

    td.bump_fragmentation(1, -1, 3)
    assert td.fragmentation == 1

    td.bump_fragmentation(1, 0, 3)
    assert td.fragmentation == 1
