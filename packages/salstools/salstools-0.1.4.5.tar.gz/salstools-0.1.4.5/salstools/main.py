
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

def assigned_completed_bar(df, index_col, completed_col, assigned_col, pct_col):
    """
    Requires a prepared dataframe that has the following columns

    :param df: DataFrame
    :param index_col: Index Column
    :param completed_col: Completed Column
    :param assigned_col: Assigned Column
    :param pct_col: Percentage Column
    """
    a = df.copy()

    # Compute totals and chart title
    completed_total = a[completed_col].sum()
    assigned_total = a[assigned_col].sum()
    pct_total = round(completed_total / assigned_total * 100, 2) if assigned_total else 0.0
    chart_title = f"Pct Completion by {index_col}: {completed_total}/{assigned_total} - ({pct_total}%)"

    # If pct_col is already numeric, round it; if it's a string, just use it
    if hasattr(a[pct_col], "round"):
        pct_vals = a[pct_col].round(1).astype(str)
    else:
        pct_vals = a[pct_col].astype(str)

    a["Labels"] = (
        a[completed_col].astype(int).astype(str) + "/" +
        a[assigned_col].astype(int).astype(str) + " - (" +
        pct_vals + "%)"
    )

    # Make the figure a bit wider for many categories
    fig_width = max(6, len(a[index_col]) * 2.25)
    fig, ax = plt.subplots(figsize=(fig_width, 6))

    # Background normalization bars (100%)
    ax.bar(a[index_col], [100] * len(a), width=1.0, alpha=.4, color="midnightblue")

    # Foreground bars: using 'assigned' as in your original (you can switch to 'completed' if desired)
    bars = ax.bar(a[index_col], a[assigned_col], width=.4, color="steelblue")

    # Title & axes styling and bar labels
    ax.set_title(chart_title)
    ax.set_ylim(0, 120)
    ax.set_yticks([])
    ax.bar_label(bars, labels=a["Labels"], padding=3, fontsize=9)

    return fig, ax

def bar_graph(df, x_col, y_col, pct: bool = False, title: str | None = None):
    """
    Bar chart with optional percentage labels.

    Parameters
    ----------
    df : pandas.DataFrame
        Source data.
    x_col : str
        Column to use for x (categories).
    y_col : str
        Column to use for bar heights (numeric).
    pct : bool, default False
        If True, append percent of total for each bar to the label.
    title : str | None
        Optional custom title; if None, uses 'Count by {x_col}'.

    Returns
    -------
    (fig, ax)
        Matplotlib figure and axes.
    """
    # Work on a copy to avoid mutating the input df
    a = df.copy()

    # Ensure y_col is numeric
    a[y_col] = pd.to_numeric(a[y_col], errors="coerce").fillna(0)

    # Compute total for percent labels
    total = a[y_col].sum()
    
    # Build labels per row
    if pct and total > 0:
        pct_vals = (a[y_col] / total * 100).round(2).astype(str)
        a["Labels"] = a[y_col].astype(int).astype(str) + " - (" + pct_vals + "%)"
    else:
        # Just the numeric value as label
        a["Labels"] = a[y_col].astype(int).astype(str)

    # Figure sizing based on number of categories
    fig_width = max(6, len(a[x_col]) * 2.25)
    fig, ax = plt.subplots(figsize=(fig_width, 6))

    # Single bar plot
    bars = ax.bar(a[x_col], a[y_col], width=.4, color="steelblue")

    # Axis styling
    ymax = (a[y_col].max() or 0) * 1.35 if len(a) else 1
    ax.set_ylim(0, max(ymax, 1))  # keep >0
    ax.set_yticks([])
    ax.set_title(title or f"Count by {x_col}")

    # Labels
    ax.bar_label(bars, labels=a["Labels"], padding=3, fontsize=12)

    return fig, ax
