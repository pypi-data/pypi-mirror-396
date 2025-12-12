"""."""

import pytest

from eval_ab_3d_mot.track_data import TrackData


@pytest.fixture
def td() -> TrackData:
    return TrackData(track_id=123, frame=456, x=1, y=2, z=3)
