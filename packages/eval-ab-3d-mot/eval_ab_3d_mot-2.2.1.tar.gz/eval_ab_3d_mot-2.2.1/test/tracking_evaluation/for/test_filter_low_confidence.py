"""."""

import pytest

from eval_ab_3d_mot.core.filter_low_confidence import filter_low_confidence


def test_filter() -> None:
    """."""
    scores_id = {1: [0.1, 0.6], 2: [0.7, 0.8, 0.9]}
    av_scores, to_delete = filter_low_confidence(scores_id, 0.5)
    assert len(to_delete) == 1
    assert to_delete[0] == 1
    assert len(av_scores) == 2
    assert av_scores[1] == pytest.approx(0.35)
    assert av_scores[2] == pytest.approx(0.8)
