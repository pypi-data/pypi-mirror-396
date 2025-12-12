"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_no_tp(te_3d: TrackingEvaluation) -> None:
    te_3d.tp = 0
    te_3d.compute_motp()
    assert te_3d.MOTP == pytest.approx(0.0)


def test_some_tp(te_3d: TrackingEvaluation) -> None:
    te_3d.tp = 123
    te_3d.total_cost = 65
    te_3d.compute_motp()
    assert te_3d.MOTP == pytest.approx(0.5284552845528455)
