"""."""

import pytest

from eval_ab_3d_mot.cli.batch_ab_3d_mot_annotations.cmd_line_object import (
    CmdLineBatchRunAb3dMotAnnotations,
)
from eval_ab_3d_mot.kitti_category import KittiCategory


@pytest.fixture()
def cli() -> CmdLineBatchRunAb3dMotAnnotations:
    cli = CmdLineBatchRunAb3dMotAnnotations()
    cli.annotations = ['car/002.txt', 'car/001.txt']
    return cli


def test_get_annotation_file_names(cli: CmdLineBatchRunAb3dMotAnnotations) -> None:
    assert cli.get_annotation_file_names() == ['car/001.txt', 'car/002.txt']


def test_get_object_category(cli: CmdLineBatchRunAb3dMotAnnotations) -> None:
    assert cli.get_object_category() == KittiCategory.CAR


def test_get_parameter_category(cli: CmdLineBatchRunAb3dMotAnnotations) -> None:
    assert cli.get_parameter_category() == KittiCategory.CAR
    cli.category_prm = 'cyclist'
    assert cli.get_parameter_category() == KittiCategory.CYCLIST
