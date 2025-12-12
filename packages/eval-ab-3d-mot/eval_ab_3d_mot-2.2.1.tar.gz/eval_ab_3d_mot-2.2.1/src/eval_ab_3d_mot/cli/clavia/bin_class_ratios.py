"""."""

from typing import Dict

from binary_classification_ratios import BinaryClassificationRatios


def get_summary(cm_dct: Dict[str, int]) -> str:
    ratios = BinaryClassificationRatios(**cm_dct)
    ratios.summary.accuracy_fmt = '.6f'
    ratios.summary.fmt = '.4f'
    return ratios.get_summary()
