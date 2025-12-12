"""."""

from pathlib import Path

from eval_ab_3d_mot.cli.ab_3d_mot.ab_3d_mot_main import run


def test_cli_run_3d(files_dir: Path) -> None:
    """."""
    det_file = files_dir / 'kitti/detections/point-r-cnn-training/cyclist/0000.txt'
    args = [str(det_file), '-v', '--last-ts', '10']
    assert run(args)
