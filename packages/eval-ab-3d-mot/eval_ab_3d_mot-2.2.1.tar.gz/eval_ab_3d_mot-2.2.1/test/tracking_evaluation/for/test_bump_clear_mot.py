"""."""

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_bump_clear_mot(te_3d: TrackingEvaluation) -> None:
    assert te_3d.bump_clear_mot(0) == 0
