"""."""


def raise_if_negative_fp(
    fp: int,
    num_tracks: int,
    tp: int,
    n_ignored_tracker: int,
    n_ignored_tp: int,
    n_ignored_pairs: int,
) -> None:
    if fp < 0:
        print(fp, num_tracks, tp, n_ignored_tracker, n_ignored_tp, n_ignored_pairs)
        raise RuntimeError('Something went wrong! FP is negative')


def raise_if_negative_fn(
    fn: int, num_gt: int, num_matches, ignored_fn: int, n_ignored_pairs: int
) -> None:
    if fn < 0:
        print(fn, num_gt, num_matches, ignored_fn, n_ignored_pairs)
        raise RuntimeError('Something went wrong! FN is negative')


def raise_if_negative_tp(tp: int, n_ignored_tp: int) -> None:
    if tp < 0:
        print(tp, n_ignored_tp)
        raise RuntimeError('Something went wrong! TP is negative')  # impossible?
