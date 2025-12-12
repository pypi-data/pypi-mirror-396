"""."""

from pathlib import Path

import pytest

from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.r_cnn_adaptor import read_r_cnn_ab_3d_mot
from eval_ab_3d_mot.cli.common.single_sequence import get_tracking_result
from eval_ab_3d_mot.cli.common.tracking_io import get_kitti_tracking


def test_reproduce_track_data_0(files_dir: Path) -> None:
    det_path = files_dir / 'kitti/detections/point-r-cnn-training/car/0001.txt'
    ann_dir = files_dir / 'kitti/annotations/training'
    adaptor = read_r_cnn_ab_3d_mot(str(det_path), str(ann_dir), 0)
    tracker = Ab3DMot()
    result = get_tracking_result(adaptor, tracker, 1)
    lst = get_kitti_tracking(result[0][0])
    assert lst[:2] == [6, 'Car']
    # fmt: off
    ref2 = [0, 0, 1.7353, 494.4558, 186.9417, 529.2401, 212.2504,
            1.492, 1.6134, 3.9173, -6.3405, 2.4432, 46.7199, 1.6004, 4.3019]
    # fmt: on
    assert lst[2:] == pytest.approx(ref2)
