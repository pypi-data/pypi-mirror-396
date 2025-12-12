"""."""

from typing import Sequence, Union

from eval_ab_3d_mot.evaluate import evaluate

from .cmd_line import get_cmd_line


def run(args: Union[Sequence[str], None] = None) -> bool:
    cli = get_cmd_line(args)
    eval_3d, eval_2d = cli.get_3d_2d_flags()
    flag = evaluate(
        cli.tracking_sha,
        eval_3d,
        eval_2d,
        cli.get_threshold(),
        cli.ann_root,
        cli.res_root,
        cli.get_seq_lengths_name(),
        cli.classes,
    )
    return flag


def main() -> None:
    run()  # pragma: no cover
