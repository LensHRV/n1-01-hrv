"""Section 4 — Extra recovery rebound post-workout (HF only).

Blog: "4 Findings from 4 Days of Tracking: An HRV Case Study"
Figure: fig3_gym_rebound.png (the "gym.png image").

Method (curve model, HF overlapped by stage — not by clock time):
  - Pre gym: last calm reading before training.
  - Post gym: first reading after training (the floor, lowest of all data).
  - Recovery / Recovery +1: next readings until before the ~3pm meal.
HF = vagal/recovery signal (higher = more recovery). All 3 gym days
(Oct 5 / Oct 7 / Oct 8; Oct 6 was rest) start at x=0 so the V shape
(crash -> parasympathetic rebound) is directly comparable.
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
OUT_PNG = BASE / "fig3_gym_rebound.png"

# (line color, measurement timestamps). Values come from CSV at runtime.
SESSIONS = {
    "Oct5 gym": (CYAN, ["2026-10-05 10:12", "2026-10-05 11:45", "2026-10-05 13:50"]),
    "Oct7 gym": (ORANGE, ["2026-10-07 09:45", "2026-10-07 11:44", "2026-10-07 14:42"]),
    "Oct8 gym": (GREEN, ["2026-10-08 09:42", "2026-10-08 11:56",
                          "2026-10-08 13:20", "2026-10-08 14:44"]),
}
STAGE_LABELS = ["Pre gym", "Post gym", "Recovery", "Recovery +1"]


def main() -> None:
    df = pd.read_csv(HRV_CSV, parse_dates=["datetime_cdmx"]).set_index("datetime_cdmx")

    fig, ax = plt.subplots(figsize=(9, 6))
    for name, (color, dts) in SESSIONS.items():
        ts = [pd.Timestamp(d) for d in dts]
        hf = [df.loc[t, "hf"] for t in ts]
        # Overlap by stage (0..n), not by clock — sessions share the same x.
        x = list(range(len(hf)))
        ax.plot(x, hf, marker="o", linewidth=2, color=color, label=f"{name} HF")
        print(f"{name}: HF={' -> '.join(f'{v:.0f}' for v in hf)}")

    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(STAGE_LABELS)
    ax.set_ylabel("hf")
    ax.set_title("Gym CURVE: HF overlapped by stage (pre -> post -> recovery)")
    ax.legend()
    ax.grid(True, alpha=0.5)
    leg = ax.get_legend()
    leg.get_frame().set_facecolor(BG)
    leg.get_frame().set_edgecolor(MUTED)
    for t in leg.get_texts():
        t.set_color(FG)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=150, facecolor=BG)
    print(f"OK -> {OUT_PNG.name}")


if __name__ == "__main__":
    main()
