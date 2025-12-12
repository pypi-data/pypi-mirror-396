"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_0_0_12(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.tp = 0
    te_3d.fp = 0
    te_3d.fn = 12
    te_3d.compute_f1()
    assert te_3d.F1 == pytest.approx(0.0)
    assert te_3d.recall == pytest.approx(0.0)
    assert te_3d.precision == pytest.approx(0.0)


def test_0_12_0(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.tp = 0
    te_3d.fp = 12
    te_3d.fn = 0
    te_3d.compute_f1()
    assert te_3d.F1 == pytest.approx(0.0)
    assert te_3d.recall == pytest.approx(0.0)
    assert te_3d.precision == pytest.approx(0.0)


def test_12_3_4(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.tp = 12
    te_3d.fp = 3
    te_3d.fn = 4
    te_3d.compute_f1()
    assert te_3d.F1 == pytest.approx(0.7741935483870969)
    assert te_3d.recall == pytest.approx(0.75)
    assert te_3d.precision == pytest.approx(0.8)
