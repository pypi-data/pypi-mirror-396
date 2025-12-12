"""."""

import pytest

from eval_ab_3d_mot.cli.batch_ab_3d_mot_annotations.cmd_line_factory import AUTO, get_cmd_line
from eval_ab_3d_mot.cli.batch_ab_3d_mot_annotations.cmd_line_object import (
    CmdLineBatchRunAb3dMotAnnotations,
)


def test_category_and_tracking_dir() -> None:
    args = ['car/0001.txt', 'car/0002.txt', '-v', '-c', 'cyclist', '-o', 'my-dir']
    cli = get_cmd_line(args)
    assert isinstance(cli, CmdLineBatchRunAb3dMotAnnotations)
    assert cli.verbosity == 1
    assert cli.category_obj == 'cyclist'
    assert cli.category_prm == AUTO
    assert cli.trk_dir == 'my-dir'
    assert cli.annotations == ['car/0001.txt', 'car/0002.txt']
    assert cli.meta.metric == AUTO
    assert cli.meta.algorithm == AUTO
    assert cli.meta.threshold == pytest.approx(1000.0)
    assert cli.meta.max_age == -1


def test_at_least_one_detection_file_expected() -> None:
    with pytest.raises(SystemExit):
        get_cmd_line([])
