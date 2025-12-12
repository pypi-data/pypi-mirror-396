"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


@pytest.fixture()
def te_sum(te_3d: TrackingEvaluation) -> TrackingEvaluation:
    """."""
    te_3d.ML = 34
    te_3d.MT = 45
    te_3d.PT = 56
    te_3d.sMOTA = 0.1
    te_3d.MOTA = 0.2
    te_3d.MOTP = 0.3
    te_3d.MOTAL = 0.4
    te_3d.MODA = 0.5
    te_3d.MODP = 1.6
    te_3d.id_switches = 123
    te_3d.fragments = 432
    te_3d.F1 = 0.6
    te_3d.FAR = 0.7
    te_3d.precision = 0.8
    te_3d.recall = 0.9
    te_3d.itp = 46
    te_3d.tp = 456
    te_3d.fp = 126
    te_3d.fn = 789
    te_3d.ifn = 78
    te_3d.n_gt = 47
    te_3d.n_igt = 48
    te_3d.n_tr = 49
    te_3d.n_itr = 50
    te_3d.n_gt_trajectories = 51
    te_3d.n_tr_trajectories = 52
    return te_3d
