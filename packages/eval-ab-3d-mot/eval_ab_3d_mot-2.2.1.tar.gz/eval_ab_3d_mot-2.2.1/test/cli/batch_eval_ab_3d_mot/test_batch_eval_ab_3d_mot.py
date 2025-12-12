"""."""

from pathlib import Path

from eval_ab_3d_mot.cli.batch_eval_ab_3d_mot.batch_eval_ab_3d_mot_main import run


def test_run(files_dir: Path, tmp_path: Path) -> None:
    # fmt: off
    args = [
        str(files_dir / 'evaluation/ann/label/0000.txt'),
        str(files_dir / 'evaluation/ann/label/0012.txt'),
        '-i', str(files_dir / 'evaluation/tracking/short'),
        '-v',
        '-c', 'cyclist',
        '-o', 'evaluation-kitti',
        '-l', 'sha'
    ]
    # fmt: on
    assert run(args)
    assert (tmp_path / 'evaluation-kitti/sha/cyclist/batch-eval-ab-3d-mot-result.txt').exists()
