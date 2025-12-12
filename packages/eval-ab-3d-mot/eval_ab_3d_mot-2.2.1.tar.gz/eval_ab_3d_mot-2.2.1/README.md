# Evaluation of a base of 3D multiple-object tracking (AB3DMOT) 

Evaluation part of the AB3DMOT by Xinshuo Weng (https://github.com/xinshuoweng/AB3DMOT)
The purpose of the package is to enable calculation of the detection+tracking quality
metrics for 3D tracking with KITTI data set.

Apart from the refactored evaluation part of the AB3DMOT, a binary classifier 
of the association outcomes is included. See the section 
[Run the pure AB-3D-MOT tracker and assess the association quality using ClavIA](#run-the-pure-ab-3d-mot-tracker-and-assess-the-association-quality-using-clavia) 

## Installation

Should be as easy as `pip install eval-ab-3d-mot`, but if you downloaded the repo,
then `uv sync` standing in the root folder.

## Download the detections & annotations

Should be as easy as

```
git clone https://github.com/kovalp/eval-ab-3d-mot.git
```

The detections (R-CNN) and annotations (training subset of KITTI)
are now in the folder `eval-ab-3d-mot/assets`.

## Command-line scripts

The command-line scripts are equipped with `--help` option which should be 
sufficient to guess their usage.

### Run the pure AB-3D-MOT tracker

```
batch-run-ab-3d-mot assets/detections/kitti/point-r-cnn-training/car/*.txt
```

Apart from the detections, the `pure-ab-3d-mot` tracker could be fed with KITTI annotations.

```
batch-run-ab-3d-mot-annotations assets/annotations/kitti/training/*.txt
```

By default, the car category is selected.

In both cases, consuming detections or annotations, the output is stored into text files.
The output of the tracker could be evaluated with ClearMOT metric.


### Evaluate the output of the pure AB-3D-MOT tracker using ClearMOT metric 

```
batch-eval-ab-3d-mot assets/annotations/kitti/training/*.txt
```

### Run the pure AB-3D-MOT tracker and evaluate the association quality using ClavIA

```
run-ab-3d-mot-with-clavia assets/annotations/kitti/training/*.txt
```

The script runs the tracker feeding it with (KITTI) annotations.
The result of the tracking is analysed with respect to the association accuracy.
The script allows to select the category of the objects to track (option 
`--category-obj` or `-c` for short).

Apart from the object category, it is possible to choose another category for
tracker *parameters*. Normally, the object category should be the same as
parameters category. By choosing a different parameter category, one could see
the effect of choosing different tracker parameters on the same detections.
The parameter category can be defined via the option `--category-prm` or `-p` for short.
If the option is absent, the parameter category will be the same as object category.

Note that some of the tracker parameters (`algorithm`, `metric`, `threshold` and `max-age`)
are possible to set via command-line options. These parameters affect the association.
