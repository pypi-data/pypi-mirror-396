#SalsTools

'''
SalsTools: Utilities for data analytics and visualization

This package provides:
- `sample_df()` – quick sample dataframe for tests/demos
- `add_pct(df, col)` – add a percent-of-total column
- `assigned_completed_bar(...)` – completion ratio bar chart with labels
- `bar_graph(...)` – simple bar chart with optional percent labels

'''



from .main import sample_df,add_pct,assigned_completed_bar,bar_graph


__all__ = [
    "sample_df",
    "add_pct",
    "assigned_completed_bar",
    "bar_graph"]

