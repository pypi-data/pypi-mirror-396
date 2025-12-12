"""."""

from pathlib import Path

from eval_ab_3d_mot.kitti_category import KittiCategory


HLP_CATEGORY = 'KITTI category.'
AUTO_CATEGORY = 'derived-from-dir-name'
CATEGORIES = tuple(c.value for c in KittiCategory) + (AUTO_CATEGORY,)


def get_kitti_category(category: str, file_name: str) -> KittiCategory:
    cls_opt = category
    first_path = Path(file_name)
    return KittiCategory(first_path.parent.name if cls_opt == AUTO_CATEGORY else cls_opt)
