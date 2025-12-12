"""."""

from pathlib import Path

from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.kitti_adaptor import read_kitti_ab_3d_mot
from eval_ab_3d_mot.cli.common.single_sequence import get_tracking_result
from eval_ab_3d_mot.cli.common.tracking_io import write_ab_3d_mot_tracking
from eval_ab_3d_mot.kitti_category import KittiCategory


def test_full_pipeline(files_dir: Path, tmp_path: Path) -> None:
    ann_path = files_dir / 'kitti/annotations/full-ann-tracking-pipeline.txt'
    adaptor = read_kitti_ab_3d_mot(str(ann_path), KittiCategory.CAR)
    tracker = Ab3DMot()
    result = get_tracking_result(adaptor, tracker, 1)
    result_path = tmp_path / 'tracking_result.txt'
    write_ab_3d_mot_tracking(result, str(result_path))
    result_txt = result_path.read_text()
    ref = """0 1 Car 0 0 -1.793451 296.744956 161.752147 455.226042 292.372804 2.000000 1.823255 4.433886 -4.552284 1.858523 13.410495 -2.115488 1.234567
1 1 Car 0 0 -1.796862 294.898777 156.024256 452.199718 284.621269 2.000000 1.823255 4.433886 -4.650945 1.766783 13.581068 -2.121059 1.234567
"""
    assert result_txt == ref
