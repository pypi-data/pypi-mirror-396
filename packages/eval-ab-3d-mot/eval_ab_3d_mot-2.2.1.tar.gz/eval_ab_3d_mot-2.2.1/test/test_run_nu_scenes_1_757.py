"""."""

from pathlib import Path

import numpy as np

from association_quality_clavia import AssociationQuality
from binary_classification_ratios import BinaryClassificationRatios
from pure_ab_3d_mot.str_const import ANN_IDS, DETS, INFO
from pure_ab_3d_mot.tracker import Ab3DMot

from eval_ab_3d_mot.cli.common.ab_3d_mot_parameters import fill_r_cnn_opt_param
from eval_ab_3d_mot.kitti_category import KittiCategory


def test_run_1_757(files_dir: Path) -> None:
    """."""
    f_path = files_dir / 'annotation_task_1_757.csv'
    ann = np.genfromtxt(f_path, 'float32', '#', ',', 1, usecols=[2, 3, 4, 5, 6, 7, 8])
    t_id = np.genfromtxt(f_path, int, '#', ',', 1, usecols=[0, 1])
    time_stamps = np.unique(t_id[:, 0])

    to_kitti = 5, 4, 3, 0, 1, 2, 6
    tracker = Ab3DMot()
    fill_r_cnn_opt_param(KittiCategory.CAR, tracker)
    classifier = AssociationQuality()  # Classifier into TP, FP, FN, TN
    for ts_num, time_stamp in enumerate(time_stamps):
        time_stamp_mask = np.where(t_id[:, 0] == time_stamp)
        ids_r = t_id[time_stamp_mask, 1].T
        det_r = ann[time_stamp_mask][:, to_kitti]
        det_dct = {DETS: det_r, INFO: ids_r, ANN_IDS: ids_r.reshape(-1)}
        tracker.track(det_dct)
        for track_num, track in enumerate(tracker.trackers):
            is_det_supplied = track.ann_id in ids_r
            classifier.classify(track.ann_id, track.upd_id, is_det_supplied)

    confusion_mat = classifier.get_confusion_matrix()
    ratios = BinaryClassificationRatios(**confusion_mat)
    print(ratios.get_summary())
    ratios.assert_min(0.78366, 1.000, 0.7789)
    assert len(tracker.trackers) == 13
