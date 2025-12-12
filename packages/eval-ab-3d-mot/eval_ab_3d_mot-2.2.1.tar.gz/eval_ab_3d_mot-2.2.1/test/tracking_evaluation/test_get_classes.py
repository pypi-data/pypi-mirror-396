"""."""

from eval_ab_3d_mot.core.tracking_evaluation import get_classes


def test_get_classes() -> None:
    """."""
    assert get_classes('car') == ['car', 'van', 'dontcare']
    assert get_classes('pedestrian') == ['pedestrian', 'person_sitting', 'dontcare']
    assert get_classes('cyclist') == ['cyclist', 'dontcare']
    assert get_classes('my-class') == ['my-class', 'dontcare']
