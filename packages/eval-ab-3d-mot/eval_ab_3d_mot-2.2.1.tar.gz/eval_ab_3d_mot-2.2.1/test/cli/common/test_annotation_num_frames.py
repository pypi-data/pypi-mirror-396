"""."""

from pathlib import Path

from eval_ab_3d_mot.cli.common.annotation_num_frames import (
    get_frame_number_from_ann_file,
    get_seq_lengths_name,
)


def test_get_frame_number_from_ann_file(files_dir: Path) -> None:
    path = files_dir / 'kitti/annotations/training/0001.txt'
    assert get_frame_number_from_ann_file(path) == 448


def test_get_seq_lengths_name(files_dir: Path) -> None:
    path1 = files_dir / 'kitti/annotations/training/0001.txt'
    path2 = files_dir / 'kitti/annotations/training/0012.txt'
    ref = {'0001': 448, '0012': 79}
    assert get_seq_lengths_name([str(path1), str(path2)]) == ref
