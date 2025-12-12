"""."""

import numpy as np
import pytest

from pure_ab_3d_mot.str_const import DETS, INFO

from eval_ab_3d_mot.cli.common.kitti_adaptor import ANN_IDS, KittiAdaptor


def test_generator(adaptor: KittiAdaptor) -> None:
    all_detections = []
    for dct in adaptor.detections_3d():
        all_detections.append(dct)

    assert len(all_detections) == 10
    for ts in (0, 3, 4, 5, 6, 7, 8, 9):
        dd = all_detections[ts]
        assert dd[DETS].shape == (0, 7)
        assert dd[INFO].shape == (0, 8)
        assert dd[ANN_IDS].shape == (0,)

    assert all_detections[1][DETS] == pytest.approx(np.array([[1, 2, 3, 4, 5, 6, 7]]))
    assert all_detections[1][INFO] == pytest.approx(
        np.array([[0, 2, 25, 26, 27, 28, 1.234567, 24]])
    )
    assert all_detections[1][ANN_IDS] == pytest.approx([1])

    assert all_detections[2][DETS] == pytest.approx(np.array([[2, 3, 4, 5, 6, 7, 8]]))
    assert all_detections[2][INFO] == pytest.approx(
        np.array([[0, 2, 26, 27, 28, 29, 1.234567, 25]])
    )
    assert all_detections[2][ANN_IDS] == pytest.approx([2])
