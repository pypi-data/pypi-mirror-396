"""."""

from eval_ab_3d_mot.track_data import TrackData


def test_bump_id_switch(td: TrackData) -> None:
    """."""
    td.id_switch = 0
    td.bump_id_switch(0, 0, 3)
    assert td.id_switch == 0

    td.bump_id_switch(1, 0, 3)
    assert td.id_switch == 1

    td.bump_id_switch(1, 0, -2)
    assert td.id_switch == 1

    td.bump_id_switch(1, -1, 3)
    assert td.id_switch == 1

    td.bump_id_switch(1, 0, 3)
    assert td.id_switch == 1
