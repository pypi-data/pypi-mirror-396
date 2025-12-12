"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_unmatched_van(te_dc_is_loose: TrackingEvaluation) -> None:
    """."""
    te_dc_is_loose.ground_truth[0][0][0].obj_type = 'van'
    assert te_dc_is_loose.compute_3rd_party_metrics()
    assert te_dc_is_loose.fn == 0
    assert te_dc_is_loose.tp == 1
    assert te_dc_is_loose.MOTP == pytest.approx(1.0)
    assert te_dc_is_loose.F1 == pytest.approx(1.0)
    assert te_dc_is_loose.recall == pytest.approx(1.0)
    assert te_dc_is_loose.precision == pytest.approx(1.0)
