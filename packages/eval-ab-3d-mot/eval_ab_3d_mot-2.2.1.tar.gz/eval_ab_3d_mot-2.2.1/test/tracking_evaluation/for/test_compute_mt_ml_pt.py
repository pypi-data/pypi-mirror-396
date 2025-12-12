"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_effectively_zero_tracked(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.n_gt_trajectories = 12
    te_3d.compute_mt_ml_pt(12)
    assert te_3d.MT == pytest.approx(0.0)
    assert te_3d.ML == pytest.approx(0.0)
    assert te_3d.PT == pytest.approx(0.0)


def test_some_tracked_tracked(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.n_gt_trajectories = 120
    te_3d.MT = 23
    te_3d.ML = 12
    te_3d.PT = 34
    te_3d.compute_mt_ml_pt(20)
    assert te_3d.MT == pytest.approx(0.23)
    assert te_3d.ML == pytest.approx(0.12)
    assert te_3d.PT == pytest.approx(0.34)
