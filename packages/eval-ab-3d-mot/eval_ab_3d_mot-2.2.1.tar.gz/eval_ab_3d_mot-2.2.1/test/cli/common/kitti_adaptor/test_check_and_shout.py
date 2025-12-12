"""."""

import numpy as np
import pytest

from eval_ab_3d_mot.cli.common.kitti_adaptor import KittiAdaptor


def test_verbosity_0(adaptor: KittiAdaptor, capsys: pytest.CaptureFixture) -> None:
    adaptor.check_and_shout_eventually('file name', 0)
    assert capsys.readouterr().out == ''


def test_verbosity_1(adaptor: KittiAdaptor, capsys: pytest.CaptureFixture) -> None:
    adaptor.check_and_shout_eventually('file name', 1)
    assert capsys.readouterr().out == 'Tracking for file name\n'


def test_verbosity_2(adaptor: KittiAdaptor, capsys: pytest.CaptureFixture) -> None:
    adaptor.time_stamps = np.empty(0, int)
    adaptor.check_and_shout_eventually('file name', 2)
    # fmt: off
    ref = ('Tracking for file name\n'
           'There is no objects of KittiCategory.CAR, but I will continue...\n')
    # fmt: on
    assert capsys.readouterr().out == ref
