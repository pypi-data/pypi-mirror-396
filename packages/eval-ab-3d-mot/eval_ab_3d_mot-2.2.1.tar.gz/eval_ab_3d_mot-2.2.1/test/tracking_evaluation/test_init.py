"""."""

import pytest

from eval_ab_3d_mot.core.tracking_evaluation import TrackingEvaluation


def test_init_3d_no_threshold() -> None:
    te = TrackingEvaluation('my-sha', {}, ann_root='kitti-root', res_root='results-root')
    assert len(te.sequence_name) == len(te.n_frames) == te.n_sequences
    assert te.t_path == 'results-root/my-sha/data_0'
    assert te.gt_path == 'kitti-root/label'
    assert te.eval_3diou
    assert not te.eval_2diou
    assert te.max_occlusion == 2
    assert te.min_height == 25
    assert te.n_sample_points == 500
    assert te.min_overlap == pytest.approx(0.25)


def test_init_2d_no_threshold() -> None:
    te = TrackingEvaluation('my-sha', {}, eval_2diou=True, eval_3diou=False)
    assert te.min_overlap == pytest.approx(0.5)


def test_init_no_2d_no_3d_no_threshold() -> None:
    with pytest.raises(AssertionError):
        TrackingEvaluation('my-sha', {}, eval_3diou=False, eval_2diou=False)


def test_given_threshold() -> None:
    te = TrackingEvaluation('my-sha', {}, thres=0.567)
    assert te.eval_3diou
    assert not te.eval_2diou
    assert te.min_overlap == pytest.approx(0.567)
