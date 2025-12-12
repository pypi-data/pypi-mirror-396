"""."""

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_create_summary_simple(te_sum: TrackingEvaluation) -> None:
    """."""
    summary = te_sum.create_summary_simple(2.0, 0.234)
    ref = """=========evaluation with confidence threshold 2.000000, recall 0.234000=========
 sMOTA   MOTA   MOTP    MT     ML     IDS  FRAG    F1   Prec  Recall  FAR     TP    FP    FN
0.1000 0.2000 0.3000 45.0000 34.0000   123   432 0.6000 0.8000 0.9000 0.7000   456   126   789
================================================================================"""
    assert summary == ref
