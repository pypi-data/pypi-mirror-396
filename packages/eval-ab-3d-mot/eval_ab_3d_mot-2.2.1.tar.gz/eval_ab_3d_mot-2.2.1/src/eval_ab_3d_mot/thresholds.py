"""."""

from typing import List, Tuple

import numpy as np

from eval_ab_3d_mot.stat import NUM_SAMPLE_POINTS


def get_thresholds(
    scores: List[float], num_gt: int, num_sample_pts=NUM_SAMPLE_POINTS
) -> Tuple[List[float], List[float]]:
    # based on score of true positive to discretize the recall
    # not necessarily have data on all points due to not fully recall the results, all the results point has zero precision
    # compute the recall based on the gt positives

    # scores: the list of scores of the matched true positives

    scores = np.array(scores)
    scores.sort()
    scores: np.ndarray = scores[::-1]
    current_recall = 0
    thresholds = []
    recalls = []
    last_idx = len(scores) - 1
    for i, score in enumerate(scores):
        l_recall = (i + 1) / num_gt
        r_recall = (i + 2) / num_gt if i < last_idx else l_recall
        if (r_recall - current_recall) < (current_recall - l_recall) and i < last_idx:
            continue

        thresholds.append(float(score))
        recalls.append(current_recall)
        current_recall += 1 / (num_sample_pts - 1.0)

    return thresholds[1:], recalls[1:]  # throw the first one with 0 recall
