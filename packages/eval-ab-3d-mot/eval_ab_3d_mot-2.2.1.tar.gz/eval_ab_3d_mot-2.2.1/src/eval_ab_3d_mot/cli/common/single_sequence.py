"""."""

from typing import List, Union

import numpy as np

from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.kitti_adaptor import KittiAdaptor
from eval_ab_3d_mot.cli.common.r_cnn_adaptor import DETS, RCnnAdaptor


def get_tracking_result(
    adaptor: Union[RCnnAdaptor, KittiAdaptor], tracker: Ab3DMot, verbosity: int
) -> List[List[np.ndarray]]:
    result = []
    if verbosity > 3:
        np.set_printoptions(linewidth=200)

    for step, det_dct in enumerate(adaptor.detections_3d()):
        tracker.track(det_dct)
        persistent_tracks = tracker.output()
        result.append(persistent_tracks)
        if verbosity > 2:
            print(step, len(det_dct[DETS]), len(persistent_tracks))
        if verbosity > 3:
            for track in persistent_tracks:
                print(track)
            print()

    return result
