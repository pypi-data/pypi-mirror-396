"""."""

from pure_ab_3d_mot.dist_metrics import MetricKind
from pure_ab_3d_mot.matching import MatchingAlgorithm
from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.ab_3d_mot_parameters import report_tracker_parameters


def test_report_tracker_parameters() -> None:
    tracker = Ab3DMot()
    tracker.metric = MetricKind.MAHALANOBIS_DIST
    tracker.algorithm = MatchingAlgorithm.GREEDY
    tracker.threshold = -0.234
    tracker.min_hits = 4
    tracker.max_age = 5
    report = report_tracker_parameters(tracker)
    ref = """Ab3DMot (AB3DMOT) parameters
    algorithm MatchingAlgorithm.GREEDY
       metric MetricKind.MAHALANOBIS_DIST
    threshold -0.234
     min_hits 4
      max_age 5"""
    assert report == ref
