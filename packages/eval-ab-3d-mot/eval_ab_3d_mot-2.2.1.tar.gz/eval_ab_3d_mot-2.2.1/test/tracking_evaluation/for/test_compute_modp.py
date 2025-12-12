"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_compute_modp(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.MODP_t = [0.5, 0.6]
    te_3d.n_frames = [10, 20]
    te_3d.compute_modp()
    assert te_3d.MODP == pytest.approx(0.0366666666666666666)


def test_compute_modp_zero_frames(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.MODP_t = [0.5]
    te_3d.n_frames = [0]
    te_3d.compute_modp()
    assert te_3d.MODP == 'n/a'
