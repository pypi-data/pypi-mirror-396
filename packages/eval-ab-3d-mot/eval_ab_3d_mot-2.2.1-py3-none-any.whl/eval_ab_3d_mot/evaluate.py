"""."""

import os

from typing import Dict, Sequence, Union

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation

from .evaluate_and_report import evaluate_and_report


def evaluate(
    result_sha: str,
    eval_3diou: bool,
    eval_2diou: bool,
    threshold: Union[float, None],
    ann_root: str,
    res_root: str,
    seq_lengths_name: Dict[str, int],
    target_classes: Sequence[str],
) -> bool:
    """
    Entry point for evaluation, will load the data and start evaluation for
    CAR and PEDESTRIAN if available.
    """

    classes = []
    for c in target_classes:
        e = TrackingEvaluation(
            result_sha,
            seq_lengths_name,
            ann_root=ann_root,
            res_root=res_root,
            cls=c,
            eval_3diou=eval_3diou,
            eval_2diou=eval_2diou,
            thres=threshold,
        )
        # load tracker data and check provided classes
        try:
            e.load_data(is_ground_truth=False)
            print('Loading Results - Success')
            print('Evaluate Object Class: %s' % c.upper())
            classes.append(c)
        except IOError as exception:  # noqa: E722
            print('Feel free to contact us (lenz@kit.edu), if you receive this error message:')
            print('   Caught exception while loading result data.')
            print(exception)
            break
        e.load_data(is_ground_truth=True)  # load ground-truth data for this class
        suffix = 'eval_3d' if eval_3diou else 'eval_2d'
        filename = os.path.join(e.t_path, '../summary_%s_average_%s.txt' % (c, suffix))
        evaluate_and_report(e, result_sha, filename, False)

    # finish
    if len(classes) == 0:
        print('The uploaded results could not be evaluated. Check for format errors.')
        return False
    print('Thank you for participating in our benchmark!')
    return True
