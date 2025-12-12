"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_no_frames(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.n_frames = [0, 0]
    te_3d.compute_far()
    assert te_3d.FAR == 'n/a'


def test_some_frames(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.fp = 15
    te_3d.n_frames = [12, 34]
    te_3d.compute_far()
    assert te_3d.FAR == pytest.approx(0.326086957)
