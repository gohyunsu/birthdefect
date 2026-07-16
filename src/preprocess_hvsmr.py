#!/usr/bin/env python3
"""Create a patient-level manifest and visual QC overlays for HVSMR-2.0.

Input layout is the official cropped_norm archive after extraction. This script
does not resample images or overwrite labels: it audits the supplied data and
creates only derived CSV/PNG artifacts under datasets/processed.
"""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".cache") / "matplotlib"))

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd


LABELS = {
    1: "LV",
    2: "RV",
    3: "LA",
    4: "RA",
    5: "AO",
    6: "PA",
    7: "SVC",
    8: "IVC",
}


def find_cases(data_dir: Path) -> list[tuple[str, Path, Path, Path]]:
    images = sorted(data_dir.rglob("pat*_cropped_norm.nii.gz"))
    cases = []
    for image in images:
        stem = image.name.replace("_cropped_norm.nii.gz", "")
        seg = image.with_name(f"{stem}_cropped_seg.nii.gz")
        endpoints = image.with_name(f"{stem}_cropped_seg_endpoints.nii.gz")
        if not seg.exists() or not endpoints.exists():
            raise FileNotFoundError(f"Missing paired label for {image}")
        cases.append((stem, image, seg, endpoints))
    return cases


def volume_record(subject_id: str, image_path: Path, seg_path: Path, endpoint_path: Path) -> dict[str, object]:
    image_nii = nib.load(image_path)
    seg_nii = nib.load(seg_path)
    endpoint_nii = nib.load(endpoint_path)
    image = image_nii.get_fdata(dtype=np.float32)
    seg = np.asanyarray(seg_nii.dataobj).astype(np.int16)
    endpoints = np.asanyarray(endpoint_nii.dataobj).astype(np.int16)
    if image.shape != seg.shape or image.shape != endpoints.shape:
        raise ValueError(f"Shape mismatch in {subject_id}: {image.shape}, {seg.shape}, {endpoints.shape}")

    record: dict[str, object] = {
        "subject_id": subject_id,
        "image_path": str(image_path),
        "seg_path": str(seg_path),
        "endpoint_path": str(endpoint_path),
        "shape_x": image.shape[0],
        "shape_y": image.shape[1],
        "shape_z": image.shape[2],
        "spacing_x_mm": float(image_nii.header.get_zooms()[0]),
        "spacing_y_mm": float(image_nii.header.get_zooms()[1]),
        "spacing_z_mm": float(image_nii.header.get_zooms()[2]),
        "dtype": str(image_nii.get_data_dtype()),
        "intensity_p01": float(np.percentile(image, 1)),
        "intensity_p50": float(np.percentile(image, 50)),
        "intensity_p99": float(np.percentile(image, 99)),
        "foreground_voxels": int(np.count_nonzero(seg)),
        "endpoint_voxels": int(np.count_nonzero(endpoints)),
    }
    for label_id, name in LABELS.items():
        record[f"voxels_{name}"] = int(np.count_nonzero(seg == label_id))
    unknown = np.setdiff1d(np.unique(seg), np.array([0, *LABELS]))
    record["unknown_labels"] = ";".join(map(str, unknown.tolist()))
    return record


def save_overlay(subject_id: str, image_path: Path, seg_path: Path, output_path: Path) -> None:
    image = nib.load(image_path).get_fdata(dtype=np.float32)
    seg = np.asanyarray(nib.load(seg_path).dataobj).astype(np.int16)
    z_index = int(np.argmax(np.count_nonzero(seg, axis=(0, 1))))
    lower, upper = np.percentile(image, [1, 99])
    fig, ax = plt.subplots(figsize=(6, 6), dpi=180)
    ax.imshow(image[:, :, z_index].T, cmap="gray", origin="lower", vmin=lower, vmax=upper)
    ax.imshow(np.ma.masked_where(seg[:, :, z_index].T == 0, seg[:, :, z_index].T), cmap="tab10", origin="lower", alpha=0.52, vmin=1, vmax=8)
    ax.set_title(f"{subject_id} · axial slice {z_index}")
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    fig.savefig(output_path, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("datasets/processed/hvsmr-2.0/cropped_norm"))
    parser.add_argument("--overlay-count", type=int, default=3)
    parser.add_argument("--clinical-csv", type=Path)
    parser.add_argument("--technical-csv", type=Path)
    args = parser.parse_args()

    cases = find_cases(args.data_dir)
    if not cases:
        raise FileNotFoundError(f"No *_cropped_norm.nii.gz files found under {args.data_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    overlay_dir = args.output_dir / "qc_overlays"
    overlay_dir.mkdir(exist_ok=True)

    records = [volume_record(*case) for case in cases]
    manifest = pd.DataFrame(records).sort_values("subject_id")
    manifest["Pat"] = manifest["subject_id"].str.extract(r"pat(\d+)").astype(int)
    for metadata_path in (args.clinical_csv, args.technical_csv):
        if metadata_path:
            metadata = pd.read_csv(metadata_path)
            metadata = metadata.loc[metadata["Pat"].notna()].copy()
            metadata["Pat"] = metadata["Pat"].astype(int)
            manifest = manifest.merge(metadata, on="Pat", how="left", validate="one_to_one")
    manifest.to_csv(args.output_dir / "manifest.csv", index=False)

    for case in cases[: args.overlay_count]:
        subject_id, image_path, seg_path, _ = case
        save_overlay(subject_id, image_path, seg_path, overlay_dir / f"{subject_id}_axial_overlay.png")

    summary = {
        "subjects": len(manifest),
        "shape_min": " × ".join(map(str, manifest[["shape_x", "shape_y", "shape_z"]].min().tolist())),
        "shape_max": " × ".join(map(str, manifest[["shape_x", "shape_y", "shape_z"]].max().tolist())),
        "foreground_voxels_median": int(manifest["foreground_voxels"].median()),
    }
    for name in LABELS.values():
        summary[f"subjects_with_{name}"] = int((manifest[f"voxels_{name}"] > 0).sum())
    with (args.output_dir / "summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary.keys())
        writer.writeheader()
        writer.writerow(summary)
    print(pd.Series(summary).to_string())


if __name__ == "__main__":
    main()
