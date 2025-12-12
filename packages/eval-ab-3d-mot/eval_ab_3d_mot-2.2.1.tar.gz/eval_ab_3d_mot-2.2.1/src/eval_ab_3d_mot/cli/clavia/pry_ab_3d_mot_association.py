"""."""

from typing import Sequence, Union

import numpy as np

from association_quality_clavia import AssociationQuality
from pure_ab_3d_mot.target import Target


def pry_association(
    targets: Sequence[Target],
    ann_ids: Union[Sequence[int], np.ndarray],
    association_quality: AssociationQuality,
) -> None:
    for target in targets:
        is_supplied = target.ann_id in ann_ids
        association_quality.classify(target.ann_id, target.upd_id, is_supplied)
