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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("assets/hvsmr"))
    args = parser.parse_args()
    setup()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(args.manifest)
    label_presence(manifest, args.output_dir / "label_presence.png")
    spatial_variation(manifest, args.output_dir / "spatial_variation.png")
    clinical_category(manifest, args.output_dir / "clinical_category.png")


if __name__ == "__main__":
    main()
