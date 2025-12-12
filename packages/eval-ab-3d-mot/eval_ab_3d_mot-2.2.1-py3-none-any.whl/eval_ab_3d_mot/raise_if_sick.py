"""."""


def raise_if_sick(num_gt: int, num_tr: int) -> None:
    if num_gt != num_tr:
        raise RuntimeError(
            'The uploaded data does not provide every sequence: %d vs %d' % (num_gt, num_tr)
        )
