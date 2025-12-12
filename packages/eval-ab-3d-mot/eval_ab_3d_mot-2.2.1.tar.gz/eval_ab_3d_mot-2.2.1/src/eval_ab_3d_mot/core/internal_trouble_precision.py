"""."""

from typing import Sequence, Tuple


def is_trouble(
    tp: int,
    fp: int,
    n_ignored_tp: int,
    n_ignored_tracker: int,
    n_ignored_pairs: int,
    num_frames: int,
) -> bool:
    return tp + fp + n_ignored_tp + n_ignored_tracker - n_ignored_pairs != num_frames


def raise_trouble(
    seq_idx: int,
    f: int,
    num_frames: int,
    tp: int,
    fp: int,
    association_matrix: Sequence[Tuple[int, int]],
) -> None:
    print(seq_idx, f, num_frames, tp, fp)
    print(len(association_matrix), association_matrix)
    raise RuntimeError('Something went wrong! nTracker is not TP+FP')


def raise_if_trouble_fp(
    tp: int,
    fp: int,
    n_ignored_tp: int,
    n_ignored_tracker: int,
    n_ignored_pairs: int,
    num_frames: int,
    seq_idx: int,
    f: int,
    association_matrix: Sequence[Tuple[int, int]],
) -> None:
    if is_trouble(tp, fp, n_ignored_tp, n_ignored_tracker, n_ignored_pairs, num_frames):
        raise_trouble(seq_idx, f, num_frames, tp, fp, association_matrix)
