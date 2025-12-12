"""."""

from pathlib import Path

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


@pytest.fixture
def te_fail_associate(files_dir: Path) -> TrackingEvaluation:
    te = TrackingEvaluation('my-sha', {'fail-associate': 1})
    te.t_path = str(files_dir / 'kitti/tracking/training')
    assert te.load_data(False)

    te.gt_path = str(files_dir / 'kitti/annotations/training')
    assert te.load_data(True)
    return te


def test_fail_to_associate(te_fail_associate: TrackingEvaluation) -> None:
    """."""
    assert te_fail_associate.compute_3rd_party_metrics()
    assert te_fail_associate.fn == 1
    assert te_fail_associate.tp == 1
    assert te_fail_associate.MOTP == pytest.approx(1.0)
    assert te_fail_associate.F1 == pytest.approx(0.5)
    assert te_fail_associate.recall == pytest.approx(0.5)
    assert te_fail_associate.precision == pytest.approx(0.5)
