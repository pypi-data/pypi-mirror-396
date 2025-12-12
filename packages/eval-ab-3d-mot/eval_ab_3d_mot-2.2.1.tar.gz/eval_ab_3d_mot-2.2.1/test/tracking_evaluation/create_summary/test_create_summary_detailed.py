"""."""

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_create_summary_details(te_sum: TrackingEvaluation) -> None:
    """."""
    summary = te_sum.create_summary_details()
    ref = """=================evaluation: best results with single threshold=================
Multiple Object Tracking Accuracy (MOTA)                                  0.2000
Multiple Object Tracking Precision (MOTP)                                 0.3000
Multiple Object Tracking Accuracy (MOTAL)                                 0.4000
Multiple Object Detection Accuracy (MODA)                                 0.5000
Multiple Object Detection Precision (MODP)                                1.6000

Recall                                                                    0.9000
Precision                                                                 0.8000
F1                                                                        0.6000
False Alarm Rate                                                          0.7000

Mostly Tracked                                                                45
Partly Tracked                                                                56
Mostly Lost                                                                   34

True Positives                                                               456
Ignored True Positives                                                        46
False Positives                                                              126
False Negatives                                                              789
Ignored False Negatives                                                       78
ID-switches                                                                  123
Fragmentations                                                               432

Ground Truth Objects (Total)                                                  95
Ignored Ground Truth Objects                                                  48
Ground Truth Trajectories                                                     51

Tracker Objects (Total)                                                       49
Ignored Tracker Objects                                                       50
Tracker Trajectories                                                          52
================================================================================"""
    assert summary == ref
