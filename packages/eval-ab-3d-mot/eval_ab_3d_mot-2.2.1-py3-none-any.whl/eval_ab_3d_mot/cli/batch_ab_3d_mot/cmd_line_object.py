"""."""

from pathlib import Path
from typing import List

from eval_ab_3d_mot.cli.common.kitti_category import AUTO_CATEGORY, get_kitti_category
from eval_ab_3d_mot.cli.common.tracker_meta import AUTO, TrackerMeta
from eval_ab_3d_mot.kitti_category import KittiCategory


class CmdLineBatchRunAb3dMot:
    def __init__(self) -> None:
        self.verbosity = 0
        self.ann_dir = 'assets/annotations/kitti/training'
        self.detections: List[str] = []
        self.trk_dir = 'tracking-kitti'
        self.category_obj = AUTO_CATEGORY
        self.category_prm = AUTO
        self.meta = TrackerMeta()

    def __repr__(self) -> str:
        return f'CmdLineBatchRunAb3dMot(category-obj {self.category_obj} parameters({self.meta}))'

    def get_object_category(self) -> KittiCategory:
        return get_kitti_category(self.category_obj, self.detections[0])

    def get_parameter_category(self) -> KittiCategory:
        if self.category_prm == AUTO:
            result = self.get_object_category()
        else:
            result = KittiCategory(self.category_prm)
        return result

    def get_detection_file_names(self) -> List[str]:
        if len(set(Path(d).parent for d in self.detections)) > 1:
            raise ValueError('I expect the detection files to be in the same directory.')
        return sorted(self.detections)
