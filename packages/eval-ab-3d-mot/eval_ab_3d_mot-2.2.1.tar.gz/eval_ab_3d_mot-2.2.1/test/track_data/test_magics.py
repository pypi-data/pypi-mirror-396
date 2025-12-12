"""."""

from eval_ab_3d_mot.track_data import TrackData


def test_track_data(td: TrackData) -> None:
    """."""
    ref = """x: 1
y: 2
z: 3
h: -1
w: -1
l: -1
ry: -10
s: -1000
ann_id: -1000
frame: 456
track_id: 123
obj_type: unset
truncation: -1
occlusion: -1
obs_angle: -10
x1: -1
y1: -1
x2: -1
y2: -1
ignored: False
valid: False
tracker: -1
distance: 0.0
fragmentation: 0
id_switch: 0
score: -1000"""
    assert str(td) == ref


def test_track_data_repr(td: TrackData) -> None:
    td.score = 0.567
    assert td.__repr__() == 'Track(id 123 frame 456 score 0.567 x 1 y 2 z 3)'
