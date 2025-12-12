"""."""

from pathlib import Path

import pytest

from eval_ab_3d_mot.cli.common.r_cnn_adaptor import read_r_cnn_ab_3d_mot


@pytest.fixture
def det_cyclist(files_dir: Path) -> str:
    return str(files_dir / 'kitti/detections/point-r-cnn-training/cyclist/0000.txt')


def test_from_ann_file(files_dir: Path, det_cyclist: str) -> None:
    ann_dir = str(files_dir / 'kitti/annotations/training')
    adaptor = read_r_cnn_ab_3d_mot(det_cyclist, ann_dir, 0)
    assert len(adaptor.unique_tss) == 8
    assert adaptor.last_time_stamp == 12


def test_from_argument(det_cyclist: str) -> None:
    adaptor = read_r_cnn_ab_3d_mot(det_cyclist, 'any-really', 123)
    assert len(adaptor.unique_tss) == 8
    assert adaptor.last_time_stamp == 123


def test_absent_ann_file(det_cyclist: str) -> None:
    with pytest.raises(ValueError):
        read_r_cnn_ab_3d_mot(det_cyclist, 'absent.txt', 0)
