
# SalsTools
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Iterable, Optional, Dict, Tuple
# ---------------------------------------------------------------------
# Simple test data
# ---------------------------------------------------------------------
def sample_df():  # Use for tests
    datadict = {
        "Name": ["Alpha", "Bravo", "Charlie"],
        "Completed": [45, 42, 37],
        "Assigned": [48, 50, 39],
    }
    df = pd.DataFrame(datadict)
    df["Pct"] = round(df["Completed"] / df["Assigned"] * 100, 2)
    return df
# ---------------------------------------------------------------------
# Helper: add_pct (unchanged)
# ---------------------------------------------------------------------
def add_pct(df, col):
    """
    Creates a Pct column based on a count column. Rounded to two decimals.
    """
    a = df.copy()
    a["Pct"] = round(a[col] / a[col].sum() * 100, 2)
    return a
# ---------------------------------------------------------------------
# NEW CORE: smart 100%-style chart
# ---------------------------------------------------------------------

def smart_bar(
    df: pd.DataFrame,
    index_col: str,
    value_cols: Iterable[str],
    *,
    mode: str = "auto",          # "auto" | "simple" | "stacked" | "grouped"
    normalize: bool = False,      # True => convert rows to percentages (stacked only)
    palette: Optional[Dict[str, str]] = None,  # {column_name: "#RRGGBB"}
    theme: str = "dark",          # "dark" | "light"
    bar_width: float = 0.8,
    figsize_scale_x: float = 0.45,
    min_figsize: Tuple[float, float] = (7.0, 4.0),
    label_kind: str = "auto",     # "none" | "value" | "pct" | "both" | "auto"
    label_threshold_pct: float = 5.0,  # stacked mode: only label segments >= this %
    rotate_xticks: bool = False,
    tight_layout: bool = True,
    show: bool = True,
) -> plt.Axes:
    """
    Universal bar chart helper.

    Parameters
    ----------
    df : DataFrame
        Source data.
    index_col : str
        Column to use as categories on the x-axis.
    value_cols : Iterable[str]
        One or more columns to plot as bars.
    mode : str
        "simple" (single series), "stacked", "grouped", or "auto".
        "auto" => one column -> simple, multiple -> stacked.
    normalize : bool
        If True in stacked mode, each row is converted to percentages (0-100).
    palette : dict or None
        Mapping {column_name: color}. If None, a colorblind-friendly default is used.
    theme : str
        "dark" uses matplotlib's dark_background; "light" uses default.
    bar_width : float
        Bar width (grouped mode uses narrower bars automatically).
    figsize_scale_x : float
        Scales figure width by number of categories (n * scale), clamped by min_figsize.
    min_figsize : (width, height)
        Minimum figure size in inches.
    label_kind : str
        "none" | "value" | "pct" | "both" | "auto".
        - "auto": simple/grouped -> "value", stacked+normalize -> "pct", stacked+counts -> "value".
    label_threshold_pct : float
        In stacked mode, skip labels for segments smaller than this percentage.
    rotate_xticks : bool
        If True, rotate x tick labels by 45 degrees.
    tight_layout : bool
        If True, call plt.tight_layout() at the end.
    show : bool
        If True, plt.show() after drawing.

    Returns
    -------
    ax : matplotlib.axes.Axes
    """
    # ---- validation ----
    if index_col not in df.columns:
        raise KeyError(f"index_col '{index_col}' not found in df.columns")

    value_cols = list(value_cols)
    if len(value_cols) == 0:
        raise ValueError("Provide at least one value column in 'value_cols'.")
    for col in value_cols:
        if col not in df.columns:
            raise KeyError(f"value column '{col}' not found in df.columns")

    # ---- styling/theme ----
    if theme == "dark":
        plt.style.use("dark_background")
        fg_text = "#FFFFFF"
        zero_color = "#6B7280"  # neutral gray
    else:
        plt.style.use("default")
        fg_text = "#111111"
        zero_color = "#8E8E93"

    # Cross-platform default font (avoid platform-specific families)
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["font.size"] = 12
    plt.rcParams["font.weight"] = "bold"

    # ---- figure sizing ----
    categories = df[index_col].astype(str)
    n = len(categories)
    width = max(min_figsize[0], n * figsize_scale_x)
    height = min_figsize[1]
    fig, ax = plt.subplots(figsize=(width, height))

    # ---- default palette (colorblind-friendly) ----
    if palette is None:
        base_colors = [
            "#1F77B4",  # blue
            "#FF7F0E",  # orange
            "#2CA02C",  # green
            "#D62728",  # red
            "#9467BD",  # purple
            "#8C564B",  # brown
            "#E377C2",  # pink
            "#7F7F7F",  # gray
            "#BCBD22",  # olive
            "#17BECF",  # teal
        ]
        palette = {col: base_colors[i % len(base_colors)] for i, col in enumerate(value_cols)}

    # ---- decide mode ----
    if mode == "auto":
        mode = "simple" if len(value_cols) == 1 else "stacked"

    # ---- plot modes ----
    if mode == "simple":
        series = df[value_cols[0]].fillna(0)
        colors = [palette[value_cols[0]] if v != 0 else zero_color for v in series]
        bars = ax.bar(categories, series, color=colors, width=bar_width)

        # labels (conditional coloring)
        lk = "value" if label_kind == "auto" else label_kind
        if lk != "none":
            max_val = float(series.max()) if len(series) else 0.0
            for i, rect in enumerate(bars):
                v = float(series.iloc[i])
                lbl_color = "#FFD700" if (max_val > 0 and np.isclose(v, max_val)) else fg_text
                if lk == "value":
                    text = f"{int(v):,}" if float(v).is_integer() else f"{v:.2f}"
                elif lk == "pct":
                    # For simple mode, pct relative to max (not typical) -> skip unless requested
                    text = f"{(v / max_val * 100):.0f}%" if max_val > 0 else "0%"
                else:  # "both"
                    text = f"{int(v):,}" if float(v).is_integer() else f"{v:.2f}"
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    rect.get_height(),
                    text,
                    ha="center",
                    va="bottom",
                    color=lbl_color,
                )

    elif mode == "grouped":
        # side-by-side bars for each column
        m = len(value_cols)
        x = np.arange(n)
        group_width = bar_width
        single_w = group_width / (m + 0.15)
        for j, col in enumerate(value_cols):
            y = df[col].fillna(0).values
            xj = x + (j - (m-1)/2) * single_w
            colors = [palette[col] if v != 0 else zero_color for v in y]
            bars = ax.bar(xj, y, width=single_w, label=col, color=colors)
            # labels
            lk = "value" if label_kind == "auto" else label_kind
            if lk != "none":
                max_val = float(np.max(y)) if len(y) else 0.0
                for i, rect in enumerate(bars):
                    v = float(y[i])
                    lbl_color = "#FFD700" if (max_val > 0 and np.isclose(v, max_val)) else fg_text
                    text = f"{int(v):,}" if float(v).is_integer() else f"{v:.2f}"
                    ax.text(
                        rect.get_x() + rect.get_width() / 2,
                        rect.get_height(),
                        text if lk in ("value", "both") else "",
                        ha="center",
                        va="bottom",
                        color=lbl_color,
                    )
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend(loc="best", frameon=False)

    elif mode == "stacked":
        # stacked bars, optionally normalized to percentages
        data = df[value_cols].fillna(0).copy()
        if normalize:
            row_totals = data.sum(axis=1).replace(0, np.nan)
            plot = data.div(row_totals, axis=0) * 100.0
            y_max = 100
            lk = "pct" if label_kind == "auto" else label_kind
        else:
            plot = data
            y_max = float(plot.sum(axis=1).max())
            lk = "value" if label_kind == "auto" else label_kind

        bottoms = np.zeros(n)
        for col in value_cols:
            vals = plot[col].values
            bars = ax.bar(categories, vals, bottom=bottoms, label=col, color=palette[col], width=bar_width)
            # labels per segment
            if lk != "none":
                for i, rect in enumerate(bars):
                    val = float(vals[i])
                    if normalize and val < label_threshold_pct:
                        continue  # skip tiny slices
                    lbl_color = "#FFD700" if (normalize and np.isclose(val, 100)) else fg_text
                    if normalize:
                        # Compose "count (pct%)" if original totals exist
                        total = float(df[value_cols].iloc[i].sum())
                        count = float(df[col].iloc[i])
                        if lk == "pct":
                            text = f"{val:.0f}%"
                        elif lk == "both":
                            text = f"{int(count):,} ({val:.0f}%)"
                        else:  # "value"
                            text = f"{int(count):,}"
                    else:
                        text = f"{int(val):,}" if float(val).is_integer() else f"{val:.2f}"

                    ax.text(
                        rect.get_x() + rect.get_width() / 2,
                        rect.get_y() + rect.get_height() / 2,
                        text,
                        ha="center",
                        va="center",
                        color=lbl_color,
                    )
            bottoms += vals

        ax.set_ylim(0, y_max * 1.05)
        ax.legend(loc="best", frameon=False)

    else:
        raise ValueError("mode must be one of: 'auto', 'simple', 'stacked', 'grouped'")

    # ---- common axes polish ----
    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.set_title("")
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_yticks([])  # your preferred clean style

    if rotate_xticks:
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
            tick.set_ha("right")

    if tight_layout:
        plt.tight_layout()
    if show:
        plt.show()
    return ax
