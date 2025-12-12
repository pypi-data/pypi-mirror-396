"""."""

import pytest

from eval_ab_3d_mot.cli.common.tracker_meta import TrackerMeta
from eval_ab_3d_mot.kitti_category import KittiCategory


@pytest.fixture
def category() -> KittiCategory:
    return KittiCategory.CAR


@pytest.fixture
def meta() -> TrackerMeta:
    return TrackerMeta()
