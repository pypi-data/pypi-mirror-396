"""."""

from pathlib import Path

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


@pytest.fixture
def te_dc_is_loose(files_dir: Path) -> TrackingEvaluation:
    te = TrackingEvaluation('my-sha', {'dc-is-loose': 1})
    te.t_path = str(files_dir / 'kitti/tracking/training')
    assert te.load_data(False), 'some file does not exist?'

    te.gt_path = str(files_dir / 'kitti/annotations/training')
    assert te.load_data(True), 'some file does not exist?'
    return te
