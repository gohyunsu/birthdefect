# HVSMR-2.0 cropped_norm: download and preprocessing record

작성자: 고현수  
실행일: 2026-07-17

## Source and reproducibility

- Official dataset: [HVSMR-2.0 cropped_norm](https://figshare.com/articles/dataset/HVSMR-2_0_cropped_norm_/25226363), DOI `10.6084/m9.figshare.25226363.v2`
- License: CC BY 4.0
- Downloaded artifact: `cropped_norm.zip` (1,214,309,305 bytes)
- Official/computed MD5: `6027791717a1ecf51b03e0d84f1acee7` (matched)
- Chosen variant: `cropped_norm`; manually heart-cropped and intensity-normalized CMR volumes.

`orig`, `cropped`, and `cropped_norm` must not be combined in the same experiment. Raw files and derived artifacts are intentionally excluded from Git.

## Executed preprocessing

The script `src/preprocess_hvsmr.py` audits the official data without changing image geometry or labels.

1. paired each `pat#_cropped_norm.nii.gz` with segmentation and endpoint mask;
2. verified identical image/segmentation/endpoint shapes per subject;
3. extracted shape, voxel spacing, intensity percentiles, label voxel counts, and endpoint voxel counts;
4. merged official clinical and technical metadata by subject ID;
5. generated three axial image-plus-segmentation QC overlays;
6. wrote a patient-level manifest and summary CSV under `datasets/processed/`.

## Observed dataset properties

| Property | Result |
|---|---:|
| Subjects | 60 |
| Extracted files | 361 |
| Image shape range | 83×95×77 to 273×322×220 |
| Voxel spacing mean | 0.728×0.734×0.808 mm |
| Voxel spacing range | 0.521–1.146, 0.521–1.146, 0.375–1.600 mm |
| Median whole-heart foreground voxels | 584,148 |
| LV / LA / AO / PA / SVC / IVC present | 60 / 60 / 60 / 60 / 60 / 60 subjects |
| RV present | 54 subjects |
| RA present | 50 subjects |
| Clinical metadata matched | 59 subjects (`pat59` has no clinical row) |
| Technical metadata matched | 60 subjects |
| Legacy HVSMR 2016 membership | 10 train, 10 test, 40 not in prior challenge split |

The missing RV/RA labels should be treated as genuine anatomy/annotation variation, not silently replaced with background-positive assumptions. Segmentation evaluation must report both per-structure scores and label-presence-aware scores.

## Baseline-ready protocol

- Train only on the `cropped_norm` variant for this first experiment.
- Split by patient, never by slice or patch.
- Retain supplied clinical/technical columns for stratification and error analysis; do not use them as predictive input unless that is an explicit multimodal task.
- Do not use `HVSMR2016` as the new split by default. It denotes a legacy 20-subject challenge subset; construct and version a new 60-subject patient-level split for the present study.
- Resample only inside a documented training transform. Preserve the original NIfTI and manifest as the audit source.
- Start with 3D U-Net/nnU-Net; report Dice and HD95 by structure, presence-aware score, and confidence intervals across subjects.
