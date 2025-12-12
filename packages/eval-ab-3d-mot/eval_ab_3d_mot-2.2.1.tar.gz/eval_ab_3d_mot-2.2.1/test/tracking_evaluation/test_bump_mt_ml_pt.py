"""."""

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_all(te_3d: TrackingEvaluation) -> None:
    te_3d.bump_mt_ml_pt(0.81)
    assert te_3d.MT == 1
    assert te_3d.PT == 0
    assert te_3d.ML == 0

    te_3d.bump_mt_ml_pt(0.79)
    assert te_3d.MT == 1
    assert te_3d.PT == 1
    assert te_3d.ML == 0

    te_3d.bump_mt_ml_pt(0.21)
    assert te_3d.MT == 1
    assert te_3d.PT == 2
    assert te_3d.ML == 0

    te_3d.bump_mt_ml_pt(0.19)
    assert te_3d.MT == 1
    assert te_3d.PT == 2
    assert te_3d.ML == 1
