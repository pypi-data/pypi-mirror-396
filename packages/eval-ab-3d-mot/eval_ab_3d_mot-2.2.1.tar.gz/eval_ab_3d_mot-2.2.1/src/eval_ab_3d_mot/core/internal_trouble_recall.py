"""."""

from typing import Sequence, Tuple


def raise_if_trouble_fn(
    tmptp: int,
    tmpfn: int,
    num_gt: int,
    ignoredfn: int,
    nignoredtp: int,
    tmpfp: int,
    seq_idx: int,
    f: int,
    matches: Sequence[Tuple[int, int]],
) -> None:
    if tmptp + tmpfn != num_gt - ignoredfn - nignoredtp:
        print('seqidx', seq_idx)
        print('frame ', f)
        print('TP    ', tmptp)
        print('FN    ', tmpfn)
        print('FP    ', tmpfp)
        print('nGT   ', num_gt)
        print('nAss  ', len(matches))
        print('ign GT', ignoredfn)
        print('ign TP', nignoredtp)
        raise RuntimeError('Something went wrong! nGroundtruth is not TP+FN')
