"""."""

import numpy as np
import pytest

from eval_ab_3d_mot.cli.common.kitti_adaptor import KittiAdaptor
from eval_ab_3d_mot.kitti_category import KittiCategory


@pytest.fixture
def adaptor() -> KittiAdaptor:
    ids_l = np.array([1, 2, 3, 4], int)
    stamps_l = np.array([1, 2, 3, 9], int)
    category_l = np.array(['Car', 'Van', 'Cyclist', 'Pedestrian'], str)
    detections_l = np.array(
        [
            np.linspace(1, 7, num=7),
            np.linspace(2, 8, num=7),
            np.linspace(3, 9, num=7),
            np.linspace(4, 10, num=7),
        ]
    )
    info_l = np.array(
        [
            np.linspace(21, 28, num=8),
            np.linspace(22, 29, num=8),
            np.linspace(23, 30, num=8),
            np.linspace(24, 31, num=8),
        ]
    )
    return KittiAdaptor(stamps_l, ids_l, category_l, detections_l, KittiCategory.CAR, info_l)
