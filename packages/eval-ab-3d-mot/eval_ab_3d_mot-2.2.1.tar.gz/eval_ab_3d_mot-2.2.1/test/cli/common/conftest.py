"""."""

import numpy as np
import pytest

from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.r_cnn_adaptor import RCnnAdaptor


@pytest.fixture
def tracker() -> Ab3DMot:
    return Ab3DMot()


@pytest.fixture
def adaptor() -> RCnnAdaptor:
    raw_data = np.linspace(1, 15 * 6, num=90).reshape(6, 15)
    raw_data[:, 0] = (1, 3, 3, 5, 5, 5)
    return RCnnAdaptor(raw_data, 10)
