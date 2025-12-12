"""."""

from pathlib import Path

from eval_ab_3d_mot.cli.common.kitti_adaptor import read_kitti_ab_3d_mot
from eval_ab_3d_mot.kitti_category import KittiCategory


def test_read_kitti_ab_3d_mot(files_dir: Path) -> None:
    ann_path = files_dir / 'kitti/annotations/training/0000.txt'
    adaptor = read_kitti_ab_3d_mot(str(ann_path), KittiCategory.CAR)
    assert adaptor.last_time_stamp == 11
    assert len(adaptor.time_stamps) == 19
