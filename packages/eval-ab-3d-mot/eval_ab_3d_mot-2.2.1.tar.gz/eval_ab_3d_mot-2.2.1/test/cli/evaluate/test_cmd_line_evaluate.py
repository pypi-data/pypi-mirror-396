"""."""

import pytest

from eval_ab_3d_mot.cli.evaluate.cmd_line import CmdLineEvaluate, get_cmd_line
from eval_ab_3d_mot.core.tracking_evaluation import SEQ_LENGTHS_NAME


def test_cmd_line() -> None:
    cli = CmdLineEvaluate()
    assert cli.get_threshold() is None
    assert cli.get_seq_lengths_name() == SEQ_LENGTHS_NAME
    assert cli.get_3d_2d_flags() == (True, False)


def test_get_cmd_line() -> None:
    """."""
    # fmt: off
    args = ['--seq-names', 'my-name',
            '--seq-lengths', '4446',
            '--classes', 'car',
            '-d', '2',
            '--ann-root', 'evaluation/ann/',
            '--res-root', 'evaluation/res/',
            '-t', '0.123']
    # fmt: on
    cli = get_cmd_line(args)
    assert cli.seq_names == ['my-name']
    assert cli.seq_lengths == [4446]
    assert cli.classes == ['car']
    assert cli.get_threshold() == pytest.approx(0.123)
    assert cli.dimension == 2
