import pytest

from eval_ab_3d_mot.cli.common.kitti_category import AUTO_CATEGORY, get_kitti_category
from eval_ab_3d_mot.kitti_category import KittiCategory


def test_get_category() -> None:
    assert get_kitti_category(AUTO_CATEGORY, 'car/0001.txt') == KittiCategory.CAR
    assert get_kitti_category('pedestrian', 'car/0001.txt') == KittiCategory.PEDESTRIAN
    with pytest.raises(ValueError):
        get_kitti_category('bogus', 'car/0001.txt')
