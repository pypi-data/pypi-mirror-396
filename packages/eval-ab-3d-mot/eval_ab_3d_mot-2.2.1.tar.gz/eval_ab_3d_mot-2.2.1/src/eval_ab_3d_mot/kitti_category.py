"""."""

from enum import Enum
from typing import Tuple, Union


CLASS_NAMES = ['?', 'Pedestrian', 'Car', 'Cyclist']


class KittiCategory(Enum):
    CAR = 'car'
    CYCLIST = 'cyclist'
    PEDESTRIAN = 'pedestrian'

    def get_kitti_labels(self) -> Union[Tuple[str], Tuple[str, str]]:
        if self == KittiCategory.CAR:
            return 'Car', 'Van'
        else:
            return (self.value.capitalize(),)

    def get_int_category(self) -> int:
        return CLASS_NAMES.index(self.value.capitalize())
