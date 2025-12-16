
# salstools/main.py

from __future__ import annotations
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Iterable, Optional, Dict, Tuple


def sample_df():  # Use for tests
    '''

    Create a small sample dataframe for testing and demos.

    Returns
    -------
    pandas.DataFrame
        Columns: `Name` (str), `Completed` (int), `Assigned` (int), `Pct` (float)

    '''

    
    datadict = {
        "Name": ["Alpha", "Bravo", "Charlie"],
        "Completed": [45, 42, 37],
        "Assigned": [48, 50, 39],
    }
    df = pd.DataFrame(datadict)
    df["Pct"] = round(df["Completed"] / df["Assigned"] * 100, 2)
    return df

def add_pct(df, col):
    """
    Creates a Pct column based on a count column. Rounded to two decimals.
    """
    a = df.copy()
    a["Pct"] = round(a[col] / a[col].sum() * 100, 2)
    return a


def assigned_completed_bar(
    df: pd.DataFrame,
    index_col: str,
    completed_col: str,
    assigned_col: str,
    pct_col: str,
) -> tuple[plt.Figure, plt.Axes]:
    """
    Plot a completion chart with labels: `completed/assigned - (pct%)`.

    Requires a dataframe with `index_col`, `completed_col`, `assigned_col`, `pct_col`.

    Parameters
    ----------
    df : pandas.DataFrame
        Prepared dataframe.
    index_col : str
        Column with category labels (x axis).
    completed_col : str
        Column with completed counts.
    assigned_col : str
        Column with assigned counts.
    pct_col : str
        Column with percentage values (per row).

    Returns
    -------
    (fig, ax) : tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]
        Matplotlib figure and axes for further customization.
    """
    a = df.copy()

    # Compute totals and chart title
    completed_total = pd.to_numeric(a[completed_col], errors="coerce").fillna(0).sum()
    assigned_total = pd.to_numeric(a[assigned_col], errors="coerce").fillna(0).sum()
    pct_total = round(completed_total / assigned_total * 100, 2) if assigned_total else 0.0
    chart_title = f"Pct Completion by {index_col}: {completed_total}/{assigned_total} - ({pct_total}%)"

    # If pct_col is numeric, round and stringify; otherwise stringify directly
    pct_series = pd.to_numeric(a[pct_col], errors="ignore")
    if pd.api.types.is_numeric_dtype(pct_series):
        pct_vals = pct_series.round(1).astype(str)
    else:
        pct_vals = a[pct_col].astype(str)

    a["Labels"] = (
        pd.to_numeric(a[completed_col], errors="coerce").fillna(0).astype(int).astype(str)
        + "/"
        + pd.to_numeric(a[assigned_col], errors="coerce").fillna(0).astype(int).astype(str)
        + " - ("
        + pct_vals
        + "%)"
    )

    # Figure size scales with number of categories
    fig_width = max(6.0, len(a[index_col]) * 2.25)
    fig, ax = plt.subplots(figsize=(fig_width, 6))

    # Background normalization bars (100%)
    ax.bar(a[index_col], [100] * len(a), width=1.0, alpha=0.4, color="midnightblue")

    # Foreground bars (assigned)
    bars = ax.bar(a[index_col], pd.to_numeric(a[assigned_col], errors="coerce").fillna(0), width=0.4, color="steelblue")

    # Title & axes styling and bar labels
    ax.set_title(chart_title)
    ax.set_ylim(0, 120)
    ax.set_yticks([])
    ax.bar_label(bars, labels=a["Labels"], padding=3, fontsize=9)

    return fig, ax


def bar_graph(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    pct: bool = False,
    title: str | None = None,
) -> tuple[plt.Figure, plt.Axes]:
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
        a["Labels"] = a[y_col].astype(int).astype(str)

    # Figure sizing based on number of categories
    fig_width = max(6.0, len(a[x_col]) * 2.25)
    fig, ax = plt.subplots(figsize=(fig_width, 6))

    # Single bar plot
    bars = ax.bar(a[x_col], a[y_col], width=0.4, color="steelblue")

    # Axis styling
    ymax = (a[y_col].max() or 0) * 1.35 if len(a) else 1
    ax.set_ylim(0, max(ymax, 1))
    ax.set_yticks([])
    ax.set_title(title or f"Count by {x_col}")

    # Labels
    ax.bar_label(bars, labels=a["Labels"], padding=3, fontsize=12)

    return fig, ax
