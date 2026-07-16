#!/usr/bin/env python3
"""Create GitHub Pages-safe visual summaries from the HVSMR audit manifest."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(".cache") / "matplotlib"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


LABELS = ["LV", "RV", "LA", "RA", "AO", "PA", "SVC", "IVC"]
COLORS = {"green": "#174c42", "coral": "#e2755d", "sage": "#dce8dc", "ink": "#18201f", "line": "#d7ded8"}


def setup() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold", "axes.labelcolor": COLORS["ink"], "xtick.color": COLORS["ink"], "ytick.color": COLORS["ink"]})


def label_presence(manifest: pd.DataFrame, output: Path) -> None:
    counts = [(label, int((manifest[f"voxels_{label}"] > 0).sum())) for label in LABELS]
    names, values = zip(*counts)
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=180)
    bars = ax.barh(names, values, color=[COLORS["green"] if value == 60 else COLORS["coral"] for value in values], height=0.62)
    ax.set_xlim(0, 64)
    ax.set_xlabel("Subjects with an annotated structure (out of 60)")
    ax.set_title("Annotation presence by cardiac structure", loc="left", pad=14)
    ax.grid(axis="x", color=COLORS["line"], linewidth=.7)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, values):
        ax.text(value + .8, bar.get_y() + bar.get_height() / 2, f"{value}/60", va="center", fontsize=9, color=COLORS["ink"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(output, transparent=False, facecolor="#fbfaf5")
    plt.close(fig)


def spatial_variation(manifest: pd.DataFrame, output: Path) -> None:
    mean_spacing = manifest[["spacing_x_mm", "spacing_y_mm", "spacing_z_mm"]].mean(axis=1)
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=180)
    colors = np.where(manifest["RV"].notna() if "RV" in manifest else manifest["voxels_RV"] > 0, COLORS["green"], COLORS["coral"])
    ax.scatter(mean_spacing, manifest["foreground_voxels"] / 1e6, c=colors, s=50, alpha=.85, edgecolors="#fbfaf5", linewidths=.8)
    ax.set_xlabel("Mean voxel spacing (mm)")
    ax.set_ylabel("Whole-heart foreground (million voxels)")
    ax.set_title("Spatial variation across the 60 CMR volumes", loc="left", pad=14)
    ax.grid(color=COLORS["line"], linewidth=.7)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(output, transparent=False, facecolor="#fbfaf5")
    plt.close(fig)


def clinical_category(manifest: pd.DataFrame, output: Path) -> None:
    counts = manifest["Category"].fillna("metadata missing").value_counts().reindex(["mild", "moderate", "severe", "metadata missing"], fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=180)
    bars = ax.bar(counts.index, counts.values, color=[COLORS["sage"], "#8eb9aa", COLORS["green"], COLORS["coral"]], width=.62)
    ax.set_ylim(0, 42)
    ax.set_ylabel("Subjects")
    ax.set_title("Official clinical severity metadata", loc="left", pad=14)
    ax.grid(axis="y", color=COLORS["line"], linewidth=.7)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + .8, str(value), ha="center", fontsize=10, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(output, transparent=False, facecolor="#fbfaf5")
    plt.close(fig)


def age_distribution(manifest: pd.DataFrame, output: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=180)
    categories = [("mild", "#b8d6c9"), ("moderate", "#5f9f8b"), ("severe", COLORS["green"])]
    bins = np.arange(-.5, 56, 4)
    for category, color in categories:
        ages = manifest.loc[manifest["Category"] == category, "Age"].dropna()
        ax.hist(ages, bins=bins, alpha=.8, color=color, label=category)
    ax.set_xlabel("Age in official clinical metadata")
    ax.set_ylabel("Subjects")
    ax.set_title("Age distribution by official severity category", loc="left", pad=14)
    ax.legend(frameon=False, ncol=3, loc="upper right")
    ax.grid(axis="y", color=COLORS["line"], linewidth=.7)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(output, transparent=False, facecolor="#fbfaf5")
    plt.close(fig)


def acquisition_distribution(manifest: pd.DataFrame, output: Path) -> None:
    fields = [("TE", "TE"), ("TR", "TR"), ("FA", "FA"), ("BW", "BW")]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), dpi=180)
    for axis, (column, label) in zip(axes.ravel(), fields):
        values = manifest[column].dropna()
        axis.hist(values, bins=min(12, max(5, len(values) // 5)), color=COLORS["green"], alpha=.88)
        axis.set_title(label, loc="left", fontweight="bold")
        axis.set_xlabel("Official technical metadata value")
        axis.set_ylabel("Subjects")
        axis.grid(axis="y", color=COLORS["line"], linewidth=.7)
        axis.set_axisbelow(True)
        for spine in axis.spines.values():
            spine.set_visible(False)
    fig.suptitle("Acquisition parameter distributions", x=.08, ha="left", y=.995, fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(output, transparent=False, facecolor="#fbfaf5")
    plt.close(fig)


def label_volume_distribution(manifest: pd.DataFrame, output: Path) -> None:
    values = [manifest.loc[manifest[f"voxels_{label}"] > 0, f"voxels_{label}"].to_numpy() / 1e3 for label in LABELS]
    fig, ax = plt.subplots(figsize=(9, 5), dpi=180)
    box = ax.boxplot(values, orientation="horizontal", tick_labels=LABELS, patch_artist=True, medianprops={"color": "#18201f"})
    for patch in box["boxes"]:
        patch.set(facecolor="#8eb9aa", edgecolor=COLORS["green"])
    ax.set_xlabel("Annotated volume (thousand voxels; present labels only)")
    ax.set_title("Per-structure label volume variation", loc="left", pad=14)
    ax.grid(axis="x", color=COLORS["line"], linewidth=.7)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(output, transparent=False, facecolor="#fbfaf5")
    plt.close(fig)


def processing_panel(manifest: pd.DataFrame, subject_id: str, output: Path) -> None:
    """Show the exact input/mask/endpoint/overlay chain for one supplied volume."""
    row = manifest.loc[manifest["subject_id"] == subject_id]
    if row.empty:
        raise ValueError(f"Subject not found: {subject_id}")
    row = row.iloc[0]
    import nibabel as nib

    image = nib.load(row["image_path"]).get_fdata(dtype=np.float32)
    segmentation = np.asanyarray(nib.load(row["seg_path"]).dataobj).astype(np.int16)
    endpoints = np.asanyarray(nib.load(row["endpoint_path"]).dataobj).astype(np.int16)
    slice_index = int(np.argmax(np.count_nonzero(segmentation, axis=(0, 1))))
    image_slice = image[:, :, slice_index].T
    seg_slice = segmentation[:, :, slice_index].T
    endpoint_slice = endpoints[:, :, slice_index].T
    lower, upper = np.percentile(image, [1, 99])

    fig, axes = plt.subplots(1, 4, figsize=(14, 4), dpi=180)
    panels = [
        ("Input CMR", image_slice, "gray", lower, upper),
        ("Whole-heart mask", np.ma.masked_where(seg_slice == 0, seg_slice), "tab10", 1, 8),
        ("Vessel endpoints", np.ma.masked_where(endpoint_slice == 0, endpoint_slice), "magma", 1, 8),
    ]
    for axis, (title, panel, cmap, vmin, vmax) in zip(axes[:3], panels):
        if title != "Input CMR":
            axis.imshow(image_slice, cmap="gray", vmin=lower, vmax=upper, origin="lower")
        axis.imshow(panel, cmap=cmap, vmin=vmin, vmax=vmax, origin="lower")
        axis.set_title(title, fontsize=10, fontweight="bold")
        axis.set_axis_off()
    axes[3].imshow(image_slice, cmap="gray", vmin=lower, vmax=upper, origin="lower")
    axes[3].imshow(np.ma.masked_where(seg_slice == 0, seg_slice), cmap="tab10", vmin=1, vmax=8, alpha=.55, origin="lower")
    axes[3].set_title("QC overlay", fontsize=10, fontweight="bold")
    axes[3].set_axis_off()
    fig.suptitle(f"{subject_id} · axial slice {slice_index}", x=.02, ha="left", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(output, transparent=False, facecolor="#fbfaf5")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("assets/hvsmr"))
    parser.add_argument("--case-id", default="pat0")
    args = parser.parse_args()
    setup()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(args.manifest)
    label_presence(manifest, args.output_dir / "label_presence.png")
    spatial_variation(manifest, args.output_dir / "spatial_variation.png")
    clinical_category(manifest, args.output_dir / "clinical_category.png")
    age_distribution(manifest, args.output_dir / "age_distribution.png")
    acquisition_distribution(manifest, args.output_dir / "acquisition_distribution.png")
    label_volume_distribution(manifest, args.output_dir / "label_volume_distribution.png")
    processing_panel(manifest, args.case_id, args.output_dir / f"{args.case_id}_processing_panel.png")


if __name__ == "__main__":
    main()
