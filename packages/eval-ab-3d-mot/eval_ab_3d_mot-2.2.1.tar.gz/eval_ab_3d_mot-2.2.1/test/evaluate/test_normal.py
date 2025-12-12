"""."""

from pathlib import Path

from eval_ab_3d_mot.evaluate import evaluate


def test_small_normal(files_dir: Path) -> None:
    """."""
    flag = evaluate(
        'my-sha',
        True,
        False,
        0.5,
        str(files_dir / 'evaluation/ann/'),
        str(files_dir / 'evaluation/res/'),
        {'0001': 4},
        ('car',),
    )
    assert flag
