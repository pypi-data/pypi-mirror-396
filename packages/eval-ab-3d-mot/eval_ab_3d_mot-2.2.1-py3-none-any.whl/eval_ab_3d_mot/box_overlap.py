"""."""

from eval_ab_3d_mot.track_data import TrackData


def box_overlap(a: TrackData, b: TrackData, criterion='union'):
    """
    box_overlap computes intersection over union for bbox a and b in KITTI format.
    If the criterion is 'union', overlap = (a inter b) / a union b).
    If the criterion is 'a', overlap = (a inter b) / a, where b should be a dontcare area.
    note that this is different from the iou in dist_metrics.py because this one uses 2D
    box rather than projected 3D boxes to compute overlap
    """

    x1 = max(a.x1, b.x1)
    y1 = max(a.y1, b.y1)
    x2 = min(a.x2, b.x2)
    y2 = min(a.y2, b.y2)

    w = x2 - x1
    h = y2 - y1

    if w <= 0.0 or h <= 0.0:
        return 0.0
    inter = w * h
    aarea = (a.x2 - a.x1) * (a.y2 - a.y1)
    barea = (b.x2 - b.x1) * (b.y2 - b.y1)

    # intersection over union overlap
    if criterion.lower() == 'union':
        o = inter / float(aarea + barea - inter)
    elif criterion.lower() == 'a':
        o = float(inter) / float(aarea)
    else:
        raise TypeError('Unknown type for criterion')
    return o
