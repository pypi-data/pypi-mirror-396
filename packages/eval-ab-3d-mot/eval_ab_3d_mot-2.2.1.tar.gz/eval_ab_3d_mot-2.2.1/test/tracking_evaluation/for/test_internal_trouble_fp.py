"""."""

import pytest

from eval_ab_3d_mot.core.internal_trouble_precision import (
    is_trouble,
    raise_if_trouble_fp,
    raise_trouble,
)


def test_condition() -> None:
    assert not is_trouble(1, 2, 3, 4, 5, 5)
    assert is_trouble(1, 2, 3, 4, 5, 6)
    assert is_trouble(1, 2, 3, 4, 5, 4)


def test_raise_trouble() -> None:
    with pytest.raises(RuntimeError):
        raise_trouble(2, 3, 4, 5, 6, [(1, 2), (3, 4)])


def test_raise_if_trouble() -> None:
    raise_if_trouble_fp(1, 2, 3, 4, 5, 5, 7, 8, [(1, 2), (3, 4)])

    with pytest.raises(RuntimeError):
        raise_if_trouble_fp(1, 2, 3, 4, 5, 6, 7, 8, [(1, 2), (3, 4)])
