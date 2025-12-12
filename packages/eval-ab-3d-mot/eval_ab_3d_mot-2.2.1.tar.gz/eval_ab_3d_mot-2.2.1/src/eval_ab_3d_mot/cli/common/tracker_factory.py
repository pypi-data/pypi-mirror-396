"""."""

from pure_ab_3d_mot.dist_metrics import MetricKind
from pure_ab_3d_mot.matching import MatchingAlgorithm
from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.clavia.cmd_line_factory import AUTO
from eval_ab_3d_mot.cli.common.ab_3d_mot_parameters import fill_r_cnn_opt_param
from eval_ab_3d_mot.cli.common.kitti_category import KittiCategory
from eval_ab_3d_mot.cli.common.tracker_meta import TrackerMeta


def get_tracker(category: KittiCategory, meta: TrackerMeta) -> Ab3DMot:
    tracker = Ab3DMot()
    fill_r_cnn_opt_param(category, tracker)
    if meta.threshold < 999.0:
        tracker.threshold = meta.threshold
    if meta.max_age > 0:
        tracker.max_age = meta.max_age
    if meta.algorithm != AUTO:
        tracker.algorithm = MatchingAlgorithm(meta.algorithm)
    if meta.metric != AUTO:
        tracker.metric = MetricKind(meta.metric)

    return tracker
