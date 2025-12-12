"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_dc_is_loose(te_dc_is_loose: TrackingEvaluation) -> None:
    """."""
    assert te_dc_is_loose.compute_3rd_party_metrics()
    assert te_dc_is_loose.fn == 1
    assert te_dc_is_loose.tp == 1
    assert te_dc_is_loose.MOTP == pytest.approx(1.0)
    assert te_dc_is_loose.F1 == pytest.approx(0.666666666666666)
    assert te_dc_is_loose.recall == pytest.approx(0.5)
    assert te_dc_is_loose.precision == pytest.approx(1.0)
