
# SalsTools
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
    df,
    index_col,
    completed_col=None,
    assigned_col=None,
    category_cols=None,
    *,
    normalize=True,
    title="",
    color_map=None,
    font_family="Xfinity Brown",
    font_size=14,
    font_weight="bold",
    dark_background=True,
    figsize_scale=2.45,
    min_figsize=(6, 4),
    show=True,
):
    """
    Smart 100%-style chart.
    Two modes, chosen based on arguments:
    1) Completion mode (like bar_chart_100_2d):
       - Provide completed_col AND assigned_col.
       - Shows each index as X of Y, with label "XX% (X/Y)" over a 100% bar.
    2) Stacked distribution mode (like stacked_ratings_100):
       - Provide category_cols (list of columns with counts).
       - If normalize=True (default), converts each row to percentages
         that sum to ~100 and stacks them in a single bar per index.
    Parameters
    ----------
    df : DataFrame
        Source data.
    index_col : str
        Column to use on the x-axis for categories (e.g., manager name).
    completed_col : str or None
        For completion mode: column with completed counts.
    assigned_col : str or None
        For completion mode: column with assigned counts.
    category_cols : list of str or None
        For stacked distribution mode: columns containing counts per category.
    normalize : bool
        Only relevant in stacked mode. If True, convert to % of row.
    title : str
        Chart title.
    color_map : dict or None
        For stacked mode: category -> color. If None, sensible defaults.
    font_family, font_size, font_weight, dark_background, figsize_scale,
    min_figsize, show : styling & control options.
    Returns
    -------
    ax : matplotlib.axes.Axes
    """
    data = df.copy()
    # Determine mode
    has_completion = completed_col is not None and assigned_col is not None
    has_categories = category_cols is not None and len(category_cols) > 0
    if has_completion and has_categories:
        raise ValueError("Provide either completed/assigned OR category_cols, not both.")
    if not has_completion and not has_categories:
        raise ValueError("Must provide completed/assigned OR category_cols.")
    # Style
    if dark_background:
        plt.style.use("dark_background")
    if font_family is not None:
        plt.rcParams["font.family"] = font_family
        plt.rcParams["font.size"] = font_size
        plt.rcParams["font.weight"] = font_weight
    # Common x-axis setup
    categories = data[index_col].astype(str)
    n_items = len(categories)
    width = max(min_figsize[0], n_items * figsize_scale)
    height = min_figsize[1]
    fig, ax = plt.subplots(figsize=(width, height))
    # ------------------------------------------------------------------
    # MODE 1: Completion chart (X of Y, percent out of 100)
    # ------------------------------------------------------------------
    if has_completion:
        # Compute percent if needed
        pct = (data[completed_col] / data[assigned_col].replace(0, np.nan)) * 100
        data["Pct"] = pct.round(2).fillna(0)
        # Background "100%" bars
        ax.bar(categories, 100, color="#00AAFF", width=0.7, alpha=0.5)
        # Foreground completion bars
        bars = ax.bar(categories, data["Pct"], width=0.4, color="#FFFFFF")
        # Labels: "XX%\n(X/Y)", gold if 100%
        for rect, p, c, a_val in zip(
            bars, data["Pct"], data[completed_col], data[assigned_col]
        ):
            height = rect.get_height()
            label_color = "#FFD700" if np.isclose(p, 100) else "#FFFFFF"
            label = f"{p:.0f}%\n({int(c)}/{int(a_val)})"
            ax.text(
                rect.get_x() + rect.get_width() / 2.0,
                height,
                label,
                ha="center",
                va="bottom",
                color=label_color,
            )
        ax.set_ylim(0, 120)  # 100% + headroom for labels
        ax.set_title(title)
        # Hide y-axis to match your style
        ax.set_yticks([])
        ax.yaxis.set_visible(False)
        plt.tight_layout()
        if show:
            plt.show()
        return ax
    # ------------------------------------------------------------------
    # MODE 2: Stacked distribution chart (e.g., Off/Eff/Out)
    # ------------------------------------------------------------------
    # Ensure columns present & in desired order
    data = data.set_index(index_col)
    data = data[category_cols]
    # Compute percent or keep counts
    if normalize:
        row_sums = data.sum(axis=1).replace(0, np.nan)
        plot_data = data.div(row_sums, axis=0) * 100
        y_max = 100
    else:
        plot_data = data
        y_max = plot_data.sum(axis=1).max()
    managers = plot_data.index.astype(str)
    # Default color map
    #No Rating Entered = #6B7280
    if color_map is None:
        default_colors = {
            "Off Track": "#5A2389",     # purple
            "Effective": "#008557",     # green
            "Outstanding": "#1F69FF",   # blue
        }
        color_map = {col: default_colors.get(col, "#6B7280") for col in category_cols}
    bottoms = np.zeros(len(plot_data))
    for col in category_cols:
        values = plot_data[col].values
        bars = ax.bar(managers, values, bottom=bottoms, label=col, color=color_map[col])
        bottoms += values
        # Label segments that are visually meaningful
        for i, (rect, val) in enumerate(zip(bars, values)):
            if normalize:
                if val <= 5:  # avoid clutter on tiny slices
                    continue
                row_total = row_sums.iloc[i]
                pct_val = (val / row_total) * 100 if row_total else 0
                text = f"{int(val)} / {int(row_total)}  ({pct_val:.2f}%)"
            else:
                if val <= 0:
                    continue
                text = f"{int(val)}"
            ax.text(
                rect.get_x() + rect.get_width() / 2.0,
                rect.get_y() + rect.get_height() / 2.0,
                text,
                ha="center",
                va="center",
            )
            # Match your visual style: hide y-axis
            ax.set_yticks([])
            ax.yaxis.set_visible(False)
            plt.tight_layout()
            if show:
                plt.show()
            return ax