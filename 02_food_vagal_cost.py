"""Section 2 — A high-calorie, high-fat meal takes ~4 hours to digest.

Blog: "4 Findings from 4 Days of Tracking: An HRV Case Study"
Figure: fig2_food_vagal_cost.png (the "food image").
Data: food_meal_deltas.csv

Method:
  1. Join key: diet_compat.csv:datetime_cdmx matches hrv datetime_cdmx
     format (%Y-%m-%d %H:%M, 24h).
  2. For each meal, take the closest HRV measurement up to 2h BEFORE
     (pre) and up to 2h AFTER (post) via pandas.merge_asof (symmetric ±2h).
  3. delta_hf = post_hf - pre_hf  (vagal / rest mode)
     delta_lf = post_lf - pre_lf  (activation)
  4. Scatter deltas vs calories + linear regression on HF only.
     Body rule from the slope: every 100 kcal costs ~170 rest points
     (slope ~= -1.70). One noisy morning point (2026-10-07 08:30) is
     excluded from the plot/fit (kept in the CSV).
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# LensHRV web theme (dark navy) so the figure matches the site.
BG = "#0e1321"      # navy-bg-primary
FG = "#f2f4f7"      # navy-text-primary
MUTED = "#a0aec0"   # navy-text-secondary
CYAN = "#00e5ff"    # primary-cyan
ORANGE = "#ff9f43"
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
DIET_CSV = BASE / "diet_compat.csv"
HRV_CSV = BASE / "hrv_metrics_tagged.csv"
OUT_CSV = BASE / "food_meal_deltas.csv"
OUT_PNG = BASE / "fig2_food_vagal_cost.png"

FMT = "%Y-%m-%d %H:%M"
WINDOW = pd.Timedelta("2h")
EXCLUDE_FROM_PLOT = "2026-10-07 08:30"  # noisy morning outlier, out of scope


def compute_deltas() -> pd.DataFrame:
    """Return one row per meal with pre/post HF/LF and deltas."""
    diet = (
        pd.read_csv(DIET_CSV, parse_dates=["datetime_cdmx"])
        .sort_values("datetime_cdmx")
        .reset_index(drop=True)
    )
    hrv = (
        pd.read_csv(HRV_CSV, parse_dates=["datetime_cdmx"])
        .sort_values("datetime_cdmx")
        .reset_index(drop=True)
    )
    hrv_small = hrv[["datetime_cdmx", "hf", "lf"]]

    # Closest HRV at most 2h before (pre) and at most 2h after (post) each meal.
    # reset_index above matters: merge_asof results align positionally.
    pre = pd.merge_asof(
        diet,
        hrv_small.rename(columns={"datetime_cdmx": "pre_datetime"}),
        left_on="datetime_cdmx",
        right_on="pre_datetime",
        direction="backward",
        tolerance=WINDOW,
    )
    post = pd.merge_asof(
        diet,
        hrv_small.rename(columns={"datetime_cdmx": "post_datetime"}),
        left_on="datetime_cdmx",
        right_on="post_datetime",
        direction="forward",
        tolerance=WINDOW,
    )

    out = pd.DataFrame(
        {
            "diet_datetime": diet["datetime_cdmx"].dt.strftime(FMT),
            "pre_datetime": pre["pre_datetime"].dt.strftime(FMT).fillna(""),
            "post_datetime": post["post_datetime"].dt.strftime(FMT).fillna(""),
            "pre_hf": pre["hf"],
            "post_hf": post["hf"],
            "delta_hf": (post["hf"] - pre["hf"]).round(2),
            "pre_lf": pre["lf"],
            "post_lf": post["lf"],
            "delta_lf": (post["lf"] - pre["lf"]).round(2),
            "calories_kcal": diet["calories_kcal"],
            "text_en": diet["text_en"],
        }
    )
    return out


def plot_deltas(df: pd.DataFrame) -> float:
    """Scatter deltas vs calories with HF regression. Returns the slope."""
    plot_df = df.dropna(subset=["delta_hf", "delta_lf"])
    plot_df = plot_df[plot_df["diet_datetime"] != EXCLUDE_FROM_PLOT]

    # Linear fit on HF only (cyan/vagal points).
    x = plot_df["calories_kcal"].to_numpy()
    y = plot_df["delta_hf"].to_numpy()
    slope, intercept = np.polyfit(x, y, 1)
    xs = np.array([x.min(), x.max()])
    ys = slope * xs + intercept

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axhline(0, color=MUTED, linewidth=1)
    ax.scatter(plot_df["calories_kcal"], plot_df["delta_hf"], label="delta_hf (vagal)", color=CYAN, alpha=0.85)
    ax.scatter(plot_df["calories_kcal"], plot_df["delta_lf"], label="delta_lf (activation)", color=ORANGE, alpha=0.85)
    ax.plot(xs, ys, color=CYAN, linewidth=2, linestyle="--", label=f"HF trend (slope={slope:.2f})")

    # Label only the extremes so the chart stays readable.
    for col in ["delta_hf", "delta_lf"]:
        for _, r in plot_df.nlargest(2, col).iterrows():
            ax.annotate(r["diet_datetime"][5:], (r["calories_kcal"], r[col]),
                        fontsize=8, color=MUTED, xytext=(4, 4), textcoords="offset points")
        for _, r in plot_df.nsmallest(1, col).iterrows():
            ax.annotate(r["diet_datetime"][5:], (r["calories_kcal"], r[col]),
                        fontsize=8, color=MUTED, xytext=(4, -10), textcoords="offset points")

    ax.set_xlabel("calories_kcal per meal")
    ax.set_ylabel("delta post-pre (±2h)")
    ax.set_title("Delta HF/LF (±2h) vs calories per meal")
    ax.legend()
    ax.grid(True, alpha=0.5)
    leg = ax.get_legend()
    leg.get_frame().set_facecolor(BG)
    leg.get_frame().set_edgecolor(MUTED)
    for t in leg.get_texts():
        t.set_color(FG)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=150, facecolor=BG)
    print(f"OK: {len(plot_df)} points -> {OUT_PNG.name} (slope={slope:.2f})")
    return slope


def main() -> None:
    out = compute_deltas()
    out.to_csv(OUT_CSV, index=False)
    ok = out["delta_hf"].notna().sum()
    print(f"OK: {len(out)} meals -> {OUT_CSV.name} | with pre+post: {ok}")
    for _, r in out.iterrows():
        dhf = "" if pd.isna(r["delta_hf"]) else r["delta_hf"]
        dlf = "" if pd.isna(r["delta_lf"]) else r["delta_lf"]
        print(f"{r['diet_datetime']} | pre={r['pre_datetime'] or '-'} "
              f"post={r['post_datetime'] or '-'} | dHF={dhf} dLF={dlf} | {r['calories_kcal']}kcal")
    plot_deltas(out)


if __name__ == "__main__":
    main()
