"""."""

from typing import List

from eval_ab_3d_mot.cli.common.tracker_meta import AUTO, TrackerMeta
from eval_ab_3d_mot.kitti_category import KittiCategory


class CmdLineBatchRunAb3dMotAnnotations:
    def __init__(self) -> None:
        self.verbosity = 0
        self.annotations: List[str] = []
        self.category_obj = KittiCategory.CAR.value
        self.category_prm = AUTO
        self.trk_dir = 'tracking-kitti'
        self.meta = TrackerMeta()

    def __repr__(self) -> str:
        return f'CmdLineBatchRunAb3dMotAnnotations(category-obj {self.category_obj} parameters({self.meta}))'

    def get_object_category(self) -> KittiCategory:
        return KittiCategory(self.category_obj)

    def get_parameter_category(self) -> KittiCategory:
        if self.category_prm == AUTO:
            result = KittiCategory(self.category_obj)
        else:
            result = KittiCategory(self.category_prm)
        return result

    def get_annotation_file_names(self) -> List[str]:
        return sorted(self.annotations)
