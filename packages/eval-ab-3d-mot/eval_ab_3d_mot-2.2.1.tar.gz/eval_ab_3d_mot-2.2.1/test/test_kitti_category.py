"""."""

from eval_ab_3d_mot.kitti_category import KittiCategory


def test_get_kitti_labels() -> None:
    assert KittiCategory.CAR.get_kitti_labels() == ('Car', 'Van')
    assert KittiCategory.CYCLIST.get_kitti_labels() == ('Cyclist',)
    assert KittiCategory.PEDESTRIAN.get_kitti_labels() == ('Pedestrian',)


def test_get_int_category() -> None:
    assert KittiCategory.CAR.get_int_category() == 2
    assert KittiCategory.CYCLIST.get_int_category() == 3
    assert KittiCategory.PEDESTRIAN.get_int_category() == 1
