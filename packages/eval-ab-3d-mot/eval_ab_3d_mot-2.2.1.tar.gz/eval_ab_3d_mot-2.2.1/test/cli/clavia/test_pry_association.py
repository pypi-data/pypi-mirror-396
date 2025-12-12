"""."""

from typing import List

import numpy as np
import pytest

from association_quality_clavia import AssociationQuality
from pure_ab_3d_mot.target import Target

from eval_ab_3d_mot.cli.clavia.pry_ab_3d_mot_association import pry_association


@pytest.fixture
def aq() -> AssociationQuality:
    return AssociationQuality()


@pytest.fixture
def targets() -> List[Target]:
    pose = np.linspace(1, 7, num=7)
    info = np.zeros(8)
    return [Target(pose, info, 1, ann_id=3), Target(pose, info, 2, ann_id=4)]


def test_hit_internal_error(aq: AssociationQuality, targets: List[Target]) -> None:
    with pytest.raises(RuntimeError):
        pry_association(targets, [], aq)


def test_normal_operation(aq: AssociationQuality, targets: List[Target]) -> None:
    pry_association(targets, [3, 4, 5], aq)
    assert aq.num_tp == 2
    assert aq.num_tn == 0
    assert aq.num_fp == 0
    assert aq.num_fn == 0
