"""."""

import copy
import math
import os

from collections import defaultdict
from typing import Dict, List, Union

from munkres import Munkres
from pure_ab_3d_mot.dist_metrics import MetricKind
from pure_ab_3d_mot.iou import iou

from eval_ab_3d_mot.box_overlap import box_overlap
from eval_ab_3d_mot.track_data import TrackData

from .bump_num_ignored_pairs import bump_num_ignored_pairs
from .filter_low_confidence import filter_low_confidence
from .internal_trouble_precision import raise_if_trouble_fp
from .internal_trouble_recall import raise_if_trouble_fn
from .internal_troubles_negative import (
    raise_if_negative_fn,
    raise_if_negative_fp,
    raise_if_negative_tp,
)
from .print_entry import print_entry


SEQ_LENGTHS_NAME = {
    '0001': 448,
    '0006': 271,
    '0008': 391,
    '0010': 295,
    '0012': 79,
    '0013': 341,
    '0014': 107,
    '0015': 377,
    '0016': 210,
    '0018': 340,
    '0019': 1060,
}


def get_classes(cls: str) -> List[str]:
    # classes that should be loaded (ignored neighboring classes)
    cls_lower = cls.lower()
    classes = [cls_lower]
    if cls_lower == 'car':
        classes.append('van')
    elif cls_lower == 'pedestrian':
        classes.append('person_sitting')
    classes.append('dontcare')
    return classes


class TrackingEvaluation(object):
    """tracking statistics (CLEAR MOT, id-switches, fragments, ML/PT/MT, precision/recall)
    MOTA   - Multi-object tracking accuracy in [0,100]
    MOTP   - Multi-object tracking precision in [0,100] (3D) / [td,100] (2D)
    MOTAL  - Multi-object tracking accuracy in [0,100] with log10(id-switches)

    id-switches - number of id switches
    fragments   - number of fragments

    MT, PT, ML - number of mostly tracked, partially tracked and mostly lost trajectories

    recall         - recall = percentage of detected targets
    precision      - precision = percentage of correctly detected targets
    FAR            - number of false alarms per frame
    false positives - number of false positives (FP)
    missed         - number of missed targets (FN)
    """

    def __init__(
        self,
        t_sha: str,
        seq_lengths_name: Dict[str, int],
        ann_root: str = './scripts/KITTI',
        res_root: str = './results/KITTI',
        max_truncation: int = 0,
        min_height: int = 25,
        max_occlusion: int = 2,
        cls: str = 'car',
        eval_3diou: bool = True,
        eval_2diou: bool = False,
        thres: Union[float, None] = None,
    ) -> None:
        self.n_frames: List[int] = list(seq_lengths_name.values())
        self.sequence_name = list(seq_lengths_name)
        self.n_sequences = len(self.sequence_name)
        self.cls = cls  # class to evaluate, i.e. pedestrian or car

        # data and parameter
        self.gt_path = os.path.join(ann_root, 'label')
        self.t_sha = t_sha
        self.t_path = os.path.join(res_root, t_sha, 'data_0')

        # statistics and numbers for evaluation
        self.n_gt = (
            0  # number of ground truth detections minus ignored false negatives and true positives
        )
        self.n_igt = 0  # number of ignored ground truth detections
        self.n_gts = []  # number of ground truth detections minus ignored false negatives and true positives PER SEQUENCE
        self.n_igts = []  # number of ground ignored truth detections PER SEQUENCE
        self.n_gt_trajectories = 0
        self.n_gt_seq = []
        self.n_tr = 0  # number of tracker detections minus ignored tracker detections
        self.n_trs = []  # number of tracker detections minus ignored tracker detections PER SEQUENCE
        self.n_itr = 0  # number of ignored tracker detections
        self.n_itrs = []  # number of ignored tracker detections PER SEQUENCE
        self.n_igttr = 0  # number of ignored ground truth detections where the corresponding associated tracker detection is also ignored
        self.n_tr_trajectories = 0
        self.n_tr_seq = []
        self.MOTA = 0
        self.MOTP = 0
        self.MOTAL = 0
        self.MODA = 0
        self.MODP: Union[str, float] = 0.0
        self.MODP_t = []
        self.sMOTA = 0.0
        self.recall = 0
        self.precision = 0
        self.F1 = 0
        self.FAR: Union[str, float] = 0.0
        self.total_cost = 0
        self.itp = 0  # number of ignored true positives
        self.itps = []  # number of ignored true positives PER SEQUENCE
        self.tp = 0  # number of true positives including ignored true positives!
        self.tps = []  # number of true positives including ignored true positives PER SEQUENCE
        self.fn = 0  # number of false negatives WITHOUT ignored false negatives
        self.fns = []  # number of false negatives WITHOUT ignored false negatives PER SEQUENCE
        self.ifn = 0  # number of ignored false negatives
        self.ifns = []  # number of ignored false negatives PER SEQUENCE
        self.fp = 0  # number of false positives
        # a bit tricky, the number of ignored false negatives and ignored true positives
        # is subtracted, but if both tracker detection and ground truth detection
        # are ignored this number is added again to avoid double counting
        self.fps = []  # above PER SEQUENCE
        self.mme = 0
        self.fragments = 0
        self.id_switches = 0
        self.MT = 0
        self.PT = 0
        self.ML = 0

        self.eval_2diou = eval_2diou
        self.eval_3diou = eval_3diou
        if thres is None:
            if eval_2diou:
                self.min_overlap = 0.5  # minimum bounding box overlap for 3rd party metrics
            elif eval_3diou:
                self.min_overlap = 0.25  # minimum bounding box overlap for 3rd party metrics
            else:
                assert False
        else:
            self.min_overlap = thres

        self.max_truncation = max_truncation  # maximum truncation of an object for evaluation
        self.max_occlusion = max_occlusion  # maximum occlusion of an object for evaluation
        self.min_height = min_height  # minimum height of an object for evaluation
        self.n_sample_points = 500

        # this should be enough to hold all ground-truth trajectories
        # is expanded if necessary and reduced in any case
        self.gt_trajectories = [[] for _ in range(self.n_sequences)]
        self.ign_trajectories = [[] for _ in range(self.n_sequences)]
        self.scores: List[float] = []
        self.ground_truth: List[List[List[TrackData]]] = []
        self.dcareas: List[List[List[TrackData]]] = []
        self.tracker: List[List[List[TrackData]]] = []
        self.num_gt: int = 0

    def get_data_dict(self) -> Dict[str, float]:
        dct = {
            'mota': self.MOTA,
            'motp': self.MOTP,
            'moda': self.MODA,
            'modp': self.MODP,
            'precision': self.precision,
            'F1': self.F1,
            'fp': self.fp,
            'fn': self.fn,
            'recall': self.recall,
            'sMOTA': self.sMOTA,
        }
        return dct

    def load_data(self, is_ground_truth: bool) -> bool:
        """
        Helper function to load ground truth or tracking data.
        """

        if is_ground_truth:
            self._load_data(self.gt_path, self.cls, is_ground_truth)
        else:
            self._load_data(self.t_path, self.cls, is_ground_truth)
        return True

    def _load_data(self, root_dir: str, cls: str, is_ground_truth: bool) -> bool:
        """
        Generic loader for ground truth and tracking data.
        Loads detections in KITTI format from textfiles.
        """
        # construct objectDetections object to hold detection data
        t_data = TrackData()
        eval_2d = True
        eval_3d = True

        seq_data = []
        n_trajectories = 0
        n_trajectories_seq = []
        classes = get_classes(cls)
        for seq, s_name in enumerate(self.sequence_name):
            filename = os.path.join(root_dir, '%s.txt' % s_name)
            f = open(filename, 'r')

            f_data = [
                [] for _ in range(self.n_frames[seq])
            ]  # current set has only 1059 entries, sufficient length is checked anyway
            ids = []
            n_in_seq = 0
            id_frame_cache = []
            for line in f:
                # KITTI tracking benchmark data format:
                # (frame,tracklet_id,objectType,truncation,occlusion,alpha,x1,y1,x2,y2,h,w,l,X,Y,Z,ry)
                line = line.strip()
                fields = line.split(' ')
                if not any([s for s in classes if s in fields[2].lower()]):
                    continue
                # get fields from table
                t_data.frame = int(float(fields[0]))  # frame
                t_data.track_id = int(float(fields[1]))  # id
                t_data.obj_type = fields[2].lower()  # object type [car, pedestrian, cyclist, ...]
                t_data.truncation = int(float(fields[3]))  # truncation [-1,0,1,2]
                t_data.occlusion = int(float(fields[4]))  # occlusion  [-1,0,1,2]
                t_data.obs_angle = float(fields[5])  # observation angle [rad]
                t_data.x1 = float(fields[6])  # left   [px]
                t_data.y1 = float(fields[7])  # top    [px]
                t_data.x2 = float(fields[8])  # right  [px]
                t_data.y2 = float(fields[9])  # bottom [px]
                t_data.h = float(fields[10])  # height [m]
                t_data.w = float(fields[11])  # width  [m]
                t_data.l = float(fields[12])  # length [m]
                t_data.x = float(fields[13])  # X [m]
                t_data.y = float(fields[14])  # Y [m]
                t_data.z = float(fields[15])  # Z [m]
                t_data.ry = float(fields[16])  # yaw angle [rad]
                t_data.corners_3d_cam = None
                if not is_ground_truth:
                    if len(fields) == 17:
                        t_data.score = -1
                    elif len(fields) == 18:
                        t_data.score = float(fields[17])  # detection score
                    else:
                        print('file is not in KITTI format')
                        return False

                # do not consider objects marked as invalid
                if t_data.track_id == -1 and t_data.obj_type != 'dontcare':
                    continue

                idx = t_data.frame
                # check if length for frame data is sufficient
                if idx >= len(f_data):
                    print('extend f_data', idx, len(f_data))
                    f_data += [[] for x in range(max(500, idx - len(f_data)))]
                id_frame = (t_data.frame, t_data.track_id)
                if id_frame in id_frame_cache and not is_ground_truth:
                    print(
                        'track ids are not unique for sequence %d: frame %d' % (seq, t_data.frame)
                    )
                    print('track id %d occured at least twice for this frame' % t_data.track_id)
                    print('Exiting...')
                    # continue # this allows to evaluate non-unique result files
                    return False
                id_frame_cache.append(id_frame)
                f_data[t_data.frame].append(copy.copy(t_data))

                if t_data.track_id not in ids and t_data.obj_type != 'dontcare':
                    ids.append(t_data.track_id)
                    n_trajectories += 1
                    n_in_seq += 1

                # check if uploaded data provides information for 2D and 3D evaluation
                if (
                    not is_ground_truth
                    and eval_2d
                    and (t_data.x1 == -1 or t_data.x2 == -1 or t_data.y1 == -1 or t_data.y2 == -1)
                ):
                    eval_2d = False
                if (
                    not is_ground_truth
                    and eval_3d
                    and (t_data.x == -1000 or t_data.y == -1000 or t_data.z == -1000)
                ):
                    eval_3d = False

            # only add existing frames
            n_trajectories_seq.append(n_in_seq)
            seq_data.append(f_data)
            f.close()

        if not is_ground_truth:
            self.tracker = seq_data
            self.n_tr_trajectories = n_trajectories
            self.eval_2d = eval_2d
            self.eval_3d = eval_3d
            self.n_tr_seq = n_trajectories_seq
            if self.n_tr_trajectories == 0:
                raise RuntimeError(f'n_tr_trajectories {self.n_tr_trajectories}')
        else:
            # split ground truth and DontCare areas
            self.dcareas.clear()
            self.ground_truth.clear()
            for seq_idx in range(len(seq_data)):
                seq_gt = seq_data[seq_idx]
                s_g, s_dc = [], []
                for f in range(len(seq_gt)):
                    all_gt = seq_gt[f]
                    g, dc = [], []
                    for gg in all_gt:
                        if gg.obj_type == 'dontcare':
                            dc.append(gg)
                        else:
                            g.append(gg)
                    s_g.append(g)
                    s_dc.append(dc)
                self.dcareas.append(s_dc)
                self.ground_truth.append(s_g)
            self.n_gt_seq = n_trajectories_seq
            self.n_gt_trajectories = n_trajectories
        return True

    def compute_3rd_party_metrics(
        self, threshold: float = -10000.0, recall_thres: float = 1.0
    ) -> bool:
        """
        Computes the metrics defined in
            - Stiefelhagen 2008: Evaluating Multiple Object Tracking Performance: The CLEAR MOT Metrics
              MOTA, MOTAL, MOTP
            - Nevatia 2008: Global Data Association for Multi-Object Tracking Using Network Flows
              MT/PT/ML
        """

        # construct Munkres object for Hungarian Method association
        hm = Munkres()
        max_cost = 1e9
        self.scores.clear()

        # go through all frames and associate ground truth and tracker results
        # ground truth and tracker contain lists for every single frame containing lists of KITTI format detections
        f = 0
        for seq_idx in range(len(self.ground_truth)):
            seq_gt = self.ground_truth[seq_idx]
            seq_dc = self.dcareas[seq_idx]  # don't care areas
            seq_tracker_before = self.tracker[seq_idx]

            # remove the tracks with low confidence for each frame
            tracker_id_score = dict()
            for frame in range(len(seq_tracker_before)):
                tracks_tmp = seq_tracker_before[frame]
                for index in range(len(tracks_tmp)):
                    trk_tmp = tracks_tmp[index]
                    id_tmp = trk_tmp.track_id
                    score_tmp = trk_tmp.score

                    if id_tmp not in tracker_id_score.keys():
                        tracker_id_score[id_tmp] = list()
                    tracker_id_score[id_tmp].append(score_tmp)

            id_average_score, to_delete_id = filter_low_confidence(tracker_id_score, threshold)

            seq_tracker = list()
            for frame in range(len(seq_tracker_before)):
                seq_tracker_frame = list()
                tracks_tmp = seq_tracker_before[frame]
                for index in range(len(tracks_tmp)):
                    trk_tmp = tracks_tmp[index]
                    id_tmp = trk_tmp.track_id
                    average_score = id_average_score[id_tmp]
                    trk_tmp.score = average_score
                    if id_tmp not in to_delete_id:
                        seq_tracker_frame.append(trk_tmp)
                seq_tracker.append(seq_tracker_frame)

            seq_trajectories = defaultdict(list)
            seq_ignored = defaultdict(list)

            # statistics over the current sequence, check the corresponding
            # variable comments in __init__ to get their meaning
            seqtp = 0
            seqitp = 0
            seqfn = 0
            seqifn = 0
            seqfp = 0
            seqigt = 0
            seqitr = 0

            last_ids = [[], []]

            n_gts = 0
            n_trs = 0

            for f in range(len(seq_gt)):  # go through each frame
                g: List[TrackData] = seq_gt[f]
                dc: List[TrackData] = seq_dc[f]
                t: List[TrackData] = seq_tracker[f]

                # counting total number of ground truth and tracker objects
                self.n_gt += len(g)
                self.n_tr += len(t)

                n_gts += len(g)
                n_trs += len(t)

                # use hungarian method to associate, using box overlap 0..1 as cost
                # build cost matrix
                # row is gt, column is det
                cost_matrix = []
                this_ids = [[], []]
                for gg in g:
                    # save current ids
                    this_ids[0].append(gg.track_id)
                    this_ids[1].append(-1)
                    gg.tracker = -1
                    gg.id_switch = 0
                    gg.fragmentation = 0
                    cost_row: List[float] = []
                    for tt in t:
                        if self.eval_2diou:
                            c = 1 - box_overlap(gg, tt)
                        elif self.eval_3diou:
                            c = 1 - iou(gg, tt, metric=MetricKind.IOU_3D)
                        else:
                            assert False, 'error'

                        # gating for box overlap
                        if c <= 1 - self.min_overlap:
                            cost_row.append(c)
                        else:
                            cost_row.append(max_cost)  # = 1e9

                    cost_matrix.append(cost_row)
                    # all ground truth trajectories are initially not associated
                    # extend ground-truth trajectories lists (merge lists)
                    seq_trajectories[gg.track_id].append(-1)
                    seq_ignored[gg.track_id].append(False)

                if len(g) == 0:
                    cost_matrix = [[]]

                # associate
                association_matrix = hm.compute(cost_matrix)

                # tmp variables for sanity checks and MODP computation
                tmptp = 0
                tmpfp = 0
                tmpfn = 0
                tmpc = 0  # this will sum up the overlaps for all true positives
                tmpcs = [0] * len(g)  # this will save the overlaps for all true positives
                # the reason is that some true positives might be ignored
                # later such that the corresponding overlaps can
                # be subtracted from tmpc for MODP computation

                # mapping for tracker ids and ground truth ids
                for row, col in association_matrix:
                    # apply gating on box overlap
                    c = cost_matrix[row][col]
                    if c < max_cost:
                        g[row].tracker = t[col].track_id
                        this_ids[1][row] = t[col].track_id
                        t[col].valid = True
                        g[row].distance = c
                        self.total_cost += 1 - c
                        tmpc += 1 - c
                        tmpcs[row] = 1 - c
                        seq_trajectories[g[row].track_id][-1] = t[col].track_id

                        # true positives are only valid associations
                        self.tp += 1
                        tmptp += 1
                        self.scores.append(t[col].score)

                    else:
                        g[row].tracker = -1
                        self.fn += 1
                        tmpfn += 1

                # associate tracker and DontCare areas
                # ignore tracker in neighboring classes
                nignoredtracker = 0  # number of ignored tracker detections
                ignoredtrackers: Dict[int, int] = dict()  # will associate the track_id with -1
                # if it is not ignored and 1 if it is
                # ignored;
                # this is used to avoid double counting ignored
                # cases, see the next loop

                for tt in t:
                    ignoredtrackers[tt.track_id] = -1
                    # ignore detection if it belongs to a neighboring class or is
                    # smaller or equal to the minimum height

                    tt_height = abs(tt.y1 - tt.y2)
                    if (
                        (self.cls == 'car' and tt.obj_type == 'van')
                        or (self.cls == 'pedestrian' and tt.obj_type == 'person_sitting')
                        or tt_height <= self.min_height
                    ) and not tt.valid:
                        nignoredtracker += 1
                        tt.ignored = True

                        ignoredtrackers[tt.track_id] = 1
                        continue

                    for d in dc:
                        # as KITTI does not provide ground truth 3D box for DontCare objects, we have to use
                        # 2D IoU here and a threshold of 0.5 for 2D IoU.
                        overlap = box_overlap(tt, d, 'a')
                        if overlap > 0.5 and not tt.valid:
                            tt.ignored = True
                            nignoredtracker += 1
                            ignoredtrackers[tt.track_id] = 1
                            break

                # check for ignored FN/TP (truncation or neighboring object class)
                ignoredfn = 0  # the number of ignored false negatives
                nignoredtp = 0  # the number of ignored true positives
                nignoredpairs = 0  # the number of ignored pairs, i.e. a true positive
                # which is ignored but where the associated tracker
                # detection has already been ignored

                gi = 0
                for gg in g:
                    if gg.tracker < 0:
                        if (
                            gg.occlusion > self.max_occlusion
                            or gg.truncation > self.max_truncation
                            or (self.cls == 'car' and gg.obj_type == 'van')
                            or (self.cls == 'pedestrian' and gg.obj_type == 'person_sitting')
                        ):
                            seq_ignored[gg.track_id][-1] = True
                            gg.ignored = True
                            ignoredfn += 1

                    elif gg.tracker >= 0:
                        if (
                            gg.occlusion > self.max_occlusion
                            or gg.truncation > self.max_truncation
                            or (self.cls == 'car' and gg.obj_type == 'van')
                            or (self.cls == 'pedestrian' and gg.obj_type == 'person_sitting')
                        ):
                            seq_ignored[gg.track_id][-1] = True
                            gg.ignored = True
                            nignoredtp += 1

                            # if the associated tracker detection is already ignored,
                            # we want to avoid double counting ignored detections
                            nignoredpairs = bump_num_ignored_pairs(
                                ignoredtrackers[gg.tracker], nignoredpairs
                            )

                            # for computing MODP, the overlaps from ignored detections
                            # are subtracted
                            tmpc -= tmpcs[gi]
                    gi += 1

                # the below might be confusion, check the comments in __init__
                # to see what the individual statistics represent

                # nignoredtp is already associated, but should be ignored
                # ignoredfn is already missed, but should be ignored

                # correct TP by number of ignored TP due to truncation
                # ignored TP are shown as tracked in visualization
                tmptp -= nignoredtp

                # count the number of ignored true positives
                self.itp += nignoredtp

                # adjust the number of ground truth objects considered
                # self.n_gt_adjusted = self.n_gt
                self.n_gt -= ignoredfn + nignoredtp

                # count the number of ignored ground truth objects
                self.n_igt += ignoredfn + nignoredtp

                # count the number of ignored tracker objects
                self.n_itr += nignoredtracker

                # count the number of ignored pairs, i.e. associated tracker and
                # ground truth objects that are both ignored
                self.n_igttr += nignoredpairs

                # false negatives = associated gt bboxes exceeding association threshold + non-associated gt bboxes
                #

                # explanation of fn
                # the original fn is in the matched gt where the score is not high enough
                # len(g) - len(association matrix), means that some gt is not matched in hungarian
                # further - ignoredfn, means that some gt can be ignored

                tmpfn += len(g) - len(association_matrix) - ignoredfn
                self.fn += len(g) - len(association_matrix) - ignoredfn
                self.ifn += ignoredfn

                # false positives = tracker bboxes - associated tracker bboxes
                # mismatches (mme_t)
                tmpfp += len(t) - tmptp - nignoredtracker - nignoredtp + nignoredpairs
                self.fp += len(t) - tmptp - nignoredtracker - nignoredtp + nignoredpairs

                # update sequence data
                seqtp += tmptp
                seqitp += nignoredtp
                seqfp += tmpfp
                seqfn += tmpfn
                seqifn += ignoredfn
                seqigt += ignoredfn + nignoredtp
                seqitr += nignoredtracker

                # sanity checks
                # - the number of true positives minus ignored true positives
                #   should be greater or equal to 0
                # - the number of false negatives should be greater or equal to 0
                # - the number of false positives needs to be greater or equal to 0
                #   otherwise ignored detections might be counted double
                # - the number of counted true positives (plus ignored ones)
                #   and the number of counted false negatives (plus ignored ones)
                #   should match the total number of ground truth objects
                # - the number of counted true positives (plus ignored ones)
                #   and the number of counted false positives
                #   plus the number of ignored tracker detections should
                #   match the total number of tracker detections; note that
                #   nignoredpairs is subtracted here to avoid double counting
                #   of ignored detections in nignoredtp and nignoredtracker
                raise_if_negative_tp(tmptp, nignoredtp)
                raise_if_negative_fn(
                    tmpfn, len(g), len(association_matrix), ignoredfn, nignoredpairs
                )
                raise_if_negative_fp(
                    tmpfp, len(t), tmptp, nignoredtracker, nignoredtp, nignoredpairs
                )
                raise_if_trouble_fn(
                    tmptp,
                    tmpfn,
                    len(g),
                    ignoredfn,
                    nignoredtp,
                    tmpfp,
                    seq_idx,
                    f,
                    association_matrix,
                )
                raise_if_trouble_fp(
                    tmptp,
                    tmpfp,
                    nignoredtp,
                    nignoredtracker,
                    nignoredpairs,
                    len(t),
                    seq_idx,
                    f,
                    association_matrix,
                )

                # check for id switches or fragmentation
                # frag will be more than id switch, switch happens only when id is different but detection exists
                # frag happens when id switch or detection is missing
                for i, tt in enumerate(this_ids[0]):
                    if tt in last_ids[0]:
                        idx = last_ids[0].index(tt)
                        tid = this_ids[1][i]  # id in current tracker corresponding to the gt tt
                        lid = last_ids[1][idx]  # id in last frame tracker corresp. to the gt tt
                        g[i].bump_id_switch(tid, lid, self.max_truncation)
                        g[i].bump_fragmentation(tid, lid, self.max_truncation)
                # save current index
                last_ids = this_ids
                # compute MOTP_t
                MODP_t = 1
                if tmptp != 0:
                    MODP_t = tmpc / float(tmptp)
                self.MODP_t.append(MODP_t)

            # remove empty lists for current gt trajectories
            self.gt_trajectories[seq_idx] = seq_trajectories
            self.ign_trajectories[seq_idx] = seq_ignored

            # self.num_gt += n_gts
            # gather statistics for "per sequence" statistics.
            self.n_gts.append(n_gts)
            self.n_trs.append(n_trs)
            self.tps.append(seqtp)
            self.itps.append(seqitp)
            self.fps.append(seqfp)
            self.fns.append(seqfn)
            self.ifns.append(seqifn)
            self.n_igts.append(seqigt)
            self.n_itrs.append(seqitr)

        # compute MT/PT/ML, fragments, idswitches for all groundtruth trajectories
        n_ignored_tr_total = self.bump_clear_mot(f)
        self.compute_mt_ml_pt(n_ignored_tr_total)
        self.compute_f1()
        self.compute_far()
        self.compute_clear_mot(recall_thres)
        self.compute_motp()
        self.compute_motal()
        self.compute_modp()
        self.num_gt = self.tp + self.fn
        return True

    def bump_clear_mot(self, f: int) -> int:
        # compute MT/PT/ML, fragments, idswitches for all groundtruth trajectories
        n_ignored_tr_total = 0
        for seq_idx, (seq_trajectories, seq_ignored) in enumerate(
            zip(self.gt_trajectories, self.ign_trajectories)
        ):
            if len(seq_trajectories) == 0:
                continue
            n_ignored_tr = 0
            for g, ign_g in zip(seq_trajectories.values(), seq_ignored.values()):
                # all frames of this gt trajectory are ignored
                if all(ign_g):
                    n_ignored_tr += 1
                    n_ignored_tr_total += 1
                    continue
                # all frames of this gt trajectory are not assigned to any detections
                if all([this == -1 for this in g]):
                    self.ML += 1
                    continue
                # compute tracked frames in trajectory
                last_id: int = g[0]
                # first detection (necessary to be in gt_trajectories) is always tracked
                tracked = 1 if g[0] >= 0 else 0
                lgt = 0 if ign_g[0] else 1
                for f in range(1, len(g)):  #!!! rather terrible use of `f` here
                    if ign_g[f]:
                        last_id = -1
                        continue
                    lgt += 1
                    self.bump_id_switches(g, f, last_id)
                    self.bump_fragments(g, f, last_id)
                    if g[f] != -1:
                        tracked += 1
                        last_id = g[f]
                # handle last frame; tracked state is handled in for loop (g[f]!=-1)
                self.handle_last_frame(g, f, ign_g, last_id)

                tracking_ratio = tracked / float(len(g) - sum(ign_g))
                self.bump_mt_ml_pt(tracking_ratio)
        return n_ignored_tr_total

    def bump_id_switches(self, g: List[int], f: int, last_id: int) -> None:
        if last_id != g[f] and last_id != -1 and g[f] != -1 and g[f - 1] != -1:
            self.id_switches += 1

    def bump_fragments(self, g: List[int], f: int, last_id: int) -> None:
        if f < len(g) - 1 and g[f - 1] != g[f] and last_id != -1 and g[f] != -1 and g[f + 1] != -1:
            self.fragments += 1

    def handle_last_frame(self, g: List[int], f: int, ign_g: List[bool], last_id: int) -> None:
        if len(g) > 1 and g[f - 1] != g[f] and last_id != -1 and g[f] != -1 and not ign_g[f]:
            self.fragments += 1

    def bump_mt_ml_pt(self, tracking_ratio: float) -> None:
        if tracking_ratio > 0.8:
            self.MT += 1
        elif tracking_ratio < 0.2:
            self.ML += 1
        else:  # 0.2 <= tracking_ratio <= 0.8
            self.PT += 1

    def compute_mt_ml_pt(self, n_ignored_tr_total: int) -> None:
        if (self.n_gt_trajectories - n_ignored_tr_total) == 0:
            self.MT = 0.0
            self.PT = 0.0
            self.ML = 0.0
        else:
            self.MT /= float(self.n_gt_trajectories - n_ignored_tr_total)
            self.PT /= float(self.n_gt_trajectories - n_ignored_tr_total)
            self.ML /= float(self.n_gt_trajectories - n_ignored_tr_total)

    def compute_f1(self) -> None:  # precision/recall/F1-score.
        if (self.fp + self.tp) == 0 or (self.fn + self.tp) == 0:
            self.recall = 0.0
            self.precision = 0.0
        else:
            self.recall = self.tp / float(self.tp + self.fn)
            self.precision = self.tp / float(self.fp + self.tp)
        if abs(self.recall + self.precision) < 0.000001:
            self.F1 = 0.0
        else:
            self.F1 = 2.0 * (self.precision * self.recall) / (self.precision + self.recall)

    def compute_far(self) -> None:
        if sum(self.n_frames) == 0:
            self.FAR = 'n/a'
        else:
            self.FAR = self.fp / float(sum(self.n_frames))

    def compute_clear_mot(self, recall_thres: float) -> None:
        # compute CLEARMOT
        if self.n_gt == 0:
            self.MOTA = -float('inf')
            self.MODA = -float('inf')
            self.sMOTA = -float('inf')
        else:
            self.MOTA = 1 - (self.fn + self.fp + self.id_switches) / float(self.n_gt)
            self.MODA = 1 - (self.fn + self.fp) / float(self.n_gt)
            ratio = 1.0 - (
                self.fn + self.fp + self.id_switches - (1.0 - recall_thres) * self.n_gt
            ) / (recall_thres * self.n_gt)
            self.sMOTA = min(1.0, max(0.0, ratio))

    def compute_motp(self) -> None:
        if self.tp == 0:
            self.MOTP = 0
        else:
            self.MOTP = self.total_cost / float(self.tp)

    def compute_motal(self) -> None:
        if self.n_gt != 0:
            if self.id_switches == 0:
                self.MOTAL = 1 - (self.fn + self.fp) / self.n_gt
            else:
                self.MOTAL = 1 - (self.fn + self.fp + math.log10(self.id_switches)) / self.n_gt
        else:
            self.MOTAL = -float('inf')

    def compute_modp(self) -> None:
        frames_num = sum(self.n_frames)
        self.MODP = 'n/a' if frames_num == 0 else sum(self.MODP_t) / frames_num

    def create_summary_details(self):
        """
        Generate and mail a summary of the results.
        If mailpy.py is present, the summary is instead printed.
        """

        summary = ''

        summary += 'evaluation: best results with single threshold'.center(80, '=') + '\n'
        summary += print_entry('Multiple Object Tracking Accuracy (MOTA)', self.MOTA) + '\n'
        summary += print_entry('Multiple Object Tracking Precision (MOTP)', float(self.MOTP)) + '\n'
        summary += print_entry('Multiple Object Tracking Accuracy (MOTAL)', self.MOTAL) + '\n'
        summary += print_entry('Multiple Object Detection Accuracy (MODA)', self.MODA) + '\n'
        summary += (
            print_entry('Multiple Object Detection Precision (MODP)', float(self.MODP)) + '\n'
        )
        summary += '\n'
        summary += print_entry('Recall', self.recall) + '\n'
        summary += print_entry('Precision', self.precision) + '\n'
        summary += print_entry('F1', self.F1) + '\n'
        summary += print_entry('False Alarm Rate', self.FAR) + '\n'
        summary += '\n'
        summary += print_entry('Mostly Tracked', self.MT) + '\n'
        summary += print_entry('Partly Tracked', self.PT) + '\n'
        summary += print_entry('Mostly Lost', self.ML) + '\n'
        summary += '\n'
        summary += print_entry('True Positives', self.tp) + '\n'
        # summary += self.printEntry("True Positives per Sequence", self.tps) + "\n"
        summary += print_entry('Ignored True Positives', self.itp) + '\n'
        # summary += self.printEntry("Ignored True Positives per Sequence", self.itps) + "\n"
        summary += print_entry('False Positives', self.fp) + '\n'
        # summary += self.printEntry("False Positives per Sequence", self.fps) + "\n"
        summary += print_entry('False Negatives', self.fn) + '\n'
        # summary += self.printEntry("False Negatives per Sequence", self.fns) + "\n"
        summary += print_entry('Ignored False Negatives', self.ifn) + '\n'
        # summary += self.printEntry("Ignored False Negatives per Sequence", self.ifns) + "\n"
        # summary += self.printEntry("Missed Targets", self.fn) + "\n"
        summary += print_entry('ID-switches', self.id_switches) + '\n'
        summary += print_entry('Fragmentations', self.fragments) + '\n'
        summary += '\n'
        summary += print_entry('Ground Truth Objects (Total)', self.n_gt + self.n_igt) + '\n'
        # summary += self.printEntry("Ground Truth Objects (Total) per Sequence", self.n_gts) + "\n"
        summary += print_entry('Ignored Ground Truth Objects', self.n_igt) + '\n'
        # summary += self.printEntry("Ignored Ground Truth Objects per Sequence", self.n_igts) + "\n"
        summary += print_entry('Ground Truth Trajectories', self.n_gt_trajectories) + '\n'
        summary += '\n'
        summary += print_entry('Tracker Objects (Total)', self.n_tr) + '\n'
        # summary += self.printEntry("Tracker Objects (Total) per Sequence", self.n_trs) + "\n"
        summary += print_entry('Ignored Tracker Objects', self.n_itr) + '\n'
        # summary += self.printEntry("Ignored Tracker Objects per Sequence", self.n_itrs) + "\n"
        summary += print_entry('Tracker Trajectories', self.n_tr_trajectories) + '\n'
        # summary += "\n"
        # summary += self.printEntry("Ignored Tracker Objects with Associated Ignored Ground Truth Objects", self.n_igttr) + "\n"
        summary += '=' * 80

        return summary

    def create_summary_simple(self, threshold, recall):
        """
        Generate and mail a summary of the results.
        If mailpy.py is present, the summary is instead printed.
        """

        summary = ''

        summary += (
            'evaluation with confidence threshold %f, recall %f' % (threshold, recall)
        ).center(80, '=') + '\n'
        summary += ' sMOTA   MOTA   MOTP    MT     ML     IDS  FRAG    F1   Prec  Recall  FAR     TP    FP    FN\n'

        summary += '{:.4f} {:.4f} {:.4f} {:.4f} {:.4f} {:5d} {:5d} {:.4f} {:.4f} {:.4f} {:.4f} {:5d} {:5d} {:5d}\n'.format(
            self.sMOTA,
            self.MOTA,
            self.MOTP,
            self.MT,
            self.ML,
            self.id_switches,
            self.fragments,
            self.F1,
            self.precision,
            self.recall,
            self.FAR,
            self.tp,
            self.fp,
            self.fn,
        )
        summary += '=' * 80

        return summary

    def reset(self) -> None:
        self.n_gt = (
            0  # number of ground truth detections minus ignored false negatives and true positives
        )
        self.n_igt = 0  # number of ignored ground truth detections
        self.n_tr = 0  # number of tracker detections minus ignored tracker detections
        self.n_itr = 0  # number of ignored tracker detections
        self.n_igttr = 0  # number of ignored ground truth detections where the corresponding associated tracker detection is also ignored

        self.MOTA = 0
        self.MOTP = 0
        self.MOTAL = 0
        self.MODA = 0
        self.MODP = 0
        self.MODP_t = []

        self.recall = 0
        self.precision = 0
        self.F1 = 0
        self.FAR = 0

        self.total_cost = 0
        self.itp = 0
        self.tp = 0
        self.fn = 0
        self.ifn = 0
        self.fp = 0

        self.n_gts = []  # number of ground truth detections minus ignored false negatives and true positives PER SEQUENCE
        self.n_igts = []  # number of ground ignored truth detections PER SEQUENCE
        self.n_trs = []  # number of tracker detections minus ignored tracker detections PER SEQUENCE
        self.n_itrs = []  # number of ignored tracker detections PER SEQUENCE

        self.itps = []  # number of ignored true positives PER SEQUENCE
        self.tps = []  # number of true positives including ignored true positives PER SEQUENCE
        self.fns = []  # number of false negatives WITHOUT ignored false negatives PER SEQUENCE
        self.ifns = []  # number of ignored false negatives PER SEQUENCE
        self.fps = []  # above PER SEQUENCE

        self.fragments = 0
        self.id_switches = 0
        self.MT = 0
        self.PT = 0
        self.ML = 0

        self.gt_trajectories = [[] for x in range(self.n_sequences)]
        self.ign_trajectories = [[] for x in range(self.n_sequences)]

    def save_to_stats(self, dump, threshold=None, recall=None) -> str:
        """
        Save the statistics in a whitespace separate file.
        """

        if threshold is None:
            summary = self.create_summary_details()
        else:
            summary = self.create_summary_simple(threshold, recall)
        print(summary)  # mail or print the summary.
        print(summary, file=dump)
        return summary
