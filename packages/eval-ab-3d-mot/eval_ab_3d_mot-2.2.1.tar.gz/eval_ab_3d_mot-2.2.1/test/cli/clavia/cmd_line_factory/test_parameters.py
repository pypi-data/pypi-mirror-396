"""."""

import pytest

from eval_ab_3d_mot.cli.clavia.cmd_line_factory import get_cmd_line


def test_parameter_exceptions(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit):
        get_cmd_line(['2.txt', '-a', 'bogus algorithm'])
    with pytest.raises(SystemExit):
        get_cmd_line(['2.txt', '-m', 'bogus metric'])


def test_parameters(capsys: pytest.CaptureFixture) -> None:
    cli1 = get_cmd_line(['2.txt', '-a', 'greedy'])
    assert cli1.meta.algorithm == 'greedy'
    cli2 = get_cmd_line(['2.txt', '-m', 'dist_3d'])
    assert cli2.meta.metric == 'dist_3d'
    cli3 = get_cmd_line(['2.txt', '-x', '6'])
    assert cli3.meta.max_age == 6
    cli4 = get_cmd_line(['2.txt', '-t', '-0.567'])
    assert cli4.meta.threshold == pytest.approx(-0.567)
