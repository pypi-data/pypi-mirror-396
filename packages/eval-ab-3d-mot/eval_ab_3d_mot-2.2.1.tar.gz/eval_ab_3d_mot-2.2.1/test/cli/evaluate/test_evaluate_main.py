"""."""

from pathlib import Path

from eval_ab_3d_mot.cli.evaluate.evaluate_main import run


def test_cli_run_3d(files_dir: Path) -> None:
    """."""
    # fmt: off
    args = ['--seq-names', '0001',
            '--seq-lengths', '4',
            '--classes', 'car',
            '--ann-root', str(files_dir / 'evaluation/ann/'),
            '--res-root', str(files_dir / 'evaluation/res/'),
            '-t', '0.1']
    # fmt: on
    assert run(args)


def test_cli_run_2d(files_dir: Path) -> None:
    """."""
    # fmt: off
    args = ['--seq-names', '0001',
            '--seq-lengths', '4',
            '--classes', 'car',
            '-d', '2',
            '--ann-root', str(files_dir / 'evaluation/ann/'),
            '--res-root', str(files_dir / 'evaluation/res/'),
            '-t', '0.1']
    # fmt: on
    assert run(args)
