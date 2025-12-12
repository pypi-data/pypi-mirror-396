"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


@pytest.fixture
def te_tal(te_3d: TrackingEvaluation) -> TrackingEvaluation:
    te_3d.n_gt = 234
    te_3d.fn = 34
    te_3d.fp = 45
    te_3d.id_switches = 123
    return te_3d


def test_no_gt(te_tal: TrackingEvaluation) -> None:
    """."""
    te_tal.n_gt = 0
    te_tal.compute_motal()
    assert te_tal.MOTAL == -float('inf')


def test_zero_no_id_switch(te_tal: TrackingEvaluation) -> None:
    """."""
    te_tal.id_switches = 0
    te_tal.compute_motal()
    assert te_tal.MOTAL == pytest.approx(0.6623931623931624)


def test_some_id_switch(te_tal: TrackingEvaluation) -> None:
    """."""
    te_tal.compute_motal()
    assert te_tal.MOTAL == pytest.approx(0.6534619439682077)
