"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_empty(te: TrackingEvaluation) -> None:
    assert te.compute_3rd_party_metrics()


def test_no_2d_no_3d(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.eval_3diou = False
    te_3d.eval_2diou = False
    with pytest.raises(AssertionError):
        te_3d.compute_3rd_party_metrics()


def test_3d_with_ideal_gt(te_3d: TrackingEvaluation) -> None:
    """."""
    assert te_3d.compute_3rd_party_metrics()
    assert te_3d.F1 == pytest.approx(1.0)
    assert te_3d.MODA == pytest.approx(1.0)
    assert te_3d.MOTA == pytest.approx(1.0)
    assert te_3d.MOTP == pytest.approx(1.0)
    assert te_3d.fn == 0


def test_2d_with_ideal_gt(te_2d: TrackingEvaluation) -> None:
    """."""
    assert te_2d.compute_3rd_party_metrics()
    assert te_2d.F1 == pytest.approx(1.0)
    assert te_2d.MODA == pytest.approx(1.0)
    assert te_2d.MOTA == pytest.approx(1.0)
    assert te_2d.MOTP == pytest.approx(1.0)
    assert te_2d.fn == 0
