"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_get_data_dict(te_3d: TrackingEvaluation) -> None:
    te_3d.MOTA = 0.1
    te_3d.MODA = 0.11
    te_3d.MOTP = 0.12
    te_3d.MODP = 0.13
    te_3d.precision = 0.14
    te_3d.F1 = 0.15
    te_3d.fp = 16
    te_3d.fn = 17
    te_3d.recall = 0.18
    te_3d.sMOTA = 0.19
    dct = te_3d.get_data_dict()
    assert dct['mota'] == pytest.approx(0.1)
    assert dct['motp'] == pytest.approx(0.12)
    assert dct['moda'] == pytest.approx(0.11)
    assert dct['modp'] == pytest.approx(0.13)
    assert dct['precision'] == pytest.approx(0.14)
    assert dct['F1'] == pytest.approx(0.15)
    assert dct['fp'] == 16
    assert dct['fn'] == 17
    assert dct['recall'] == pytest.approx(0.18)
    assert dct['sMOTA'] == pytest.approx(0.19)
