"""."""

import pytest

from eval_ab_3d_mot.core.internal_trouble_recall import raise_if_trouble_fn


def test_raise_if_trouble() -> None:
    raise_if_trouble_fn(1, 2, 10, 3, 4, 5, 7, 8, [(1, 2), (3, 4)])

    with pytest.raises(RuntimeError):
        raise_if_trouble_fn(1, 2, 7, 3, 4, 5, 7, 8, [(1, 2), (3, 4)])
