"""."""

from pathlib import Path
from typing import Dict, Iterable

import numpy as np

from pure_ab_3d_mot.str_const import DETS, INFO

from eval_ab_3d_mot.cli.common.annotation_num_frames import get_frame_number_from_ann_file


class RCnnAdaptor:
    def __init__(self, raw_data: np.ndarray, num_ts_ann: int) -> None:
        assert raw_data.ndim == 2
        assert raw_data.shape[1] == 15
        self.raw_data: np.ndarray = raw_data
        self.time_stamps = np.array(raw_data[:, 0], int)
        self.unique_tss = np.unique(self.time_stamps)
        assert num_ts_ann >= self.unique_tss.max()
        self.last_time_stamp = num_ts_ann

    def detections_3d(self) -> Iterable[Dict[str, np.ndarray]]:
        for ts in range(self.last_time_stamp + 1):
            ts_data = self.raw_data[self.time_stamps == ts, :]
            hwl_xyz_ry = ts_data[:, 7:14]
            info = np.zeros((ts_data.shape[0], 8))
            info[:, :7] = ts_data[:, :7]
            info[:, 7] = ts_data[:, -1]
            yield {DETS: hwl_xyz_ry, INFO: info}


def read_r_cnn_ab_3d_mot(file_name: str, ann_dir: str, last_ts: int) -> RCnnAdaptor:
    det_data = np.loadtxt(file_name, delimiter=',')
    if last_ts < 1:
        ann_path = Path(ann_dir) / Path(file_name).name
        if not ann_path.exists():
            raise ValueError(
                f'The annotation file {ann_path} does not exist. '
                'I need this file to find the number of time stamps.'
            )
        last_ts = get_frame_number_from_ann_file(str(ann_path)) - 1
    else:
        last_ts = last_ts
    return RCnnAdaptor(det_data, last_ts)
