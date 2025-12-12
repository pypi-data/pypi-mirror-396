from typing import Dict, List, Tuple


def filter_low_confidence(
    tracker_id_scores: Dict[int, List[float]], threshold: float
) -> Tuple[Dict[int, float], List[int]]:
    id_average_score = dict()
    to_delete_id = list()
    for track_id, score_list in tracker_id_scores.items():
        average_score = sum(score_list) / len(score_list)
        id_average_score[track_id] = average_score
        if average_score < threshold:  # <= or <
            to_delete_id.append(track_id)
    return id_average_score, to_delete_id
