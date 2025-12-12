"""."""

from argparse import ArgumentParser
from typing import Dict, Sequence, Tuple, Union

from rich_argparse import RawTextRichHelpFormatter

from eval_ab_3d_mot.cli.common.get_hlp import get_hlp


PROG = 'eval-ab-3d-mot'
HLP_SHA = 'Subfolder to lookup the results of tracking.'
HLP_THR = 'Threshold for dropping low confidence annotations.'
HLP_LEN = 'Number of frames for each of the sequences.'
HLP_ANN = 'Root folder with KITTI annotations.'
HLP_RES = 'Root folder with tracking results.'
HLP_SEQ_NAMES = 'Names of sequences to evaluate.'
HLP_CLS = 'Classes to evaluate.'


class CmdLineEvaluate:
    def __init__(self) -> None:
        self.tracking_sha = 'my-sha'
        self.dimension = 3
        self.threshold: str = 'none'
        self.ann_root = 'kitti/annotations'
        self.res_root = 'results/'
        self.seq_names = [
            '0001',
            '0006',
            '0008',
            '0010',
            '0012',
            '0013',
            '0014',
            '0015',
            '0016',
            '0018',
            '0019',
        ]
        self.seq_lengths = [448, 271, 391, 295, 79, 341, 107, 377, 210, 340, 1060]
        self.classes = ['car', 'pedestrian', 'cyclist']

    def get_3d_2d_flags(self) -> Tuple[bool, bool]:
        eval_3d = False
        eval_2d = False
        if self.dimension == 3:
            eval_3d = True
        elif self.dimension == 2:
            eval_2d = True
        return eval_3d, eval_2d

    def get_seq_lengths_name(self) -> Dict[str, int]:
        return {name: ln for name, ln in zip(self.seq_names, self.seq_lengths)}

    def get_threshold(self) -> Union[float, None]:
        return None if self.threshold.lower() == 'none' else float(self.threshold)


def get_cmd_line(args: Sequence[str]) -> CmdLineEvaluate:
    cli = CmdLineEvaluate()
    parser = ArgumentParser(PROG, f'{PROG} [OPTIONS]', formatter_class=RawTextRichHelpFormatter)
    parser.add_argument('--tracking-sha', help=get_hlp(HLP_SHA, cli.tracking_sha))
    parser.add_argument('--threshold', '-t', type=str, help=get_hlp(HLP_THR, cli.threshold))
    hlp_d = get_hlp('2D or 3D evaluation?', cli.dimension)
    parser.add_argument('--dimension', '-d', choices=(2, 3), type=int, help=hlp_d)
    parser.add_argument('--ann-root', help=get_hlp(HLP_ANN, cli.ann_root))
    parser.add_argument('--res-root', help=get_hlp(HLP_RES, cli.res_root))
    parser.add_argument('--seq-names', nargs='*', help=get_hlp(HLP_SEQ_NAMES, cli.seq_names))
    parser.add_argument(
        '--seq-lengths', nargs='*', type=int, help=get_hlp(HLP_LEN, cli.seq_lengths)
    )
    cls_choice = ['car', 'pedestrian', 'cyclist']
    hlp_cls = get_hlp(HLP_CLS, cli.classes)
    parser.add_argument('--classes', nargs='*', choices=cls_choice, help=hlp_cls)
    parser.parse_args(args, namespace=cli)
    return cli
