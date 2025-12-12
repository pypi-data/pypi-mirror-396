"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_no_gt(te_3d: TrackingEvaluation) -> None:
    te_3d.n_gt = 0
    te_3d.compute_clear_mot(-1.0)
    assert te_3d.MOTA == -float('inf')
    assert te_3d.MODA == -float('inf')
    assert te_3d.sMOTA == -float('inf')


def test_some_gt(te_3d: TrackingEvaluation) -> None:
    te_3d.n_gt = 345
    te_3d.fp = 12
    te_3d.fn = 23
    te_3d.id_switches = 5
    te_3d.compute_clear_mot(1.0)
    assert te_3d.MOTA == pytest.approx(0.8840579710144928)
    assert te_3d.sMOTA == pytest.approx(0.8840579710144928)
    assert te_3d.MODA == pytest.approx(0.8985507246376812)


def test_bounds_0(te_3d: TrackingEvaluation) -> None:
    te_3d.n_gt = 345
    te_3d.fp = 500
    te_3d.fn = 0
    te_3d.id_switches = 0
    te_3d.compute_clear_mot(1.0)
    assert te_3d.sMOTA == pytest.approx(0.0)


def test_bounds_1(te_3d: TrackingEvaluation) -> None:
    te_3d.n_gt = 345
    te_3d.fp = 12
    te_3d.fn = 23
    te_3d.id_switches = 0
    te_3d.compute_clear_mot(0.15)
    assert te_3d.sMOTA == pytest.approx(1.0)
