"""."""

from pytest_mock import MockerFixture

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_load_data_gt(te: TrackingEvaluation, mocker: MockerFixture) -> None:
    """."""
    mock_load_data = mocker.patch.object(te, '_load_data')
    assert te.load_data(is_ground_truth=True)
    gt_path_ref = 'kitti-root/label'
    mock_load_data.assert_called_once_with(gt_path_ref, 'car', True)


def test_load_data_tracking(te: TrackingEvaluation, mocker: MockerFixture) -> None:
    """."""
    mock_load_data = mocker.patch.object(te, '_load_data')
    assert te.load_data(False)
    mock_load_data.assert_called_once_with(te.t_path, 'car', False)
