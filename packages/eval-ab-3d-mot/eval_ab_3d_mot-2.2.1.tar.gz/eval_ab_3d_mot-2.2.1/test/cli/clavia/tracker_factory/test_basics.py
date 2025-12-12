"""."""

from pure_ab_3d_mot.dist_metrics import MetricKind
from pure_ab_3d_mot.matching import MatchingAlgorithm
from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.tracker_factory import get_tracker
from eval_ab_3d_mot.cli.common.tracker_meta import TrackerMeta
from eval_ab_3d_mot.kitti_category import KittiCategory


def test_get_tracker(category: KittiCategory, meta: TrackerMeta) -> None:
    tracker = get_tracker(category, meta)
    assert isinstance(tracker, Ab3DMot)
    assert tracker.algorithm == MatchingAlgorithm.HUNGARIAN
    assert tracker.metric == MetricKind.GIOU_3D
