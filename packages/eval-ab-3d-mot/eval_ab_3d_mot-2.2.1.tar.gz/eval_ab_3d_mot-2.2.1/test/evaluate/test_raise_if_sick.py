"""."""

import pytest

from eval_ab_3d_mot.raise_if_sick import raise_if_sick


def test_raise() -> None:
    """."""
    raise_if_sick(3, 3)
    with pytest.raises(RuntimeError):
        raise_if_sick(2, 3)
