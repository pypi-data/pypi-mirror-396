"""."""

from pathlib import Path

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


@pytest.fixture
def te_ignored_trackers(files_dir: Path) -> TrackingEvaluation:
    te = TrackingEvaluation('my-sha', {'ignored-trackers': 1})
    te.t_path = str(files_dir / 'kitti/tracking/training')
    assert te.load_data(False), 'some file does not exist?'

    te.gt_path = str(files_dir / 'kitti/annotations/training')
    assert te.load_data(True), 'some file does not exist?'
    return te


def test_ignored_trackers(te_ignored_trackers: TrackingEvaluation) -> None:
    """."""
    assert te_ignored_trackers.compute_3rd_party_metrics()
    assert te_ignored_trackers.fn == 0
    assert te_ignored_trackers.tp == 1
    assert te_ignored_trackers.MOTP == pytest.approx(1.0)
    assert te_ignored_trackers.F1 == pytest.approx(0.666666666666666666666)
    assert te_ignored_trackers.recall == pytest.approx(1.0)
    assert te_ignored_trackers.precision == pytest.approx(0.5)
