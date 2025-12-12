"""."""

import pytest

from eval_ab_3d_mot.cli.batch_eval_ab_3d_mot.cmd_line import get_cmd_line


def test_category_and_tracking_dir() -> None:
    # fmt: off
    args = ['car/0001.txt', 'car/0002.txt',
            '-v',
            '-c', 'cyclist',
            '-i', 'my-dir',
            '-l', 'my-custom-label']
    # fmt: on
    cli = get_cmd_line(args)
    assert cli.verbosity == 1
    assert cli.category == 'cyclist'
    assert cli.trk_dir == 'my-dir'
    assert cli.annotations == ['car/0001.txt', 'car/0002.txt']
    assert cli.label == 'my-custom-label'


def test_at_least_one_detection_file_expected() -> None:
    with pytest.raises(SystemExit):
        get_cmd_line([])
