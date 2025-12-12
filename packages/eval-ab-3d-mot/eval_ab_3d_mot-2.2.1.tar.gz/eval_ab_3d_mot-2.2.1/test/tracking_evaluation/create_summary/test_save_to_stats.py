"""."""

from io import StringIO

from pytest_mock import MockerFixture

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_save_to_stats_details(te_3d: TrackingEvaluation, mocker: MockerFixture) -> None:
    """."""
    str_io = StringIO()
    mock_details = mocker.patch.object(te_3d, 'create_summary_details')
    mock_details.return_value = 'my summary'
    mock_simple = mocker.patch.object(te_3d, 'create_summary_simple')
    te_3d.save_to_stats(str_io)
    mock_details.assert_called_once()
    mock_simple.assert_not_called()
    assert str_io.getvalue() == 'my summary\n'


def test_save_to_stats_simple(te_3d: TrackingEvaluation, mocker: MockerFixture) -> None:
    """."""
    str_io = StringIO()
    mock_details = mocker.patch.object(te_3d, 'create_summary_details')
    mock_simple = mocker.patch.object(te_3d, 'create_summary_simple')
    mock_simple.return_value = 'my summary'
    te_3d.save_to_stats(str_io, -1.0, 0.5)
    mock_details.assert_not_called()
    mock_simple.assert_called_once_with(-1.0, 0.5)
    assert str_io.getvalue() == 'my summary\n'
