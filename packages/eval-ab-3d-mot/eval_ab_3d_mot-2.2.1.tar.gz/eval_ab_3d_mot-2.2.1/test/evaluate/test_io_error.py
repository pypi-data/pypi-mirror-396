"""."""

from eval_ab_3d_mot.evaluate import evaluate


def test_results_root_does_not_exist() -> None:
    """."""
    flag = evaluate(
        'my-sha',
        True,
        False,
        0.5,
        'ann-root-not-important',
        'bogus-result-root',
        {'0001': 4},
        ('cyclist',),
    )
    assert not flag
