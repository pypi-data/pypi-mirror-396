"""."""

from argparse import ArgumentParser
from pathlib import Path
from typing import List, Sequence

from rich_argparse import RawTextRichHelpFormatter

from eval_ab_3d_mot.cli.common.get_hlp import get_hlp
from eval_ab_3d_mot.cli.common.kitti_category import CATEGORIES, HLP_CATEGORY
from eval_ab_3d_mot.kitti_category import KittiCategory


PROG = 'batch-eval-ab-3d-mot'
HLP_OUT = 'Directory to store evaluation results.'
HLP_TRK = 'The root directory with tracking results.'
HLP_LBL = 'A custom label to distinguish this evaluation.'
HLP_THR = 'Threshold used for association in MOTA / ClearMOT.'
HLP_SMR = (
    'Skip maximizing association threshold.Recommended when evaluating the tracking of annotations.'
)


class CmdLineBatchEvalAb3dMot:
    def __init__(self) -> None:
        self.verbosity = 0
        self.annotations: List[str] = []
        self.eval_dir = 'evaluation-kitti'
        self.trk_dir = 'tracking-kitti'
        self.category = CATEGORIES[0]
        self.label = 'batch-eval'
        self.threshold: float = 0.25
        self.skip_maximizing_threshold: bool = False

    def get_category(self) -> KittiCategory:
        return KittiCategory(self.category)

    def get_gt_path(self) -> str:
        return str(Path(self.get_annotation_file_names()[0]).parent)

    def get_trk_path(self) -> str:
        return str(Path(self.trk_dir) / self.get_category().value)

    def get_annotation_file_names(self) -> List[str]:
        if len(set(Path(d).parent for d in self.annotations)) > 1:
            raise ValueError('I expect the annotation files to be in the same directory.')
        return sorted(self.annotations)


def get_cmd_line(args: Sequence[str]) -> CmdLineBatchEvalAb3dMot:
    cli = CmdLineBatchEvalAb3dMot()
    parser = ArgumentParser(
        PROG, f'{PROG} <annotation files> [OPTIONS]', formatter_class=RawTextRichHelpFormatter
    )
    parser.add_argument('annotations', nargs='+', help='Annotations files.')
    parser.add_argument('--trk-dir', '-i', help=get_hlp(HLP_TRK, cli.trk_dir))
    parser.add_argument('--eval-dir', '-o', help=get_hlp(HLP_OUT, cli.eval_dir))
    parser.add_argument('--label', '-l', help=get_hlp(HLP_LBL, cli.label))
    parser.add_argument('--threshold', '-t', type=float, help=get_hlp(HLP_THR, cli.threshold))
    parser.add_argument(
        '--skip-maximizing-threshold',
        '-ann',
        action='store_true',
        help=get_hlp(HLP_SMR, cli.skip_maximizing_threshold),
    )
    parser.add_argument(
        '--category', '-c', choices=CATEGORIES, help=get_hlp(HLP_CATEGORY, cli.category)
    )
    parser.add_argument('--verbosity', '-v', action='count', help='Script verbosity.')
    parser.parse_args(args, namespace=cli)
    return cli
