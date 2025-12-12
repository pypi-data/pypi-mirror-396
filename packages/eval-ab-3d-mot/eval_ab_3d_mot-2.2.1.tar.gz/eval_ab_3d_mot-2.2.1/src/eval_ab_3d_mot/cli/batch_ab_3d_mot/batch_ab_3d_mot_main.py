"""."""

from pathlib import Path
from typing import Sequence, Union

from rich.progress import Progress

from eval_ab_3d_mot.cli.common.ab_3d_mot_parameters import report_tracker_parameters
from eval_ab_3d_mot.cli.common.r_cnn_adaptor import read_r_cnn_ab_3d_mot
from eval_ab_3d_mot.cli.common.single_sequence import get_tracking_result
from eval_ab_3d_mot.cli.common.tracker_factory import get_tracker
from eval_ab_3d_mot.cli.common.tracking_io import write_ab_3d_mot_tracking

from .cmd_line_factory import get_cmd_line


def run(args: Union[Sequence[str], None] = None) -> bool:
    cli = get_cmd_line(args)
    category = cli.get_object_category()
    if cli.verbosity > 1:
        print(report_tracker_parameters(get_tracker(cli.get_parameter_category(), cli.meta)))

    result_root = Path(cli.trk_dir) / category.value
    result_root.mkdir(exist_ok=True, parents=True)
    with Progress() as progress:
        detections = cli.get_detection_file_names()
        task = progress.add_task('[cyan]Working...', total=len(detections))
        for det_file_name in detections:
            adaptor = read_r_cnn_ab_3d_mot(det_file_name, cli.ann_dir, 0)
            tracker = get_tracker(cli.get_parameter_category(), cli.meta)
            result = get_tracking_result(adaptor, tracker, cli.verbosity)
            output_path = result_root / Path(det_file_name).name
            print(f'    Store {output_path}')
            write_ab_3d_mot_tracking(result, str(output_path))
            progress.update(task, advance=1)

    return True


def main() -> None:
    run()  # pragma: no cover
