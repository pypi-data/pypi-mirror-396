"""."""

from argparse import ArgumentParser
from pathlib import Path
from typing import Sequence

from rich_argparse import RawTextRichHelpFormatter

from eval_ab_3d_mot.cli.common.get_hlp import get_hlp


PROG = 'eval-ab-3d-mot-single-seq'
HLP_INP = 'File name to read tracking results.'


class CmdLineSingleSequence:
    def __init__(self) -> None:
        self.verbosity = 0
        self.trk_file_name = 'tracking-kitti.txt'
        self.ann_file_name = ''

    def get_ann_path(self) -> Path:
        ann_path = Path(self.ann_file_name)
        if ann_path.suffix != '.txt':
            raise ValueError('The suffix (extension) should be .txt')
        return ann_path


def get_cmd_line(args: Sequence[str]) -> CmdLineSingleSequence:
    cli = CmdLineSingleSequence()
    parser = ArgumentParser(PROG, f'{PROG} [OPTIONS]', formatter_class=RawTextRichHelpFormatter)
    parser.add_argument('ann_file_name', help='File name with annotations.')
    parser.add_argument('--verbosity', '-v', action='count', help='Script verbosity.')
    parser.add_argument('--trk-file-name', '-i', help=get_hlp(HLP_INP, cli.trk_file_name))
    parser.parse_args(args, namespace=cli)
    return cli
