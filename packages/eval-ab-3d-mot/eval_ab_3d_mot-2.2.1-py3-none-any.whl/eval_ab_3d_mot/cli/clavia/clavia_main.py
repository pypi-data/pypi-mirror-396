"""."""

from typing import Sequence, Union

from association_quality_clavia import AssociationQuality
from pure_ab_3d_mot.tracker import ANN_IDS

from eval_ab_3d_mot.cli.common.ab_3d_mot_parameters import report_tracker_parameters
from eval_ab_3d_mot.cli.common.kitti_adaptor import read_kitti_ab_3d_mot
from eval_ab_3d_mot.cli.common.tracker_factory import get_tracker

from .bin_class_ratios import get_summary
from .cmd_line_factory import get_cmd_line
from .pry_ab_3d_mot_association import pry_association


def run(args: Union[Sequence[str], None] = None) -> str:
    cli = get_cmd_line(args)
    association_quality = AssociationQuality()
    if cli.verbosity > 1:
        print(report_tracker_parameters(get_tracker(cli.get_parameter_category(), cli.meta)))

    for ann_file_name in cli.get_annotation_file_names():
        adaptor = read_kitti_ab_3d_mot(ann_file_name, cli.get_object_category())
        adaptor.check_and_shout_eventually(ann_file_name, cli.verbosity)
        tracker = get_tracker(cli.get_parameter_category(), cli.meta)
        for detections_dct in adaptor.detections_3d():
            tracker.track(detections_dct)
            pry_association(tracker.trackers, detections_dct[ANN_IDS], association_quality)

    txt_summary = get_summary(association_quality.get_confusion_matrix())
    print(txt_summary)
    return txt_summary


def main() -> None:
    run()  # pragma: no cover
