"""."""

import pytest

from eval_ab_3d_mot.thresholds import get_thresholds


def test_get_thresholds_102() -> None:
    """."""
    thresholds, recalls = get_thresholds([0.75, 0.7, 0.8, 0.9, 0.96], 67, 102)
    assert thresholds == pytest.approx([0.9, 0.8, 0.75, 0.7])
    assert recalls == pytest.approx(
        [0.009900990099009901, 0.019801980198019802, 0.0297029702970297, 0.039603960396039604]
    )


def test_get_thresholds_12() -> None:
    """."""
    thresholds, recalls = get_thresholds([0.75, 0.7, 0.8, 0.9, 0.96], 67, 12)
    assert thresholds == pytest.approx([0.7])
    assert recalls == pytest.approx([0.09090909090909091])
