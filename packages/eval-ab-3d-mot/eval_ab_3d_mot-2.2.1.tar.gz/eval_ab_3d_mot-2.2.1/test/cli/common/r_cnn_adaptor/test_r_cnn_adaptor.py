"""."""

import numpy as np
import pytest

from eval_ab_3d_mot.cli.common.r_cnn_adaptor import DETS, INFO, RCnnAdaptor


def test_r_cnn_adaptor(adaptor: RCnnAdaptor) -> None:
    """."""
    all_det = []
    for ts, det_dct in enumerate(adaptor.detections_3d()):
        all_det.append(det_dct)

    assert len(all_det) == 11
    assert len(all_det[0][DETS]) == 0
    assert all_det[1][DETS] == pytest.approx(np.array([[8, 9, 10, 11, 12, 13, 14]]))
    assert len(all_det[2][DETS]) == 0
    assert all_det[3][DETS] == pytest.approx(
        np.array([[23, 24, 25, 26, 27, 28, 29], [38, 39, 40, 41, 42, 43, 44]])
    )
    assert len(all_det[4][DETS]) == 0
    assert all_det[5][DETS] == pytest.approx(
        np.array(
            [
                [53, 54, 55, 56, 57, 58, 59],
                [68, 69, 70, 71, 72, 73, 74],
                [83, 84, 85, 86, 87, 88, 89],
            ]
        )
    )
    for ts in range(6, 11):
        assert all_det[ts][DETS].shape == (0, 7)
        assert all_det[ts][INFO].shape == (0, 8)
