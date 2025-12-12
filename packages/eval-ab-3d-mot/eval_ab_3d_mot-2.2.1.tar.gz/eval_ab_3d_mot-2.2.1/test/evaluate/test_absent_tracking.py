"""."""

from pathlib import Path

import pytest

from eval_ab_3d_mot.evaluate import evaluate


def test_absent_tracking(files_dir: Path) -> None:
    """."""
    with pytest.raises(RuntimeError):
        evaluate(
            'my-sha',
            True,
            False,
            0.5,
            str(files_dir / 'evaluation/ann/'),
            str(files_dir / 'evaluation/res/'),
            {'0001': 4},
            ('car', 'pedestrian'),
        )
