"""."""

import pytest

from eval_ab_3d_mot.stat import NUM_SAMPLE_POINTS, Stat


@pytest.fixture
def stat() -> Stat:
    return Stat('sha', 'cyclist')


def test_stat_init(stat: Stat) -> None:
    assert stat.mota == pytest.approx(0.0)
    assert stat.mota_list == []
    assert stat.t_sha == 'sha'
    assert stat.cls == 'cyclist'


def test_stat_update(stat: Stat) -> None:
    data = {
        'mota': 0.1,
        'motp': 0.2,
        'F1': 0.3,
        'precision': 0.4,
        'fp': 5,
        'fn': 6,
        'sMOTA': 0.7,
        'recall': 0.87,
    }
    stat.update(data)
    assert stat.mota == pytest.approx(0.1)
    assert len(stat.mota_list) == 1
    data = {
        'mota': 0.11,
        'motp': 0.2,
        'F1': 0.3,
        'precision': 0.4,
        'fp': 5,
        'fn': 6,
        'sMOTA': 0.7,
        'recall': 0.87,
    }
    stat.update(data)
    assert stat.mota == pytest.approx(0.21)
    assert len(stat.mota_list) == 2


def test_output(stat: Stat) -> None:
    data = {
        'mota': 0.1,
        'motp': 0.2,
        'F1': 0.3,
        'precision': 0.4,
        'fp': 5,
        'fn': 6,
        'sMOTA': 0.7,
        'recall': 0.87,
    }
    stat.update(data)
    stat.output()
    assert stat.sAMOTA == pytest.approx(0.7 / (NUM_SAMPLE_POINTS - 1))
    assert stat.amota == pytest.approx(0.1 / (NUM_SAMPLE_POINTS - 1))
    assert stat.amotp == pytest.approx(0.2 / (NUM_SAMPLE_POINTS - 1))


def test_get_summary(stat: Stat) -> None:
    data = {
        'mota': 0.1,
        'motp': 0.2,
        'F1': 0.3,
        'precision': 0.4,
        'fp': 5,
        'fn': 6,
        'sMOTA': 0.7,
        'recall': 0.87,
    }
    stat.update(data)
    stat.output()
    summary = stat.get_summary()
    ref = """========================evaluation: average over recall=========================
 sAMOTA  AMOTA  AMOTP 
0.0175 0.0025 0.0050
================================================================================"""
    assert summary == ref
