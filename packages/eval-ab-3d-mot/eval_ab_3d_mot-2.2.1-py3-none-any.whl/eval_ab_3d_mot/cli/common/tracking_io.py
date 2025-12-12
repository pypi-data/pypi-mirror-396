"""."""

import csv

from typing import Any, List, Union

import numpy as np

from eval_ab_3d_mot.kitti_category import CLASS_NAMES


def fmt(val: Any) -> str:
    if isinstance(val, float):
        return f'{val:.6f}'
    return str(val)


def get_kitti_tracking(track: np.ndarray) -> List[Union[int, float, str]]:
    assert track.shape == (1, 16)
    kitti_det = track[0, 0:7]
    track_id = int(track[0, 7])
    _frame_num = int(track[0, 8])
    class_name = CLASS_NAMES[int(track[0, 9])]
    truncation, occlusion, alpha = 0, 0, float(track[0, 15])
    bbox = track[0, 10:14].tolist()
    # The field 14 is part of the detection info
    # It should be some measure of the detection confidence in some convention.
    # In original ab-3D-MOT this is the last column.
    # In the r-cnn detection files this field follows the bounding box.
    header = [track_id, class_name, truncation, occlusion, alpha] + bbox
    return header + kitti_det.tolist() + [float(track[0, 14])]


def write_ab_3d_mot_tracking(result: List[List[np.ndarray]], file_name: str) -> None:
    """."""
    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        for step, tracks_at_time_step in enumerate(result):
            step_ls = [step]
            if len(tracks_at_time_step) > 0:
                for track in tracks_at_time_step:
                    line_ls = step_ls + get_kitti_tracking(track)
                    writer.writerow([fmt(e) for e in line_ls])
