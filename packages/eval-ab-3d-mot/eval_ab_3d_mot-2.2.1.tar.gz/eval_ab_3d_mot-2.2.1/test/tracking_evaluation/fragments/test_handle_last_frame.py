"""."""

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_no_bump_fragments(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.fragments = 0
    te_3d.handle_last_frame([], 1, [], 2)
    assert te_3d.fragments == 0


def test_bump_fragments(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.fragments = 0
    te_3d.handle_last_frame([1, 2], 1, [True, False], 2)
    assert te_3d.fragments == 1

    te_3d.handle_last_frame([1, 2], 1, [False, False], 2)
    assert te_3d.fragments == 2

    te_3d.handle_last_frame([1, 2], 1, [False, True], 2)
    assert te_3d.fragments == 2

    te_3d.handle_last_frame([1, 2], 1, [False, False], -1)
    assert te_3d.fragments == 2
