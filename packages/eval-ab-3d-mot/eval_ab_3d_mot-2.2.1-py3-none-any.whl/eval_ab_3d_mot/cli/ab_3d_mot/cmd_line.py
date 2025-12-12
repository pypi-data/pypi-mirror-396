"""."""

from argparse import ArgumentParser
from typing import Sequence

from rich_argparse import RawTextRichHelpFormatter

from eval_ab_3d_mot.cli.common.get_hlp import get_hlp


PROG = 'run-ab-3d-mot'
HLP_OUT = 'File name to store tracking results.'
HLP_ANN = 'Annotations (ground-truth) directory.'
HLP_TS = 'Last timestamp (if there is no annotation file).'


class CmdLineRunAb3dMot:
    def __init__(self) -> None:
        self.verbosity = 0
        self.det_file_name = ''
        self.trk_file_name = 'tracking-kitti.txt'
        self.ann_dir = 'assets/annotations/kitti/training'
        self.last_ts = 0


def get_cmd_line(args: Sequence[str]) -> CmdLineRunAb3dMot:
    cli = CmdLineRunAb3dMot()
    parser = ArgumentParser(
        PROG, f'{PROG} <det_file> [OPTIONS]', formatter_class=RawTextRichHelpFormatter
    )
    parser.add_argument('det_file_name', help='File name with detections.')
    parser.add_argument('--verbosity', '-v', action='count', help='Script verbosity.')
    parser.add_argument('--trk-file-name', '-o', help=get_hlp(HLP_OUT, cli.trk_file_name))
    parser.add_argument('--ann-dir', '-a', help=get_hlp(HLP_ANN, cli.ann_dir))
    parser.add_argument('--last-ts', type=int, help=get_hlp(HLP_TS, cli.last_ts))
    parser.parse_args(args, namespace=cli)
    return cli
