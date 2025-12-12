"""."""

from eval_ab_3d_mot.cli.clavia.cmd_line_factory import AUTO, CmdLineRunWithClavIA
from eval_ab_3d_mot.kitti_category import KittiCategory


def test_init(cli: CmdLineRunWithClavIA) -> None:
    assert cli.category_prm == AUTO
    assert cli.category_obj == 'car'


def test_get_annotation_file_names(cli: CmdLineRunWithClavIA) -> None:
    assert cli.get_annotation_file_names() == ['001.txt', '002.txt']


def test_repr(cli: CmdLineRunWithClavIA) -> None:
    ref = (
        'CmdLineBatchRunWithClavIA(category-obj car '
        "parameters(threshold=1000.0 max_age=-1 metric='auto' algorithm='auto'))"
    )
    assert repr(cli) == ref


def test_get_object_category(cli: CmdLineRunWithClavIA) -> None:
    assert cli.get_object_category() == KittiCategory.CAR


def test_get_parameter_category(cli: CmdLineRunWithClavIA) -> None:
    assert cli.get_parameter_category() == KittiCategory.CAR


def test_different_get_parameter_category(cli: CmdLineRunWithClavIA) -> None:
    cli.category_prm = 'pedestrian'
    assert cli.get_parameter_category() == KittiCategory.PEDESTRIAN
