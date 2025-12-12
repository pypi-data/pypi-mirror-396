"""."""

import pytest

from eval_ab_3d_mot.cli.batch_eval_ab_3d_mot.cmd_line import CmdLineBatchEvalAb3dMot


@pytest.fixture()
def cli() -> CmdLineBatchEvalAb3dMot:
    cli = CmdLineBatchEvalAb3dMot()
    cli.annotations = ['002.txt', '001.txt']
    return cli


def test_get_annotations(cli: CmdLineBatchEvalAb3dMot) -> None:
    assert cli.get_annotation_file_names() == ['001.txt', '002.txt']
    cli.annotations = ['car/002.txt', 'pedestrian/001.txt']
    with pytest.raises(ValueError):
        cli.get_annotation_file_names()
