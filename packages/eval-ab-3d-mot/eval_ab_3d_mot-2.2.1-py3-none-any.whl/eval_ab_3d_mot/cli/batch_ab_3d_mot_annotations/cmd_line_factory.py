"""."""

from argparse import ArgumentParser
from typing import Sequence

from pure_ab_3d_mot.dist_metrics import MetricKind
from pure_ab_3d_mot.matching import MatchingAlgorithm
from rich_argparse import RawTextRichHelpFormatter

from eval_ab_3d_mot.cli.common.get_hlp import get_hlp
from eval_ab_3d_mot.cli.common.init_coinciding_attrs import init_coinciding_attrs
from eval_ab_3d_mot.cli.common.tracker_meta import AUTO
from eval_ab_3d_mot.kitti_category import KittiCategory

from .cmd_line_object import CmdLineBatchRunAb3dMotAnnotations


PROG = 'batch-run-ab-3d-mot-annotations'
HLP_OUT = 'Directory to store tracking results.'
DEF_POLICY = 'If not given the category-dependent optimal will be used.'
HLP_CAT_OBJ = 'Category of the objects selected for tracking.'
HLP_THR = 'Association threshold.'
HLP_ALG = 'Association algorithm.'
HLP_MET = 'Association metric.'
HLP_MAX = 'Maximal number of steps without association.'
HLP_CAT_PRM = 'Category of to selected tracker parameters.'


def get_cmd_line(args: Sequence[str]) -> CmdLineBatchRunAb3dMotAnnotations:
    cli = CmdLineBatchRunAb3dMotAnnotations()
    parser = ArgumentParser(
        PROG, f'{PROG} <annotations+> [OPTIONS]', formatter_class=RawTextRichHelpFormatter
    )
    parser.add_argument('annotations', nargs='+', help='KITTI annotation files.')
    parser.add_argument('--trk-dir', '-o', help=get_hlp(HLP_OUT, cli.trk_dir))
    cc_oo = tuple(c.value for c in KittiCategory)
    hlp_c_obj = get_hlp(HLP_CAT_OBJ, cli.category_obj)
    parser.add_argument('--category-obj', '-c', choices=cc_oo, help=hlp_c_obj)
    hlp_c_prm = get_hlp(HLP_CAT_PRM, cli.category_prm + ' 🛈 objects category')
    cc_pp = tuple(c.value for c in KittiCategory) + (AUTO,)
    parser.add_argument('--category-prm', '-p', choices=cc_pp, help=hlp_c_prm)
    parser.add_argument('--verbosity', '-v', action='count', help='Script verbosity.')
    parser.add_argument('--threshold', '-t', type=float, help=get_hlp(HLP_THR, DEF_POLICY))
    parser.add_argument('--max-age', '-x', type=int, help=get_hlp(HLP_MAX, DEF_POLICY))
    aa = (MatchingAlgorithm.HUNGARIAN.value, MatchingAlgorithm.GREEDY.value) + (AUTO,)
    parser.add_argument('--algorithm', '-a', choices=aa, help=get_hlp(HLP_ALG, DEF_POLICY))
    mm = tuple(c.value for c in MetricKind if c != MetricKind.UNKNOWN) + (AUTO,)
    parser.add_argument('--metric', '-m', choices=mm, help=get_hlp(HLP_MET, DEF_POLICY))
    ns = parser.parse_args(args)
    init_coinciding_attrs(ns, cli)
    init_coinciding_attrs(ns, cli.meta)
    if cli.verbosity > 0:
        print(cli)

    return cli
