"""Section 1 — Smoking stresses my body, verified.

Blog: "4 Findings from 4 Days of Tracking: An HRV Case Study"
Figure: fig1_smoking_night_curve.png (the "3-point image").

Method (3-stage night curve, dumbbell x3 on stressIndex):
  - Stage 0 "Clean rest (~8pm)": relaxed baseline, digestion done, no stressors.
  - Stage 1 "Nicotine + snack (~10pm)": first jump after cigarettes (+ small snack).
  - Stage 2 "In bed after dinner (~midnight)": final state, trapped near the ceiling.
Each night is one continuous line through its 3 stations.
"""
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# LensHRV web theme (dark navy) so the figure matches the site.
BG = "#0e1321"      # navy-bg-primary
FG = "#f2f4f7"      # navy-text-primary
MUTED = "#a0aec0"   # navy-text-secondary
CYAN = "#00e5ff"    # primary-cyan
ORANGE = "#ff9f43"
RED = "#f87171"     # alert-soft-red
GREEN = "#4ade80"
GRID = "#232c45"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": BG,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": FG,
    "text.color": FG,
    "xtick.color": FG,
    "ytick.color": FG,
    "grid.color": GRID,
})

BASE = Path(__file__).parent
HRV_CSV = BASE / "hrv_metrics_tagged.csv"
OUT_PNG = BASE / "fig1_smoking_night_curve.png"

# Explicit triplets (measurement timestamps, CDMX). Values are read from CSV,
# never hardcoded, so the figure always reflects the data.
NIGHTS = {
    "Oct 5 night": ("Oct 5 night", CYAN, ["2026-10-05 20:09", "2026-10-05 22:06", "2026-10-06 00:53"]),
    "Oct 7 night": ("Oct 7 night", ORANGE, ["2026-10-07 19:39", "2026-10-07 22:55", "2026-10-08 00:01"]),
    "Oct 8 night": ("Oct 8 night", GREEN, ["2026-10-08 19:40", "2026-10-08 21:43", "2026-10-08 23:46"]),
}
STAGES = [
    "Clean rest\n(~8pm)",
    "Nicotine + snack\n(~10pm)",
    "In bed after dinner\n(~midnight)",
]
STAGE_COLORS = [CYAN, ORANGE, RED]  # one color per station, shared by all nights
X = [0, 1, 2]


def _dark_legend(ax):
    """Paint the legend for the dark theme."""
    leg = ax.get_legend()
    if leg is not None:
        leg.get_frame().set_facecolor(BG)
        leg.get_frame().set_edgecolor(MUTED)
        for t in leg.get_texts():
            t.set_color(FG)


def main() -> None:
    df = pd.read_csv(HRV_CSV, parse_dates=["datetime_cdmx"]).set_index("datetime_cdmx")

    fig, ax = plt.subplots(figsize=(10, 6))
    for _, (label, color, dts) in NIGHTS.items():
        # Pull stressIndex for the 3 stations of this night.
        vals = [df.loc[pd.Timestamp(d), "stressIndex"] for d in dts]
        # Continuous line = the full movie of the night (not just 2 dots).
        ax.plot(X, vals, marker="o", linewidth=2, color=color, label=label)
        # Overpaint each station dot with its stage color.
        for x, v, c in zip(X, vals, STAGE_COLORS):
            ax.scatter([x], [v], color=c, s=80, zorder=3)
        print(f"{label}: " + " -> ".join(f"{d} stress={v:.1f}" for d, v in zip(dts, vals)))

    ax.set_xticks(X)
    ax.set_xticklabels(STAGES)
    ax.set_ylabel("stressIndex")
    ax.set_title("Night curve: rest -> nicotine + snack -> in bed (stressIndex)")
    ax.legend()
    ax.grid(True, alpha=0.5)
    _dark_legend(ax)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=150, facecolor=BG)
    print(f"OK: 3 nights x 3 stations -> {OUT_PNG.name}")


if __name__ == "__main__":
    main()
