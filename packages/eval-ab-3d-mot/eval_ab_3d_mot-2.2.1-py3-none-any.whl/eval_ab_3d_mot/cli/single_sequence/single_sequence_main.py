"""."""

import shutil

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Sequence, Union

from eval_ab_3d_mot.cli.common.annotation_num_frames import get_seq_lengths_name
from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation
from eval_ab_3d_mot.evaluate_and_report import evaluate_and_report

from .cmd_line import get_cmd_line


def run(args: Union[Sequence[str], None] = None) -> bool:
    result_sha = 'single-sequence'
    cli = get_cmd_line(args)
    ann_path = cli.get_ann_path()
    seq_lengths_name = get_seq_lengths_name([str(ann_path)])

    trk_path = Path(cli.trk_file_name)
    category = trk_path.read_text().splitlines()[0].split()[2].lower()
    trk_eval = TrackingEvaluation(result_sha, seq_lengths_name, cls=category)
    trk_eval.gt_path = str(ann_path.parent)
    trk_eval.load_data(True)

    with TemporaryDirectory() as tmpdir:
        seq_name = ann_path.with_suffix('').name
        tmp_file_path = (Path(tmpdir) / seq_name).with_suffix('.txt')
        shutil.copy(trk_path, tmp_file_path)
        trk_eval.t_path = str(tmp_file_path.parent)
        trk_eval.load_data(False)

    file_name = './single_sequence_result.txt'
    evaluate_and_report(trk_eval, result_sha, file_name, False)
    return True


def main() -> None:
    run()  # pragma: no cover
