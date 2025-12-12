"""."""

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_reset(te: TrackingEvaluation) -> None:
    te.tp = 123
    te.reset()
    assert te.tp == 0
