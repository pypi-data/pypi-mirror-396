"""."""

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_no_bump(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.id_switches = 0
    te_3d.bump_id_switches([1], 0, 1)
    assert te_3d.id_switches == 0


def test_bump(te_3d: TrackingEvaluation) -> None:
    """."""
    te_3d.id_switches = 0
    te_3d.bump_id_switches([1, 2], 0, 2)
    assert te_3d.id_switches == 1

    te_3d.bump_id_switches([1, 2], 1, 2)
    assert te_3d.id_switches == 1

    te_3d.bump_id_switches([1, 2], 1, 1)
    assert te_3d.id_switches == 2
