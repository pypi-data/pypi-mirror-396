# Detections for KITTI sequences from a Point-RCNN detector.

The data is copied from [AB-3D-MOT original repo](https://github.com/xinshuoweng/AB3DMOT/tree/master/data/KITTI/detection)

The goal is to reproduce the well-known tracking quality metrics (MOTA and ClearMOT) locally
without submission to the KITTI evaluation server. This implies having the corresponding 
annotations on-site. The KITTI provides annotations only for its `training` subset
(referred by the short name `val` in the original AB3DMOT repo). Therefore, only corresponding
detections are stored in this repo.

The format of the data per column

    0. time stamp
    1. object class: (1: pedestrian, 2: car, 3: cyclist)
    2:4. top-left corner of the detection on the image in pixels
    4:6. bottom-right corner of the detection on the image in pixels
    6. ? could be the observation angle in degrees?
    7:10. size of the 3D bounding box in KITTI order (height, width, length) in meters
    10:13. position of the 3D bounding box in meters (x, y, z)
    14. rotation around Y-axis in camera coordinates in radians.
    15. ? occlusion or truncation?

[A description of KITTI detection format](https://labelformat.com/formats/object-detection/kitti/)
is helpful, but not accurate. It claims 15 values, but specifies only 13. The format 
for this data might not be precisely the same.

