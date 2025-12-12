"""."""

from typing import Sequence, Union

from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.r_cnn_adaptor import read_r_cnn_ab_3d_mot
from eval_ab_3d_mot.cli.common.single_sequence import get_tracking_result
from eval_ab_3d_mot.cli.common.tracking_io import write_ab_3d_mot_tracking

from .cmd_line import get_cmd_line


def run(args: Union[Sequence[str], None] = None) -> bool:
    cli = get_cmd_line(args)
    adaptor = read_r_cnn_ab_3d_mot(cli.det_file_name, cli.ann_dir, cli.last_ts)
    tracker = Ab3DMot()
    result = get_tracking_result(adaptor, tracker, cli.verbosity)
    write_ab_3d_mot_tracking(result, cli.trk_file_name)
    print('written', cli.trk_file_name)
    return True


def main() -> None:
    run()  # pragma: no cover
