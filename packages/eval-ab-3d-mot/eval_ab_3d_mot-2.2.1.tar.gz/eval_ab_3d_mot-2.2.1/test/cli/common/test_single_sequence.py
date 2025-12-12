"""."""

from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.r_cnn_adaptor import RCnnAdaptor
from eval_ab_3d_mot.cli.common.single_sequence import get_tracking_result


def test_get_tracking_result(adaptor: RCnnAdaptor, tracker: Ab3DMot) -> None:
    """."""
    result = get_tracking_result(adaptor, tracker, 4)
    assert len(result) == 11
