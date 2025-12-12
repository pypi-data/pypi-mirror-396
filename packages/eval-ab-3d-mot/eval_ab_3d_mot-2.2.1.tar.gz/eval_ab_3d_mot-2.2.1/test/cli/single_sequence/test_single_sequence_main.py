"""."""

from pathlib import Path

from eval_ab_3d_mot.cli.single_sequence.single_sequence_main import run


def test_cli_run_3d(files_dir: Path) -> None:
    ann_file = files_dir / 'kitti/annotations/training/0012.txt'
    trk_file = files_dir / 'kitti/tracking/training/0012.txt'
    args = [str(ann_file), '--trk-file-name', str(trk_file), '-v']
    assert run(args)
