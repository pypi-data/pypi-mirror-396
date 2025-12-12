"""
Utility class to load data.
"""

from pure_ab_3d_mot.box import Box3D


class TrackData(Box3D):
    def __init__(
        self,
        frame=-1,
        obj_type='unset',
        truncation=-1,
        occlusion=-1,
        obs_angle=-10,
        x1=-1,
        y1=-1,
        x2=-1,
        y2=-1,
        w=-1,
        h=-1,
        l=-1,  # noqa: E741
        x=-1000,
        y=-1000,
        z=-1000,
        ry=-10,
        score=-1000,
        track_id=-1,
    ) -> None:
        """
        Constructor, initializes the object given the parameters.
        """
        super().__init__(x, y, z, h, w, l, ry, score)
        self.frame = frame
        self.track_id = track_id
        self.obj_type = obj_type
        self.truncation = truncation
        self.occlusion = occlusion
        self.obs_angle = obs_angle
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.ignored = False
        self.valid = False
        self.tracker = -1
        self.distance = 0.0
        self.fragmentation = 0
        self.id_switch = 0
        self.score = score

    def __repr__(self) -> str:
        return (
            f'Track(id {self.track_id} frame {self.frame} score {self.score} '
            f'x {self.x} y {self.y} z {self.z})'
        )

    def __str__(self) -> str:
        """
        Print read data.
        """
        attrs = vars(self)
        return '\n'.join('%s: %s' % item for item in attrs.items())

    def bump_fragmentation(self, tid: int, lid: int, max_truncation: int) -> None:
        if tid != lid and lid != -1 and self.truncation < max_truncation:
            self.fragmentation = 1

    def bump_id_switch(self, tid: int, lid: int, max_truncation: int) -> None:
        if tid != lid and lid != -1 and tid != -1 and self.truncation < max_truncation:
            self.id_switch = 1
