"""."""

from pathlib import Path

from eval_ab_3d_mot.cli.batch_ab_3d_mot_annotations.batch_ab_3d_mot_annotations_main import run


def test_run(files_dir: Path, tmp_path: Path) -> None:
    # fmt: off
    args = [
        str(files_dir / 'kitti/annotations/training/0000.txt'),
        str(files_dir / 'kitti/annotations/training/0012.txt'),
        '-vv',
        '-o', 'tracking-results',
        '-c', 'cyclist'
    ]
    # fmt: on
    assert run(args)
    assert (tmp_path / 'tracking-results').exists()
    assert (tmp_path / 'tracking-results/cyclist').exists()
    assert (tmp_path / 'tracking-results/cyclist/0000.txt').exists()
    assert (tmp_path / 'tracking-results/cyclist/0012.txt').exists()
