"""."""

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation
from eval_ab_3d_mot.raise_if_sick import raise_if_sick
from eval_ab_3d_mot.stat import Stat
from eval_ab_3d_mot.thresholds import get_thresholds


def evaluate_and_report(
    e: TrackingEvaluation, result_sha: str, filename: str, skip_maximizing_threshold: bool
) -> None:
    raise_if_sick(len(e.ground_truth), len(e.tracker))  # sanity check
    print(f'Loaded {len(e.ground_truth)} sequences.')
    print('Start evaluation...')

    dump = open(filename, 'w+')
    stat_meter = Stat(t_sha=result_sha, cls=e.cls)
    e.compute_3rd_party_metrics()
    e.save_to_stats(dump)
    stat_meter.output()
    summary = stat_meter.get_summary()
    print(summary)  # mail or print the summary.
    if skip_maximizing_threshold:
        return

    # evaluate the mean average metrics
    best_mota, best_threshold = 0, -10000
    e.scores = [score * (1.0 + 1e-12) for score in e.scores]
    threshold_list, recall_list = get_thresholds(e.scores, e.num_gt)
    for threshold_tmp, recall_tmp in zip(threshold_list, recall_list):
        e.reset()
        e.compute_3rd_party_metrics(threshold_tmp, recall_tmp)

        data_tmp = e.get_data_dict()
        stat_meter.update(data_tmp)
        mota_tmp = e.MOTA
        if mota_tmp > best_mota:
            best_threshold = threshold_tmp
            best_mota = mota_tmp
        e.save_to_stats(dump, threshold_tmp, recall_tmp)

    e.reset()
    e.compute_3rd_party_metrics(best_threshold)
    e.save_to_stats(dump)
    stat_meter.output()
    summary = stat_meter.get_summary()
    print(summary)  # mail or print the summary.
    dump.close()
