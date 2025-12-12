"""."""


def bump_num_ignored_pairs(num_ignored_trackers: int, n_ignored_pairs: int) -> int:
    if num_ignored_trackers > 0:
        return n_ignored_pairs + 1
    else:
        return n_ignored_pairs
