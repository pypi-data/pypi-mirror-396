"""."""

from eval_ab_3d_mot.cli.clavia.bin_class_ratios import get_summary


def test_get_summary() -> None:
    summary = get_summary({'tp': 1, 'tn': 2, 'fp': 3, 'fn': 4})
    assert summary == (
        'Confusion matrix TP 1 TN 2 FP 3 FN 4\n'
        '     accuracy 0.300000\n'
        '    precision 0.2500\n'
        '       recall 0.2000\n'
        '     f1-score 0.2222'
    )
