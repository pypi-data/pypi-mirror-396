"""."""

from pathlib import Path
from typing import Sequence, Union

from eval_ab_3d_mot.cli.common.annotation_num_frames import get_seq_lengths_name
from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation
from eval_ab_3d_mot.evaluate_and_report import evaluate_and_report

from .cmd_line import get_cmd_line


def run(args: Union[Sequence[str], None] = None) -> bool:
    cli = get_cmd_line(args)
    category = cli.get_category().value
    ann_files = cli.get_annotation_file_names()
    seq_lengths_name = get_seq_lengths_name(ann_files)
    trk_eval = TrackingEvaluation(cli.label, seq_lengths_name, cls=category, thres=cli.threshold)
    trk_eval.t_path = cli.get_trk_path()
    print(f'Loading tracking data from {trk_eval.t_path}/ ...')
    trk_eval.load_data(False)

    trk_eval.gt_path = cli.get_gt_path()
    print(f'Loading ground truth data from {trk_eval.gt_path}/ ...')
    trk_eval.load_data(True)

    eval_category_label_dir = Path(cli.eval_dir) / cli.label / category
    eval_category_label_dir.mkdir(parents=True, exist_ok=True)
    print('eval_category_label_dir', eval_category_label_dir)
    out_path = eval_category_label_dir / 'batch-eval-ab-3d-mot-result.txt'
    evaluate_and_report(trk_eval, cli.label, str(out_path), cli.skip_maximizing_threshold)
    return True


def main() -> None:
    run()  # pragma: no cover
