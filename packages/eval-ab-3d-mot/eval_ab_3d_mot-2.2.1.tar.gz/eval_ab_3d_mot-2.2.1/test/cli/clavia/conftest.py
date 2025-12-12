"""."""

import pytest

from eval_ab_3d_mot.cli.clavia.cmd_line_factory import CmdLineRunWithClavIA


@pytest.fixture()
def cli() -> CmdLineRunWithClavIA:
    cli = CmdLineRunWithClavIA()
    cli.annotations = ['002.txt', '001.txt']
    return cli
