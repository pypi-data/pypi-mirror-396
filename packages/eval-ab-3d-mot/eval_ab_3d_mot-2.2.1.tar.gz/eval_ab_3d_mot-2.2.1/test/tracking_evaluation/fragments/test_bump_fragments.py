"""."""

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_no_bump_fragments(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.fragments = 0
    te_3d.bump_fragments([], 0, 1)
    assert te_3d.fragments == 0


def test_bump_fragments(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.fragments = 0
    te_3d.bump_fragments([1, 2], 0, 1)
    assert te_3d.fragments == 1

    te_3d.bump_fragments([1, 2], 0, -1)
    assert te_3d.fragments == 1
