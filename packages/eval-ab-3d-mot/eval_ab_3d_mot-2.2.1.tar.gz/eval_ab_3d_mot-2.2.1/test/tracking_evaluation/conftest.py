"""."""

from pathlib import Path

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


@pytest.fixture
def te(files_dir: Path) -> TrackingEvaluation:
    tracking_evaluation = TrackingEvaluation('my-sha', {}, ann_root='kitti-root')
    tracking_evaluation.t_path = str(files_dir / 'kitti/tracking/training')
    return tracking_evaluation


@pytest.fixture
def te_3d(files_dir: Path) -> TrackingEvaluation:
    te = TrackingEvaluation('my-sha', {'0012': 79})
    te.t_path = str(files_dir / 'kitti/tracking/training')
    assert te.load_data(False)

    te.gt_path = str(files_dir / 'kitti/annotations/training')
    assert te.load_data(True)
    assert te.eval_2d
    assert te.eval_3d
    return te


@pytest.fixture
def te_2d(files_dir: Path) -> TrackingEvaluation:
    te = TrackingEvaluation('my-sha', {'0012': 79}, eval_2diou=True, eval_3diou=False)
    te.t_path = str(files_dir / 'kitti/tracking/training')
    assert te.load_data(False)

    te.gt_path = str(files_dir / 'kitti/annotations/training')
    assert te.load_data(True)
    assert te.eval_2d
    assert te.eval_3d
    return te
