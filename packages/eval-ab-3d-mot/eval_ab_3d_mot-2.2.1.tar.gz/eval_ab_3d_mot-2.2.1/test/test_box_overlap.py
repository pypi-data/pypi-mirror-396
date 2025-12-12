"""."""

import pytest

from eval_ab_3d_mot.box_overlap import box_overlap
from eval_ab_3d_mot.track_data import TrackData


@pytest.fixture
def a() -> TrackData:
    return TrackData(x1=20, y1=30, x2=40, y2=50)


def test_box_overlap_union(a: TrackData) -> None:
    assert box_overlap(a, a) == pytest.approx(1.0)
    assert box_overlap(a, TrackData(x1=20, y1=30, x2=80, y2=90)) == pytest.approx(0.1111111111111)


def test_box_overlap_a(a: TrackData) -> None:
    assert box_overlap(a, a, criterion='a') == pytest.approx(1.0)
    assert box_overlap(a, TrackData(x1=20, y1=30, x2=80, y2=90), criterion='a') == pytest.approx(
        1.0
    )


def test_unknown_criterion(a: TrackData) -> None:
    with pytest.raises(TypeError):
        box_overlap(a, a, criterion='bogus')


def test_no_overlap_condition() -> None:
    a = TrackData(x1=20, y1=30, x2=20, y2=50)
    assert box_overlap(a, a) == pytest.approx(0.0)
    a = TrackData(x1=20, y1=30, x2=40, y2=30)
    assert box_overlap(a, a) == pytest.approx(0.0)
    assert box_overlap(a, TrackData(x1=60, y1=70, x2=80, y2=90)) == pytest.approx(0.0)
