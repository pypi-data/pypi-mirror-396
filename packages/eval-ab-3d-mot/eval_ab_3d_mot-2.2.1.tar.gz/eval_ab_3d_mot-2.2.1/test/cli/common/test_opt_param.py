"""."""

import pytest

from pure_ab_3d_mot.dist_metrics import MetricKind
from pure_ab_3d_mot.matching import MatchingAlgorithm
from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.ab_3d_mot_parameters import fill_r_cnn_opt_param
from eval_ab_3d_mot.kitti_category import KittiCategory


def test_opt_param(tracker: Ab3DMot) -> None:
    """."""
    fill_r_cnn_opt_param(KittiCategory.PEDESTRIAN, tracker)
    assert tracker.algorithm == MatchingAlgorithm.GREEDY
    assert tracker.min_hits == 1
    assert tracker.max_age == 4
    assert tracker.threshold == pytest.approx(-0.4)
    assert tracker.metric == MetricKind.GIOU_3D

    fill_r_cnn_opt_param(KittiCategory.CAR, tracker)
    assert tracker.algorithm == MatchingAlgorithm.HUNGARIAN
    assert tracker.min_hits == 3
    assert tracker.max_age == 2
    assert tracker.threshold == pytest.approx(-0.2)
    assert tracker.metric == MetricKind.GIOU_3D

    fill_r_cnn_opt_param(KittiCategory.CYCLIST, tracker)
    assert tracker.algorithm == MatchingAlgorithm.HUNGARIAN
    assert tracker.min_hits == 3
    assert tracker.max_age == 4
    assert tracker.threshold == -2
    assert tracker.threshold == pytest.approx(-2.0)
    assert tracker.metric == MetricKind.DIST_3D
