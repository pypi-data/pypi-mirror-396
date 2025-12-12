"""."""

from pathlib import Path

from pytest import CaptureFixture

from eval_ab_3d_mot.cli.clavia.clavia_main import run


def test_run(files_dir: Path) -> None:
    summary = run([str(files_dir / 'kitti/annotations/training/0001.txt'), '-c', 'pedestrian'])
    ref = """Confusion matrix TP 112 TN 9 FP 0 FN 0
     accuracy 1.000000
    precision 1.0000
       recall 1.0000
     f1-score 1.0000"""
    assert summary == ref


def test_verbose_run(files_dir: Path, capsys: CaptureFixture) -> None:
    run([str(files_dir / 'kitti/annotations/training/0001.txt'), '-c', 'pedestrian', '-vv'])
    ref = """Ab3DMot (AB3DMOT) parameters
    algorithm MatchingAlgorithm.GREEDY
       metric MetricKind.GIOU_3D
    threshold -0.4
     min_hits 1
      max_age 4"""
    fix_stdout = capsys.readouterr().out
    assert ref in fix_stdout
    assert 'Tracking for ' in fix_stdout
    assert '0001.txt' in fix_stdout
