"""."""

import pytest

from eval_ab_3d_mot.core.internal_troubles_negative import (
    raise_if_negative_fn,
    raise_if_negative_fp,
    raise_if_negative_tp,
)


def test_raise_if_negative_fp() -> None:
    raise_if_negative_fp(1, 2, 3, 4, 5, 5)

    with pytest.raises(RuntimeError):
        raise_if_negative_fp(-1, 2, 3, 4, 5, 6)


def test_raise_if_negative_fn() -> None:
    raise_if_negative_fn(1, 2, 3, 4, 5)

    with pytest.raises(RuntimeError):
        raise_if_negative_fn(-1, 2, 3, 4, 5)


def test_raise_if_negative_tp() -> None:
    raise_if_negative_tp(1, 2)

    with pytest.raises(RuntimeError):
        raise_if_negative_tp(-1, 2)
