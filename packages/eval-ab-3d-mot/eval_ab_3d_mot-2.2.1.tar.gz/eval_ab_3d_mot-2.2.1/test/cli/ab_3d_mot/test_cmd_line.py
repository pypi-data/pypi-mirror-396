"""."""

from eval_ab_3d_mot.cli.ab_3d_mot.cmd_line import CmdLineRunAb3dMot, get_cmd_line


def test_get_cmd_line() -> None:
    """."""
    # fmt: off
    args = ['detections-in-point-r-cnn-format/cyclist/0000.txt', '-v']
    # fmt: on
    cli = get_cmd_line(args)
    assert isinstance(cli, CmdLineRunAb3dMot)
    assert cli.verbosity == 1
    assert cli.det_file_name == 'detections-in-point-r-cnn-format/cyclist/0000.txt'
    assert cli.trk_file_name == 'tracking-kitti.txt'
