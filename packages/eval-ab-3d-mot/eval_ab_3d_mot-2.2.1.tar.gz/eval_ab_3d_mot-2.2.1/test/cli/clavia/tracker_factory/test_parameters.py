"""."""

import pytest

from pure_ab_3d_mot.dist_metrics import MetricKind
from pure_ab_3d_mot.matching import MatchingAlgorithm

from eval_ab_3d_mot.cli.common.tracker_factory import get_tracker
from eval_ab_3d_mot.cli.common.tracker_meta import TrackerMeta
from eval_ab_3d_mot.kitti_category import KittiCategory


def test_overwrite_algorithm(category: KittiCategory, meta: TrackerMeta) -> None:
    meta.algorithm = 'greedy'
    tracker = get_tracker(category, meta)
    assert tracker.algorithm == MatchingAlgorithm.GREEDY


def test_overwrite_metric(category: KittiCategory, meta: TrackerMeta) -> None:
    meta.metric = 'm_dis'
    tracker = get_tracker(category, meta)
    assert tracker.metric == MetricKind.MAHALANOBIS_DIST


def test_overwrite_max_age(category: KittiCategory, meta: TrackerMeta) -> None:
    meta.max_age = 123
    tracker = get_tracker(category, meta)
    assert tracker.max_age == 123


def test_overwrite_threshold(category: KittiCategory, meta: TrackerMeta) -> None:
    meta.threshold = -1.234
    tracker = get_tracker(category, meta)
    assert tracker.threshold == pytest.approx(-1.234)
