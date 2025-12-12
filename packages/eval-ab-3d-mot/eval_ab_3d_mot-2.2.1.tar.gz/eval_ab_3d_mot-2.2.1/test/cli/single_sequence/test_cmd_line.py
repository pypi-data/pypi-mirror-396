"""."""

from pathlib import Path

import pytest

from eval_ab_3d_mot.cli.single_sequence.cmd_line import CmdLineSingleSequence, get_cmd_line


def test_cmd_line_get_ann_path() -> None:
    cli = CmdLineSingleSequence()
    cli.ann_file_name = 'annotations/0000.txt'
    assert isinstance(cli.get_ann_path(), Path)

    cli.ann_file_name = 'annotations/0000.csv'
    with pytest.raises(ValueError):
        cli.get_ann_path()


def test_get_cmd_line() -> None:
    args = ['annotations/0000.txt', '-v']
    cli = get_cmd_line(args)
    assert isinstance(cli, CmdLineSingleSequence)
    assert cli.verbosity == 1
    assert cli.ann_file_name == 'annotations/0000.txt'
    assert cli.trk_file_name == 'tracking-kitti.txt'
