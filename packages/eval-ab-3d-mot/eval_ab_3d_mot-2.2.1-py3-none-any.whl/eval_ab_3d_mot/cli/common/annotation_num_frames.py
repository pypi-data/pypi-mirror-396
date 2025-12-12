"""."""

from pathlib import Path
from typing import Dict, List

import numpy as np


def get_frame_number_from_ann_file(ann_path: Path) -> int:
    frame_numbers = np.genfromtxt(ann_path, usecols=[0], dtype=int)
    return int(np.max(frame_numbers) + 2)
    # should be +1, but in order to have this number as in original repo, we use +2.


def get_seq_lengths_name(ann_file_names: List[str]) -> Dict[str, int]:
    seq_lengths_name = {}
    for path in map(Path, ann_file_names):
        seq_name = path.with_suffix('').name
        seq_lengths_name[seq_name] = get_frame_number_from_ann_file(path)
    return seq_lengths_name
